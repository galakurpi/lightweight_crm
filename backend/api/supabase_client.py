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
    """Service class to handle Supabase operations for leads"""
    
    @staticmethod
    def get_all_leads():
        """Fetch all leads from Supabase, ordered by status and card_order"""
        client = get_supabase_client()
        if not client:
            print("Supabase client not available")
            return []
        try:
            response = client.table('leads').select('*').order('status').order('card_order').execute()
            return response.data
        except Exception as e:
            print(f"Error fetching leads: {e}")
            return []
    
    @staticmethod
    def create_lead(lead_data):
        """Create a new lead in Supabase"""
        client = get_supabase_client()
        if not client:
            print("Supabase client not available")
            return None
        try:
            response = client.table('leads').insert(lead_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error creating lead: {e}")
            return None
    
    @staticmethod
    def update_lead(lead_id, lead_data):
        """Update an existing lead in Supabase"""
        client = get_supabase_client()
        if not client:
            print("Supabase client not available")
            return None
        try:
            response = client.table('leads').update(lead_data).eq('id', lead_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error updating lead: {e}")
            return None
    
    @staticmethod
    def delete_lead(lead_id):
        """Delete a lead from Supabase"""
        client = get_supabase_client()
        if not client:
            print("Supabase client not available")
            return False
        try:
            response = client.table('leads').delete().eq('id', lead_id).execute()
            return True
        except Exception as e:
            print(f"Error deleting lead: {e}")
            return False
    
    @staticmethod
    def get_lead_by_id(lead_id):
        """Get a specific lead by ID"""
        client = get_supabase_client()
        if not client:
            print("Supabase client not available")
            return None
        try:
            response = client.table('leads').select('*').eq('id', lead_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error fetching lead: {e}")
            return None 