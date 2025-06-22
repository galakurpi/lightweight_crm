from django.conf import settings
from openai import OpenAI
import json
import re
from typing import Dict, List, Optional, Any
from .supabase_client import SupabaseService


def parse_currency_value(value_str: str) -> Optional[float]:
    """
    Parse various currency formats and return the numeric value.
    
    Supports formats like:
    - "500 euros", "500 EUR", "€500"
    - "$2500", "2500 USD", "2500 dollars"
    - "1000", "1,000.50", "1.000,50"
    - "£1500", "1500 GBP", "1500 pounds"
    
    Args:
        value_str (str): String containing currency value
        
    Returns:
        Optional[float]: Parsed numeric value or None if parsing fails
    """
    if not value_str:
        return None
    
    # Convert to string and clean up
    value_str = str(value_str).strip().lower()
    
    # Remove common currency symbols and words
    currency_patterns = [
        r'[€$£¥₹₽¢]',  # Currency symbols
        r'\b(usd|eur|gbp|jpy|inr|rub|cents?|dollars?|euros?|pounds?|yen|rupees?|rubles?)\b',  # Currency words
        r'\b(k|thousand|m|million|b|billion)\b'  # Scale words (we'll handle these separately)
    ]
    
    # Extract scale multipliers before removing them
    scale_multiplier = 1
    if 'k' in value_str or 'thousand' in value_str:
        scale_multiplier = 1000
    elif 'm' in value_str or 'million' in value_str:
        scale_multiplier = 1000000
    elif 'b' in value_str or 'billion' in value_str:
        scale_multiplier = 1000000000
    
    # Remove currency symbols and words
    cleaned = value_str
    for pattern in currency_patterns:
        cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
    
    # Remove extra whitespace
    cleaned = re.sub(r'\s+', '', cleaned)
    
    # Handle different decimal separators (European vs US format)
    # European: 1.000,50 or 1 000,50
    # US: 1,000.50
    
    # Check if it looks like European format (comma as decimal separator)
    if re.match(r'^\d{1,3}(\.\d{3})*,\d{2}$', cleaned) or re.match(r'^\d+,\d{1,2}$', cleaned):
        # European format: replace dots with nothing, comma with dot
        cleaned = cleaned.replace('.', '').replace(',', '.')
    else:
        # US format or simple number: remove commas (thousand separators)
        cleaned = cleaned.replace(',', '')
    
    # Try to convert to float
    try:
        numeric_value = float(cleaned)
        return numeric_value * scale_multiplier
    except (ValueError, TypeError):
        # Try to extract just the numbers
        numbers = re.findall(r'\d+\.?\d*', cleaned)
        if numbers:
            try:
                return float(numbers[0]) * scale_multiplier
            except (ValueError, TypeError):
                pass
        return None


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
        Clear conversation context and pending deletions from Django session.
        
        Args:
            session_key (str): Django session key
        """
        from django.contrib.sessions.backends.db import SessionStore
        
        try:
            session = SessionStore(session_key=session_key)
            session['chat_context'] = []
            session['pending_deletions'] = {}
            session.save()
        except Exception as e:
            print(f"Error clearing conversation context: {e}")
    
    def get_pending_deletions(self, session_key: str) -> Dict:
        """
        Get pending lead deletions from Django session.
        
        Args:
            session_key (str): Django session key
            
        Returns:
            Dict: Pending deletions {lead_id: lead_data}
        """
        from django.contrib.sessions.backends.db import SessionStore
        
        try:
            session = SessionStore(session_key=session_key)
            return session.get('pending_deletions', {})
        except Exception:
            return {}
    
    def add_pending_deletion(self, session_key: str, lead_id: str, lead_data: Dict) -> None:
        """
        Add a lead to pending deletions in Django session.
        
        Args:
            session_key (str): Django session key
            lead_id (str): Lead ID to mark for deletion
            lead_data (Dict): Lead data for confirmation message
        """
        from django.contrib.sessions.backends.db import SessionStore
        
        try:
            session = SessionStore(session_key=session_key)
            pending = session.get('pending_deletions', {})
            pending[lead_id] = lead_data
            session['pending_deletions'] = pending
            session.save()
        except Exception as e:
            print(f"Error adding pending deletion: {e}")
    
    def remove_pending_deletion(self, session_key: str, lead_id: str) -> None:
        """
        Remove a lead from pending deletions in Django session.
        
        Args:
            session_key (str): Django session key
            lead_id (str): Lead ID to remove from pending deletions
        """
        from django.contrib.sessions.backends.db import SessionStore
        
        try:
            session = SessionStore(session_key=session_key)
            pending = session.get('pending_deletions', {})
            if lead_id in pending:
                del pending[lead_id]
                session['pending_deletions'] = pending
                session.save()
        except Exception as e:
            print(f"Error removing pending deletion: {e}")
    
    def get_openai_functions(self) -> List[Dict]:
        """
        Define OpenAI function schemas for lead operations.
        
        Returns:
            List[Dict]: Function definitions for OpenAI function calling
        """
        return [
            {
                "name": "search_leads",
                "description": "Search for leads by name, company, email, or other lead data",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query (name, company, email, or other lead data)"
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
                            "description": "New value for the field. For currency values, use formats like '500 euros', '$2500', '1000 USD', '€1500', etc."
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
                            "type": "string",
                            "description": "Lead value in any currency format like '500 euros', '$2500', '1000 USD', '€1500', etc."
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
                "description": "Request deletion of a lead - this will ask for user confirmation and NOT actually delete the lead yet",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lead_id": {
                            "type": "string",
                            "description": "ID of the lead to request deletion for"
                        }
                    },
                    "required": ["lead_id"]
                }
            },
            {
                "name": "confirm_delete_lead",
                "description": "Actually delete a lead after user has confirmed - only use this when user has explicitly confirmed deletion",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lead_id": {
                            "type": "string",
                            "description": "ID of the lead to permanently delete"
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
    
    def execute_function_call(self, function_name: str, arguments: Dict, leads: List[Dict], session_key: str = None, user_id: str = None) -> Dict:
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
            # Debug logging
            if session_key:
                pending = self.get_pending_deletions(session_key)
                print(f"EXECUTE_FUNCTION_CALL: Pending deletions: {pending}")
                
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
                }, user_id=user_id)
                
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
                    parsed_value = parse_currency_value(value)
                    if parsed_value is None:
                        return {
                            "success": False,
                            "message": f"Invalid currency format '{value}'. Please use formats like '500 euros', '$2500', '1000 USD', etc."
                        }
                    value = parsed_value
                
                updated_lead = SupabaseService.update_lead(lead_id, {field: value}, user_id=user_id)
                
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
                
                # Parse currency value if provided
                if 'value' in arguments and arguments['value'] is not None:
                    parsed_value = parse_currency_value(str(arguments['value']))
                    if parsed_value is None:
                        return {
                            "success": False,
                            "message": f"Invalid currency format '{arguments['value']}'. Please use formats like '500 euros', '$2500', '1000 USD', etc."
                        }
                    arguments['value'] = parsed_value
                
                # Set card order
                same_status_leads = [l for l in leads if l.get('status') == arguments['status']]
                arguments['card_order'] = len(same_status_leads) + 1
                
                new_lead = SupabaseService.create_lead(arguments, user_id=user_id)
                
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
                print(f"DELETE_LEAD_FUNCTION: Starting delete_lead function with lead_id: {arguments.get('lead_id')}")
                lead_id = arguments.get("lead_id")
                
                # Find lead for confirmation message
                lead = next((l for l in leads if l.get('id') == lead_id), None)
                if not lead:
                    print(f"DEBUG: Lead not found for id: {lead_id}")
                    return {
                        "success": False,
                        "message": "Lead not found"
                    }
                
                print(f"DEBUG: Found lead: {lead.get('name')}")
                
                # Add to pending deletions instead of deleting immediately
                if session_key:
                    print(f"DEBUG: Adding to pending deletions for session: {session_key}")
                    self.add_pending_deletion(session_key, lead_id, lead)
                else:
                    print("DEBUG: No session key provided!")
                
                confirmation_message = f"⚠️ Are you sure you want to delete '{lead.get('name', 'Unknown')}'?\n\nThis action cannot be undone. Please confirm by saying 'yes, delete {lead.get('name', 'this lead')}' or 'confirm deletion'."
                
                result = {
                    "success": True,
                    "requires_confirmation": True,
                    "message": confirmation_message
                }
                print(f"DEBUG: Final result: {result}")
                return result
            
            elif function_name == "confirm_delete_lead":
                lead_id = arguments.get("lead_id")
                
                # Check if this lead is in pending deletions
                if not session_key:
                    return {
                        "success": False,
                        "message": "Session error - cannot confirm deletion"
                    }
                
                pending_deletions = self.get_pending_deletions(session_key)
                if lead_id not in pending_deletions:
                    return {
                        "success": False,
                        "message": "No pending deletion found for this lead. Please request deletion first."
                    }
                
                lead_data = pending_deletions[lead_id]
                
                # Actually delete the lead
                success = SupabaseService.delete_lead(lead_id, user_id=user_id)
                
                if success:
                    # Remove from pending deletions
                    self.remove_pending_deletion(session_key, lead_id)
                    return {
                        "success": True,
                        "message": f"✅ Lead '{lead_data.get('name', 'Unknown')}' has been permanently deleted."
                    }
                else:
                    return {
                        "success": False,
                        "message": "Failed to delete lead. Please try again."
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
    
    def process_message(self, message: str, session_key: str, leads: List[Dict], conversation_id: str = None, user_id: str = None) -> Dict:
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
            
            # Get pending deletions for context
            pending_deletions = self.get_pending_deletions(session_key) if session_key else {}
            
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

Pending deletions requiring confirmation: {json.dumps(pending_deletions, indent=2)}

You can:
1. Search for leads by name, company, or email
2. Update lead status (move between Kanban columns)
3. Update lead data (name, company, email, phone, value, notes, source)
4. Create new leads with provided information
5. Delete leads (requires confirmation - first call delete_lead, then user must confirm)

CURRENCY VALUE SUPPORT:
- Accept any currency format: "500 euros", "$2500", "1000 USD", "€1500", "£2000", "1.5k", "2M", etc.
- Automatically parse and convert to numeric values
- Support multiple currencies: USD, EUR, GBP, JPY, INR, RUB, etc.
- Handle different decimal formats: "1,000.50" (US) or "1.000,50" (European)

CRITICAL DELETION RULES:
1. NEVER use confirm_delete_lead unless user has explicitly confirmed deletion
2. When user asks to delete a lead, ALWAYS use delete_lead function first (this only requests confirmation, does NOT delete)
3. delete_lead function will add lead to pending deletions and ask user for confirmation
4. Only use confirm_delete_lead when user says "yes", "confirm", "delete it", etc. AND there are pending deletions
5. Check pending deletions to know which leads are awaiting confirmation
6. If user cancels, just acknowledge (no function call needed)
7. Distinguish between removing information from a lead and deleting a lead.

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
                result = self.execute_function_call(function_name, function_args, leads, session_key, user_id)
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
            
            # Save AI response to database if conversation_id is provided
            if conversation_id:
                SupabaseService.create_message(
                    conversation_id, 
                    ai_message, 
                    is_user=False, 
                    function_results=function_results
                )
            
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