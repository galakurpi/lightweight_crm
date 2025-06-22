from http.server import BaseHTTPRequestHandler
import json
import os
from urllib.parse import urlparse, parse_qs

# Import your existing Supabase client
import sys
sys.path.append('../backend')
from backend.api.supabase_client import SupabaseService

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Handle GET /api/leads/
        try:
            supabase_service = SupabaseService()
            leads = supabase_service.get_all_leads()
            
            # Group leads by status for Kanban board
            grouped_leads = {
                'Interest': [],
                'Meeting booked': [],
                'Proposal sent': [],
                'Closed win': [],
                'Closed lost': []
            }
            
            for lead in leads:
                status = lead.get('status', 'Interest')
                if status in grouped_leads:
                    grouped_leads[status].append(lead)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(grouped_leads).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())
    
    def do_POST(self):
        # Handle POST /api/leads/
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            lead_data = json.loads(post_data)
            
            supabase_service = SupabaseService()
            new_lead = supabase_service.create_lead(lead_data)
            
            self.send_response(201)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(new_lead).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode()) 