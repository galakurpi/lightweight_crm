from django.shortcuts import render
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

@api_view(['GET', 'POST'])
def leads_list(request):
    """
    List all leads or create a new lead
    GET: Returns all leads grouped by status for Kanban board
    POST: Creates a new lead
    """
    if request.method == 'GET':
        leads = SupabaseService.get_all_leads()
        
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
        leads = SupabaseService.get_all_leads()
        same_status_leads = [l for l in leads if l.get('status') == lead_data['status']]
        lead_data['card_order'] = len(same_status_leads) + 1
        
        new_lead = SupabaseService.create_lead(lead_data)
        
        if new_lead:
            return Response(new_lead, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {'error': 'Failed to create lead'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

@api_view(['GET', 'PUT', 'DELETE'])
def lead_detail(request, lead_id):
    """
    Retrieve, update or delete a specific lead
    """
    if request.method == 'GET':
        lead = SupabaseService.get_lead_by_id(lead_id)
        if lead:
            return Response(lead)
        return Response(
            {'error': 'Lead not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    elif request.method == 'PUT':
        lead_data = request.data
        updated_lead = SupabaseService.update_lead(lead_id, lead_data)
        
        if updated_lead:
            return Response(updated_lead)
        return Response(
            {'error': 'Failed to update lead'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    elif request.method == 'DELETE':
        success = SupabaseService.delete_lead(lead_id)
        if success:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'error': 'Failed to delete lead'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['PUT'])
def update_lead_status(request, lead_id):
    """
    Update lead status (for moving cards between Kanban columns)
    """
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
    
    updated_lead = SupabaseService.update_lead(lead_id, lead_data)
    
    if updated_lead:
        return Response(updated_lead)
    return Response(
        {'error': 'Failed to update lead status'}, 
        status=status.HTTP_400_BAD_REQUEST
    )

@api_view(['POST'])
def chat_message(request):
    """
    Initiate async chat message processing, returns task_id
    """
    try:
        message = request.data.get('message')
        if not message:
            return Response(
                {'error': 'Message is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get or create session
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key
        
        # Initiate async task
        task = process_chat_message.delay(message, session_key)
        
        return Response({
            'task_id': task.id,
            'status': 'processing',
            'message': 'Message received, processing...'
        })
        
    except Exception as e:
        return Response(
            {'error': 'Failed to process message', 'details': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
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
def clear_chat(request):
    """
    Clear conversation context from session
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
