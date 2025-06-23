from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .supabase_client import SupabaseService
from .tasks import process_chat_message
from .chat_service import ChatService
from celery.result import AsyncResult
import json

@api_view(['GET'])
def test_api(request):
    """Test endpoint to check if Django API is working"""
    return Response({
        'message': 'Django API is working!',
        'status': 'success'
    })

# Create your views here.

# Authentication endpoints
@api_view(['POST'])
@csrf_exempt
def login_view(request):
    """User login with email and password"""
    try:
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            return Response(
                {'error': 'Email and password are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get user from Supabase
        user_data = SupabaseService.get_user_by_email(email)
        if not user_data:
            return Response(
                {'error': 'Invalid credentials'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Check password
        if check_password(password, user_data['password_hash']):
            # Store user info in session
            request.session['user_id'] = user_data['id']
            request.session['user_email'] = user_data['email']
            request.session['is_admin'] = user_data.get('is_admin', False)
            
            # Debug: Log session creation
            print(f"✅ Login successful for {email}")
            print(f"Session ID: {request.session.session_key}")
            print(f"User ID stored in session: {request.session['user_id']}")
            
            return Response({
                'success': True,
                'user': {
                    'id': user_data['id'],
                    'email': user_data['email'],
                    'first_name': user_data.get('first_name', ''),
                    'last_name': user_data.get('last_name', ''),
                    'is_admin': user_data.get('is_admin', False)
                }
            })
        else:
            return Response(
                {'error': 'Invalid credentials'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
            
    except Exception as e:
        return Response(
            {'error': 'Login failed', 'details': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
def logout_view(request):
    """User logout"""
    try:
        request.session.flush()
        return Response({'success': True, 'message': 'Logged out successfully'})
    except Exception as e:
        return Response(
            {'error': 'Logout failed', 'details': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def current_user(request):
    """Get current user info"""
    user_id = request.session.get('user_id')
    if not user_id:
        return Response(
            {'error': 'Not authenticated'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    try:
        user_data = SupabaseService.get_user_by_id(user_id)
        if user_data:
            return Response({
                'user': {
                    'id': user_data['id'],
                    'email': user_data['email'],
                    'first_name': user_data.get('first_name', ''),
                    'last_name': user_data.get('last_name', ''),
                    'is_admin': user_data.get('is_admin', False)
                }
            })
        else:
            return Response(
                {'error': 'User not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    except Exception as e:
        return Response(
            {'error': 'Failed to get user info', 'details': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

def require_authentication(view_func):
    """Decorator to require authentication for views"""
    def wrapper(request, *args, **kwargs):
        user_id = request.session.get('user_id')
        
        # Debug: Log session checking
        print(f"🔍 Checking auth for {request.path}")
        print(f"Session key: {request.session.session_key}")
        print(f"User ID in session: {user_id}")
        print(f"Session data: {dict(request.session)}")
        
        if not user_id:
            print("❌ No user_id in session - returning 401")
            return Response(
                {'error': 'Authentication required'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        print(f"✅ User authenticated: {user_id}")
        return view_func(request, *args, **kwargs)
    return wrapper

@api_view(['GET', 'POST'])
@require_authentication
def leads_list(request):
    """
    List all leads or create a new lead (user-specific)
    GET: Returns all leads grouped by status for Kanban board
    POST: Creates a new lead
    """
    user_id = request.session.get('user_id')
    
    if request.method == 'GET':
        leads = SupabaseService.get_all_leads(user_id=user_id)
        
        # Group leads by status for Kanban board
        kanban_data = {
            'Interest': [],
            'Meeting booked': [],
            'Proposal sent': [],
            'Closed win': [],
            'Closed lost': []
        }
        
        for lead in leads:
            status_key = lead.get('status', 'Interest')
            if status_key in kanban_data:
                kanban_data[status_key].append(lead)
        
        return Response(kanban_data)
    
    elif request.method == 'POST':
        lead_data = request.data
        
        # Set default values if not provided
        if 'status' not in lead_data:
            lead_data['status'] = 'Interest'
        
        # Set card order to be last in the column
        leads = SupabaseService.get_all_leads(user_id=user_id)
        same_status_leads = [l for l in leads if l.get('status') == lead_data['status']]
        lead_data['card_order'] = len(same_status_leads) + 1
        
        new_lead = SupabaseService.create_lead(lead_data, user_id=user_id)
        
        if new_lead:
            return Response(new_lead, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {'error': 'Failed to create lead'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

@api_view(['GET', 'PUT', 'DELETE'])
@require_authentication
def lead_detail(request, lead_id):
    """
    Retrieve, update or delete a specific lead (user-specific)
    """
    user_id = request.session.get('user_id')
    
    if request.method == 'GET':
        lead = SupabaseService.get_lead_by_id(lead_id, user_id=user_id)
        if lead:
            return Response(lead)
        return Response(
            {'error': 'Lead not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    elif request.method == 'PUT':
        lead_data = request.data
        updated_lead = SupabaseService.update_lead(lead_id, lead_data, user_id=user_id)
        
        if updated_lead:
            return Response(updated_lead)
        return Response(
            {'error': 'Failed to update lead'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    elif request.method == 'DELETE':
        success = SupabaseService.delete_lead(lead_id, user_id=user_id)
        if success:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'error': 'Failed to delete lead'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['PUT'])
@require_authentication
def update_lead_status(request, lead_id):
    """
    Update lead status (for moving cards between Kanban columns) - user-specific
    """
    user_id = request.session.get('user_id')
    new_status = request.data.get('status')
    new_order = request.data.get('card_order', 1)
    
    if not new_status:
        return Response(
            {'error': 'Status is required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Update the lead with new status and order
    lead_data = {
        'status': new_status,
        'card_order': new_order
    }
    
    updated_lead = SupabaseService.update_lead(lead_id, lead_data, user_id=user_id)
    
    if updated_lead:
        return Response(updated_lead)
    return Response(
        {'error': 'Failed to update lead status'}, 
        status=status.HTTP_400_BAD_REQUEST
    )

# Conversation endpoints
@api_view(['GET'])
@require_authentication
def conversations_list(request):
    """Get all conversations for the current user"""
    user_id = request.session.get('user_id')
    
    try:
        conversations = SupabaseService.get_user_conversations(user_id)
        return Response(conversations)
    except Exception as e:
        return Response(
            {'error': 'Failed to fetch conversations', 'details': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@require_authentication
def create_conversation(request):
    """Create a new conversation"""
    user_id = request.session.get('user_id')
    title = request.data.get('title', 'New Conversation')
    
    try:
        conversation = SupabaseService.create_conversation(user_id, title)
        if conversation:
            return Response(conversation, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {'error': 'Failed to create conversation'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    except Exception as e:
        return Response(
            {'error': 'Failed to create conversation', 'details': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET', 'PUT', 'DELETE'])
@require_authentication
def conversation_detail(request, conversation_id):
    """Get, update, or delete a specific conversation"""
    user_id = request.session.get('user_id')
    
    if request.method == 'GET':
        try:
            conversation = SupabaseService.get_conversation_by_id(conversation_id, user_id)
            if conversation:
                return Response(conversation)
            else:
                return Response(
                    {'error': 'Conversation not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
        except Exception as e:
            return Response(
                {'error': 'Failed to fetch conversation', 'details': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    elif request.method == 'PUT':
        try:
            conversation_data = request.data
            updated_conversation = SupabaseService.update_conversation(
                conversation_id, conversation_data, user_id
            )
            if updated_conversation:
                return Response(updated_conversation)
            else:
                return Response(
                    {'error': 'Failed to update conversation'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            return Response(
                {'error': 'Failed to update conversation', 'details': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    elif request.method == 'DELETE':
        try:
            success = SupabaseService.delete_conversation(conversation_id, user_id)
            if success:
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(
                    {'error': 'Failed to delete conversation'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            return Response(
                {'error': 'Failed to delete conversation', 'details': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

@api_view(['GET'])
@require_authentication
def conversation_messages(request, conversation_id):
    """Get all messages for a specific conversation"""
    user_id = request.session.get('user_id')
    
    try:
        # First verify user owns this conversation
        conversation = SupabaseService.get_conversation_by_id(conversation_id, user_id)
        if not conversation:
            return Response(
                {'error': 'Conversation not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        messages = SupabaseService.get_conversation_messages(conversation_id)
        return Response(messages)
    except Exception as e:
        return Response(
            {'error': 'Failed to fetch messages', 'details': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@require_authentication
def chat_message(request):
    """
    Initiate async chat message processing, returns task_id
    """
    user_id = request.session.get('user_id')
    
    try:
        message = request.data.get('message')
        conversation_id = request.data.get('conversation_id')
        
        if not message:
            return Response(
                {'error': 'Message is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # If no conversation_id provided, create a new conversation
        if not conversation_id:
            title = SupabaseService.generate_conversation_title(message)
            conversation = SupabaseService.create_conversation(user_id, title)
            if not conversation:
                return Response(
                    {'error': 'Failed to create conversation'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            conversation_id = conversation['id']
        else:
            # Verify user owns this conversation
            conversation = SupabaseService.get_conversation_by_id(conversation_id, user_id)
            if not conversation:
                return Response(
                    {'error': 'Conversation not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # If this is a "New Chat" conversation, update the title with the first message
            if conversation.get('title') == 'New Chat':
                new_title = SupabaseService.generate_conversation_title(message)
                SupabaseService.update_conversation(conversation_id, {'title': new_title}, user_id)
        
        # Save user message to database
        SupabaseService.create_message(conversation_id, message, is_user=True)
        
        # Get or create session
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key
        
        # Debug: Check Celery/Redis connection
        print(f"🔗 Attempting to start Celery task...")
        print(f"Redis URL: {getattr(settings, 'CELERY_BROKER_URL', 'Not configured')}")
        
        # Initiate async task with conversation_id and user_id
        task = process_chat_message.delay(message, session_key, conversation_id=conversation_id, user_id=user_id)
        print(f"✅ Celery task started: {task.id}")
        
        return Response({
            'task_id': task.id,
            'conversation_id': conversation_id,
            'status': 'processing',
            'message': 'Message received, processing...'
        })
        
    except Exception as e:
        return Response(
            {'error': 'Failed to process message', 'details': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@require_authentication
def chat_status(request, task_id):
    """
    Poll for task status and results
    """
    try:
        task_result = AsyncResult(task_id)
        
        if task_result.state == 'PENDING':
            response = {
                'state': task_result.state,
                'status': 'Task is waiting to be processed...'
            }
        elif task_result.state == 'PROCESSING':
            response = {
                'state': task_result.state,
                'status': task_result.info.get('status', 'Processing...')
            }
        elif task_result.state == 'SUCCESS':
            response = {
                'state': task_result.state,
                'result': task_result.result
            }
        elif task_result.state == 'FAILURE':
            response = {
                'state': task_result.state,
                'error': str(task_result.info),
                'status': 'Task failed'
            }
        else:
            response = {
                'state': task_result.state,
                'status': 'Unknown task state'
            }
        
        return Response(response)
        
    except Exception as e:
        return Response(
            {'error': 'Failed to get task status', 'details': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@require_authentication
def clear_chat(request):
    """
    Clear conversation context from session (legacy support)
    """
    try:
        # Get or create session
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key
        
        # Clear conversation context
        chat_service = ChatService()
        chat_service.clear_conversation_context(session_key)
        
        return Response({
            'status': 'success',
            'message': 'Conversation context cleared'
        })
        
    except Exception as e:
        return Response(
            {'error': 'Failed to clear conversation', 'details': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
