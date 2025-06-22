from celery import shared_task
from django.conf import settings
import openai
import json
from .supabase_client import SupabaseService
from .chat_service import ChatService

# Initialize OpenAI client
openai.api_key = settings.OPENAI_API_KEY

@shared_task(bind=True)
def process_chat_message(self, message, session_key, conversation_context=None):
    """
    Background task to process chat messages with OpenAI
    
    Args:
        message (str): User's chat message
        session_key (str): Django session key for context storage
        conversation_context (list): Previous conversation context
    
    Returns:
        dict: Response containing AI message and any lead operations performed
    """
    try:
        # Update task status
        self.update_state(state='PROCESSING', meta={'status': 'Processing your message...'})
        
        # Get current leads for context
        leads = SupabaseService.get_all_leads()
        
        # Initialize chat service
        chat_service = ChatService()
        
        # Process the message with OpenAI
        response = chat_service.process_message(message, session_key, leads)
        
        return response
        
    except Exception as exc:
        # Update task state with error
        self.update_state(
            state='FAILURE',
            meta={'error': str(exc), 'status': 'An error occurred while processing your message.'}
        )
        raise exc 