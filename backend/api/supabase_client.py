from django.conf import settings
import os

# Global variable to hold the client
supabase = None

def get_supabase_client():
    """Get Supabase client with lazy loading and error handling"""
    global supabase
    
    if supabase is not None:
        return supabase
    
    try:
        # Import here to avoid issues during Django startup
        from supabase import create_client, Client
        
        # Get credentials from settings
        url = getattr(settings, 'SUPABASE_URL', None)
        key = getattr(settings, 'SUPABASE_KEY', None)
        
        print(f"Attempting to connect to Supabase...")
        print(f"URL configured: {url is not None}")
        print(f"Key configured: {key is not None}")
        
        # Check if we have real credentials
        if not url or not key or url == 'https://placeholder.supabase.co' or key == 'placeholder-key':
            print("Warning: Supabase credentials not properly configured. Please check your .env file.")
            print("Make sure you have SUPABASE_URL and SUPABASE_KEY in your .env file.")
            supabase = None
            return None
            
        # Create client with minimal configuration
        supabase = create_client(url, key)
        print("✅ Supabase client created successfully!")
        return supabase
    except Exception as e:
        print(f"❌ Error creating Supabase client: {e}")
        print("Try installing: pip install httpx[http2]")
        supabase = None
        return None

class SupabaseService:
    """Service class to handle Supabase operations for leads, conversations, and messages"""
    
    # Lead operations with user filtering
    @staticmethod
    def get_all_leads(user_id=None):
        """Fetch all leads from Supabase, ordered by status and card_order, filtered by user"""
        client = get_supabase_client()
        if not client:
            print("Supabase client not available")
            return []
        try:
            query = client.table('leads').select('*').order('status').order('card_order')
            if user_id:
                query = query.eq('user_id', user_id)
            response = query.execute()
            return response.data
        except Exception as e:
            print(f"Error fetching leads: {e}")
            return []
    
    @staticmethod
    def create_lead(lead_data, user_id=None):
        """Create a new lead in Supabase"""
        client = get_supabase_client()
        if not client:
            print("Supabase client not available")
            return None
        try:
            if user_id:
                lead_data['user_id'] = user_id
            response = client.table('leads').insert(lead_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error creating lead: {e}")
            return None
    
    @staticmethod
    def update_lead(lead_id, lead_data, user_id=None):
        """Update an existing lead in Supabase"""
        client = get_supabase_client()
        if not client:
            print("Supabase client not available")
            return None
        try:
            query = client.table('leads').update(lead_data).eq('id', lead_id)
            if user_id:
                query = query.eq('user_id', user_id)
            response = query.execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error updating lead: {e}")
            return None
    
    @staticmethod
    def delete_lead(lead_id, user_id=None):
        """Delete a lead from Supabase"""
        client = get_supabase_client()
        if not client:
            print("Supabase client not available")
            return False
        try:
            query = client.table('leads').delete().eq('id', lead_id)
            if user_id:
                query = query.eq('user_id', user_id)
            response = query.execute()
            return True
        except Exception as e:
            print(f"Error deleting lead: {e}")
            return False
    
    @staticmethod
    def get_lead_by_id(lead_id, user_id=None):
        """Get a specific lead by ID"""
        client = get_supabase_client()
        if not client:
            print("Supabase client not available")
            return None
        try:
            query = client.table('leads').select('*').eq('id', lead_id)
            if user_id:
                query = query.eq('user_id', user_id)
            response = query.execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error fetching lead: {e}")
            return None
    
    # User operations
    @staticmethod
    def get_user_by_email(email):
        """Get user by email"""
        client = get_supabase_client()
        if not client:
            print("Supabase client not available")
            return None
        try:
            response = client.table('users').select('*').eq('email', email).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error fetching user: {e}")
            return None
    
    @staticmethod
    def get_user_by_id(user_id):
        """Get user by ID"""
        client = get_supabase_client()
        if not client:
            print("Supabase client not available")
            return None
        try:
            response = client.table('users').select('*').eq('id', user_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error fetching user: {e}")
            return None
    
    @staticmethod
    def create_user(user_data):
        """Create a new user"""
        client = get_supabase_client()
        if not client:
            print("Supabase client not available")
            return None
        try:
            response = client.table('users').insert(user_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error creating user: {e}")
            return None
    
    # Conversation operations
    @staticmethod
    def get_user_conversations(user_id):
        """Get all conversations for a user, ordered by updated_at desc"""
        client = get_supabase_client()
        if not client:
            print("Supabase client not available")
            return []
        try:
            response = client.table('conversations').select('*').eq('user_id', user_id).order('updated_at', desc=True).execute()
            return response.data
        except Exception as e:
            print(f"Error fetching conversations: {e}")
            return []
    
    @staticmethod
    def create_conversation(user_id, title="New Conversation"):
        """Create a new conversation"""
        client = get_supabase_client()
        if not client:
            print("Supabase client not available")
            return None
        try:
            conversation_data = {
                'user_id': user_id,
                'title': title
            }
            response = client.table('conversations').insert(conversation_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error creating conversation: {e}")
            return None
    
    @staticmethod
    def get_conversation_by_id(conversation_id, user_id=None):
        """Get conversation by ID"""
        client = get_supabase_client()
        if not client:
            print("Supabase client not available")
            return None
        try:
            query = client.table('conversations').select('*').eq('id', conversation_id)
            if user_id:
                query = query.eq('user_id', user_id)
            response = query.execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error fetching conversation: {e}")
            return None
    
    @staticmethod
    def update_conversation(conversation_id, conversation_data, user_id=None):
        """Update conversation (e.g., title)"""
        client = get_supabase_client()
        if not client:
            print("Supabase client not available")
            return None
        try:
            query = client.table('conversations').update(conversation_data).eq('id', conversation_id)
            if user_id:
                query = query.eq('user_id', user_id)
            response = query.execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error updating conversation: {e}")
            return None
    
    @staticmethod
    def delete_conversation(conversation_id, user_id=None):
        """Delete conversation and all its messages"""
        client = get_supabase_client()
        if not client:
            print("Supabase client not available")
            return False
        try:
            query = client.table('conversations').delete().eq('id', conversation_id)
            if user_id:
                query = query.eq('user_id', user_id)
            response = query.execute()
            return True
        except Exception as e:
            print(f"Error deleting conversation: {e}")
            return False
    
    # Message operations
    @staticmethod
    def get_conversation_messages(conversation_id):
        """Get all messages for a conversation, ordered by timestamp"""
        client = get_supabase_client()
        if not client:
            print("Supabase client not available")
            return []
        try:
            response = client.table('messages').select('*').eq('conversation_id', conversation_id).order('timestamp').execute()
            return response.data
        except Exception as e:
            print(f"Error fetching messages: {e}")
            return []
    
    @staticmethod
    def create_message(conversation_id, content, is_user, function_results=None):
        """Create a new message in a conversation"""
        client = get_supabase_client()
        if not client:
            print("Supabase client not available")
            return None
        try:
            message_data = {
                'conversation_id': conversation_id,
                'content': content,
                'is_user': is_user,
                'function_results': function_results
            }
            response = client.table('messages').insert(message_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error creating message: {e}")
            return None
    
    @staticmethod
    def generate_conversation_title(first_message):
        """Generate conversation title from first message (max 50 chars)"""
        if not first_message:
            return "New Conversation"
        
        if len(first_message) <= 50:
            return first_message
        else:
            return first_message[:47] + "..." 