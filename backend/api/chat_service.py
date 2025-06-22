from django.conf import settings
from openai import OpenAI
import json
import re
from typing import Dict, List, Optional, Any
from .supabase_client import SupabaseService


class ChatService:
    """
    Service class for handling AI chat functionality with OpenAI integration.
    Manages conversation context, intent routing, and lead matching.
    """
    
    def __init__(self):
        """Initialize OpenAI client and conversation context."""
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-4-1106-preview"  # GPT-4 Turbo with function calling
    
    def get_conversation_context(self, session_key: str) -> List[Dict]:
        """
        Retrieve conversation context from Django session.
        
        Args:
            session_key (str): Django session key
            
        Returns:
            List[Dict]: Conversation context messages
        """
        from django.contrib.sessions.models import Session
        from django.contrib.sessions.backends.db import SessionStore
        
        try:
            session = SessionStore(session_key=session_key)
            return session.get('chat_context', [])
        except Exception:
            return []
    
    def update_conversation_context(self, session_key: str, message: Dict) -> None:
        """
        Update conversation context in Django session.
        
        Args:
            session_key (str): Django session key
            message (Dict): Message to add to context
        """
        from django.contrib.sessions.backends.db import SessionStore
        
        try:
            session = SessionStore(session_key=session_key)
            context = session.get('chat_context', [])
            context.append(message)
            
            # Keep only last 10 messages for context management
            if len(context) > 10:
                context = context[-10:]
            
            session['chat_context'] = context
            session.save()
        except Exception as e:
            print(f"Error updating conversation context: {e}")
    
    def clear_conversation_context(self, session_key: str) -> None:
        """
        Clear conversation context from Django session.
        
        Args:
            session_key (str): Django session key
        """
        from django.contrib.sessions.backends.db import SessionStore
        
        try:
            session = SessionStore(session_key=session_key)
            session['chat_context'] = []
            session.save()
        except Exception as e:
            print(f"Error clearing conversation context: {e}")
    
    def get_openai_functions(self) -> List[Dict]:
        """
        Define OpenAI function schemas for lead operations.
        
        Returns:
            List[Dict]: Function definitions for OpenAI function calling
        """
        return [
            {
                "name": "search_leads",
                "description": "Search for leads by name, company, or email",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query (name, company, or email)"
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "update_lead_status",
                "description": "Update the status of a lead",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lead_id": {
                            "type": "string",
                            "description": "ID of the lead to update"
                        },
                        "new_status": {
                            "type": "string",
                            "enum": ["Interest", "Meeting booked", "Proposal sent", "Closed win", "Closed lost"],
                            "description": "New status for the lead"
                        }
                    },
                    "required": ["lead_id", "new_status"]
                }
            },
            {
                "name": "update_lead_data",
                "description": "Update specific data fields of a lead",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lead_id": {
                            "type": "string",
                            "description": "ID of the lead to update"
                        },
                        "field": {
                            "type": "string",
                            "enum": ["name", "company", "email", "phone", "value", "notes", "source"],
                            "description": "Field to update"
                        },
                        "value": {
                            "type": "string",
                            "description": "New value for the field"
                        }
                    },
                    "required": ["lead_id", "field", "value"]
                }
            },
            {
                "name": "create_lead",
                "description": "Create a new lead with provided information",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Lead's name"
                        },
                        "company": {
                            "type": "string",
                            "description": "Company name"
                        },
                        "email": {
                            "type": "string",
                            "description": "Email address"
                        },
                        "phone": {
                            "type": "string",
                            "description": "Phone number"
                        },
                        "value": {
                            "type": "number",
                            "description": "Lead value in dollars"
                        },
                        "notes": {
                            "type": "string",
                            "description": "Additional notes"
                        },
                        "source": {
                            "type": "string",
                            "description": "Lead source"
                        },
                        "status": {
                            "type": "string",
                            "enum": ["Interest", "Meeting booked", "Proposal sent", "Closed win", "Closed lost"],
                            "description": "Initial status (defaults to Interest)"
                        }
                    },
                    "required": ["name"]
                }
            },
            {
                "name": "delete_lead",
                "description": "Delete a lead (requires confirmation for destructive action)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lead_id": {
                            "type": "string",
                            "description": "ID of the lead to delete"
                        }
                    },
                    "required": ["lead_id"]
                }
            }
        ]
    
    def find_matching_leads(self, query: str, leads: List[Dict]) -> List[Dict]:
        """
        Find leads that match the search query using fuzzy matching.
        
        Args:
            query (str): Search query
            leads (List[Dict]): Available leads
            
        Returns:
            List[Dict]: Matching leads sorted by relevance
        """
        if not query or not leads:
            return []
        
        query_lower = query.lower()
        matches = []
        
        for lead in leads:
            score = 0
            
            # Name matching (highest weight)
            if lead.get('name') and query_lower in lead['name'].lower():
                score += 70
                if lead['name'].lower().startswith(query_lower):
                    score += 20  # Bonus for prefix match
            
            # Company matching
            if lead.get('company') and query_lower in lead['company'].lower():
                score += 20
            
            # Email matching
            if lead.get('email') and query_lower in lead['email'].lower():
                score += 10
            
            if score > 0:
                matches.append((lead, score))
        
        # Sort by score descending and return leads
        matches.sort(key=lambda x: x[1], reverse=True)
        return [match[0] for match in matches]
    
    def execute_function_call(self, function_name: str, arguments: Dict, leads: List[Dict]) -> Dict:
        """
        Execute OpenAI function calls for lead operations.
        
        Args:
            function_name (str): Name of the function to execute
            arguments (Dict): Function arguments
            leads (List[Dict]): Available leads for context
            
        Returns:
            Dict: Function execution result
        """
        try:
            if function_name == "search_leads":
                query = arguments.get("query", "")
                matching_leads = self.find_matching_leads(query, leads)
                return {
                    "success": True,
                    "data": matching_leads[:5],  # Return top 5 matches
                    "message": f"Found {len(matching_leads)} matching leads"
                }
            
            elif function_name == "update_lead_status":
                lead_id = arguments.get("lead_id")
                new_status = arguments.get("new_status")
                
                # Calculate new order (place at end of column)
                same_status_leads = [l for l in leads if l.get('status') == new_status]
                new_order = len(same_status_leads) + 1
                
                updated_lead = SupabaseService.update_lead(lead_id, {
                    'status': new_status,
                    'card_order': new_order
                })
                
                if updated_lead:
                    return {
                        "success": True,
                        "data": updated_lead,
                        "message": f"Lead status updated to '{new_status}'"
                    }
                else:
                    return {
                        "success": False,
                        "message": "Failed to update lead status"
                    }
            
            elif function_name == "update_lead_data":
                lead_id = arguments.get("lead_id")
                field = arguments.get("field")
                value = arguments.get("value")
                
                # Convert value to appropriate type
                if field == "value":
                    try:
                        value = float(value)
                    except (ValueError, TypeError):
                        return {
                            "success": False,
                            "message": "Invalid value format for lead value field"
                        }
                
                updated_lead = SupabaseService.update_lead(lead_id, {field: value})
                
                if updated_lead:
                    return {
                        "success": True,
                        "data": updated_lead,
                        "message": f"Lead {field} updated to '{value}'"
                    }
                else:
                    return {
                        "success": False,
                        "message": f"Failed to update lead {field}"
                    }
            
            elif function_name == "create_lead":
                # Set default status if not provided
                if 'status' not in arguments:
                    arguments['status'] = 'Interest'
                
                # Set card order
                same_status_leads = [l for l in leads if l.get('status') == arguments['status']]
                arguments['card_order'] = len(same_status_leads) + 1
                
                new_lead = SupabaseService.create_lead(arguments)
                
                if new_lead:
                    return {
                        "success": True,
                        "data": new_lead,
                        "message": f"New lead '{arguments.get('name')}' created successfully"
                    }
                else:
                    return {
                        "success": False,
                        "message": "Failed to create lead"
                    }
            
            elif function_name == "delete_lead":
                lead_id = arguments.get("lead_id")
                
                # Find lead for confirmation message
                lead = next((l for l in leads if l.get('id') == lead_id), None)
                if not lead:
                    return {
                        "success": False,
                        "message": "Lead not found"
                    }
                
                success = SupabaseService.delete_lead(lead_id)
                
                if success:
                    return {
                        "success": True,
                        "message": f"Lead '{lead.get('name', 'Unknown')}' deleted successfully"
                    }
                else:
                    return {
                        "success": False,
                        "message": "Failed to delete lead"
                    }
            
            else:
                return {
                    "success": False,
                    "message": f"Unknown function: {function_name}"
                }
        
        except Exception as e:
            return {
                "success": False,
                "message": f"Error executing {function_name}: {str(e)}"
            }
    
    def process_message(self, message: str, session_key: str, leads: List[Dict]) -> Dict:
        """
        Process user message with OpenAI and execute any required functions.
        
        Args:
            message (str): User's message
            session_key (str): Django session key
            leads (List[Dict]): Available leads
            
        Returns:
            Dict: AI response and function execution results
        """
        try:
            # Get conversation context
            context = self.get_conversation_context(session_key)
            
            # Prepare system message
            system_message = {
                "role": "system",
                "content": f"""You are a CRM assistant. You help manage leads in a Kanban board with these statuses:
- Interest
- Meeting booked  
- Proposal sent
- Closed win
- Closed lost

Available leads: {json.dumps(leads, indent=2)}

You can:
1. Search for leads by name, company, or email
2. Update lead status (move between Kanban columns)
3. Update lead data (name, company, email, phone, value, notes, source)
4. Create new leads with provided information
5. Delete leads (ask for confirmation first)

Be formal but brief in responses. When referencing leads from conversation context, use smart matching to identify the correct lead."""
            }
            
            # Prepare messages for OpenAI
            messages = [system_message] + context + [{"role": "user", "content": message}]
            
            # Call OpenAI with function calling
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                functions=self.get_openai_functions(),
                function_call="auto",
                temperature=0.1
            )
            
            response_message = response.choices[0].message
            function_results = []
            
            # Execute function calls if any
            if response_message.function_call:
                function_name = response_message.function_call.name
                function_args = json.loads(response_message.function_call.arguments)
                
                # Execute the function
                result = self.execute_function_call(function_name, function_args, leads)
                function_results.append({
                    "function": function_name,
                    "arguments": function_args,
                    "result": result
                })
                
                # Add function result to conversation for final response
                messages.append({
                    "role": "function",
                    "name": function_name,
                    "content": json.dumps(result)
                })
                
                # Get final response from AI
                final_response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.1
                )
                
                ai_message = final_response.choices[0].message.content
            else:
                ai_message = response_message.content
            
            # Update conversation context
            self.update_conversation_context(session_key, {"role": "user", "content": message})
            self.update_conversation_context(session_key, {"role": "assistant", "content": ai_message})
            
            return {
                "ai_message": ai_message,
                "function_results": function_results,
                "status": "success"
            }
        
        except Exception as e:
            return {
                "ai_message": "I apologize, but I encountered an error processing your request. Please try again.",
                "function_results": [],
                "status": "error",
                "error": str(e)
            } 