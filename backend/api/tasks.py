from celery import shared_task
from django.conf import settings
import openai
import json
from .supabase_client import SupabaseService
from .chat_service import ChatService

# Initialize OpenAI client
openai.api_key = settings.OPENAI_API_KEY

@shared_task(bind=True)
def process_chat_message(self, message, session_key, conversation_id=None, user_id=None):
    """
    Background task to process chat messages with OpenAI
    
    Args:
        message (str): User's chat message
        session_key (str): Django session key for context storage
        conversation_id (str): ID of the conversation for message persistence
        user_id (str): ID of the user for lead filtering
    
    Returns:
        dict: Response containing AI message and any lead operations performed
    """
    try:
        # Update task status
        self.update_state(state='PROCESSING', meta={'status': 'Processing your message...'})
        
        # Get current leads for context (filtered by user)
        leads = SupabaseService.get_all_leads(user_id=user_id)
        
        # Initialize chat service
        chat_service = ChatService()
        
        # Process the message with OpenAI
        response = chat_service.process_message(
            message, 
            session_key, 
            leads, 
            conversation_id=conversation_id, 
            user_id=user_id
        )
        
        return response
        
    except Exception as exc:
        # Update task state with error
        self.update_state(
            state='FAILURE',
            meta={'error': str(exc), 'status': 'An error occurred while processing your message.'}
        )
        raise exc 