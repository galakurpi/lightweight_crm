-- Cleanup and Reset Script for Lightweight CRM
-- Run this FIRST to clean up existing tables and policies

-- ================================
-- STEP 1: Disable RLS on all tables
-- ================================
ALTER TABLE IF EXISTS users DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS conversations DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS messages DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS leads DISABLE ROW LEVEL SECURITY;

-- ================================
-- STEP 2: Drop all existing policies
-- ================================
-- Users table policies
DROP POLICY IF EXISTS "Users can view own profile" ON users;
DROP POLICY IF EXISTS "Users can update own profile" ON users;
DROP POLICY IF EXISTS "Allow login access" ON users;
DROP POLICY IF EXISTS "Users can read their own data" ON users;
DROP POLICY IF EXISTS "Enable read access for authentication" ON users;
DROP POLICY IF EXISTS "Prevent client modifications" ON users;
DROP POLICY IF EXISTS "Prevent client updates" ON users;
DROP POLICY IF EXISTS "Prevent client deletes" ON users;

-- Conversations table policies
DROP POLICY IF EXISTS "Users can view own conversations" ON conversations;
DROP POLICY IF EXISTS "Users can insert own conversations" ON conversations;
DROP POLICY IF EXISTS "Users can update own conversations" ON conversations;
DROP POLICY IF EXISTS "Users can delete own conversations" ON conversations;

-- Messages table policies
DROP POLICY IF EXISTS "Users can view messages in own conversations" ON messages;
DROP POLICY IF EXISTS "Users can insert messages in own conversations" ON messages;

-- Leads table policies
DROP POLICY IF EXISTS "Users can view own leads" ON leads;
DROP POLICY IF EXISTS "Users can insert own leads" ON leads;
DROP POLICY IF EXISTS "Users can update own leads" ON leads;
DROP POLICY IF EXISTS "Users can delete own leads" ON leads;

-- ================================
-- STEP 3: Drop all triggers (including existing ones on leads table)
-- ================================
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
DROP TRIGGER IF EXISTS update_conversations_updated_at ON conversations;
DROP TRIGGER IF EXISTS handle_updated_at ON leads;

-- ================================
-- STEP 4: Drop all functions (now safe to drop after triggers are removed)
-- ================================
DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE;
DROP FUNCTION IF EXISTS generate_conversation_title(TEXT) CASCADE;

-- ================================
-- STEP 5: Drop all indexes
-- ================================
DROP INDEX IF EXISTS idx_conversations_user_id;
DROP INDEX IF EXISTS idx_conversations_created_at;
DROP INDEX IF EXISTS idx_messages_conversation_id;
DROP INDEX IF EXISTS idx_messages_timestamp;
DROP INDEX IF EXISTS idx_leads_user_id;

-- ================================
-- STEP 6: Remove user_id column from leads table
-- ================================
ALTER TABLE IF EXISTS leads DROP COLUMN IF EXISTS user_id;

-- ================================
-- STEP 7: Drop all tables in correct order (respecting foreign keys)
-- ================================
DROP TABLE IF EXISTS messages CASCADE;
DROP TABLE IF EXISTS conversations CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Note: We keep the leads table since it's the original table

-- ================================
-- STEP 8: Verification
-- ================================
SELECT 'Database cleaned successfully!' as status;

-- Show remaining tables
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name; 