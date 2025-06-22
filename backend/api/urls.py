from django.urls import path
from . import views

urlpatterns = [
    # Test endpoint to check if Django is working
    path('test/', views.test_api, name='test_api'),
    
    # Authentication endpoints
    path('auth/login/', views.login_view, name='login'),
    path('auth/logout/', views.logout_view, name='logout'),
    path('auth/user/', views.current_user, name='current_user'),
    
    # Main leads endpoint - GET all leads (grouped by status) or POST new lead
    path('leads/', views.leads_list, name='leads_list'),
    
    # Individual lead operations - GET, PUT, DELETE by ID
    path('leads/<str:lead_id>/', views.lead_detail, name='lead_detail'),
    
    # Special endpoint for updating lead status (Kanban drag & drop)
    path('leads/<str:lead_id>/status/', views.update_lead_status, name='update_lead_status'),
    
    # Conversation endpoints
    path('conversations/', views.conversations_list, name='conversations_list'),
    path('conversations/create/', views.create_conversation, name='create_conversation'),
    path('conversations/<str:conversation_id>/', views.conversation_detail, name='conversation_detail'),
    path('conversations/<str:conversation_id>/messages/', views.conversation_messages, name='conversation_messages'),
    
    # Chat endpoints for AI assistant
    path('chat/', views.chat_message, name='chat_message'),
    path('chat/status/<str:task_id>/', views.chat_status, name='chat_status'),
    path('chat/clear/', views.clear_chat, name='clear_chat'),
] 