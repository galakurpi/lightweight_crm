-- Supabase Table Setup for Conversation History Feature
-- Execute these SQL commands in your Supabase SQL editor

-- 1. Create users table (extends Django's auth functionality)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    first_name VARCHAR(150),
    last_name VARCHAR(150),
    is_active BOOLEAN DEFAULT TRUE,
    date_joined TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 2. Create conversations table
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL DEFAULT 'New Conversation',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 3. Create messages table
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    is_user BOOLEAN NOT NULL,
    function_results JSONB,
    timestamp TIMESTAMP DEFAULT NOW()
);

-- 4. Add user_id column to existing leads table
ALTER TABLE leads ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES users(id) ON DELETE CASCADE;

-- 5. Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_conversations_created_at ON conversations(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_leads_user_id ON leads(user_id);

-- 6. Create default admin user
-- First, temporarily disable RLS to allow user creation
ALTER TABLE users DISABLE ROW LEVEL SECURITY;

-- Delete existing admin user if exists
DELETE FROM users WHERE email = 'admin@crm.local';

-- Insert admin user with proper password hash for 'admin123'
INSERT INTO users (
    id, 
    email, 
    password_hash, 
    is_admin, 
    first_name, 
    last_name, 
    is_active, 
    date_joined, 
    created_at, 
    updated_at
) VALUES (
    gen_random_uuid(),
    'admin@crm.local',
    'pbkdf2_sha256$600000$0tak1PsAWvlN5ql5b0qdEe$97ycFXjFzxjBnoPRVadjB/W3qiGXL3ittYXjFM5NMWc=',
    true,
    'Admin',
    'User',
    true,
    NOW(),
    NOW(),
    NOW()
);

-- 7. Get the admin user ID for leads migration
DO $$
DECLARE
    admin_user_id UUID;
BEGIN
    SELECT id INTO admin_user_id FROM users WHERE email = 'admin@crm.local';
    
    -- Update all existing leads to belong to admin user
    UPDATE leads SET user_id = admin_user_id WHERE user_id IS NULL;
END $$;

-- 8. Add Row Level Security (RLS) policies for data isolation
-- Re-enable RLS for users table with proper policies
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE leads ENABLE ROW LEVEL SECURITY;

-- Drop any existing policies first
DROP POLICY IF EXISTS "Users can view own profile" ON users;
DROP POLICY IF EXISTS "Users can update own profile" ON users;
DROP POLICY IF EXISTS "Allow login access" ON users;
DROP POLICY IF EXISTS "Users can read their own data" ON users;
DROP POLICY IF EXISTS "Enable read access for authentication" ON users;
DROP POLICY IF EXISTS "Prevent client modifications" ON users;
DROP POLICY IF EXISTS "Prevent client updates" ON users;
DROP POLICY IF EXISTS "Prevent client deletes" ON users;

-- RLS Policies for users table (allow authentication but prevent client modifications)
CREATE POLICY "Enable read access for authentication" ON users
    FOR SELECT 
    USING (true);

CREATE POLICY "Prevent client modifications" ON users
    FOR INSERT 
    WITH CHECK (false);

CREATE POLICY "Prevent client updates" ON users
    FOR UPDATE 
    USING (false);

CREATE POLICY "Prevent client deletes" ON users
    FOR DELETE 
    USING (false);

-- RLS Policies for conversations table
CREATE POLICY "Users can view own conversations" ON conversations
    FOR SELECT USING (user_id::text = current_setting('app.current_user_id', true));

CREATE POLICY "Users can insert own conversations" ON conversations
    FOR INSERT WITH CHECK (user_id::text = current_setting('app.current_user_id', true));

CREATE POLICY "Users can update own conversations" ON conversations
    FOR UPDATE USING (user_id::text = current_setting('app.current_user_id', true))
    WITH CHECK (user_id::text = current_setting('app.current_user_id', true));

CREATE POLICY "Users can delete own conversations" ON conversations
    FOR DELETE USING (user_id::text = current_setting('app.current_user_id', true));

-- RLS Policies for messages table
CREATE POLICY "Users can view messages in own conversations" ON messages
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM conversations 
            WHERE conversations.id = messages.conversation_id 
            AND conversations.user_id::text = current_setting('app.current_user_id', true)
        )
    );

CREATE POLICY "Users can insert messages in own conversations" ON messages
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM conversations 
            WHERE conversations.id = messages.conversation_id 
            AND conversations.user_id::text = current_setting('app.current_user_id', true)
        )
    );

-- RLS Policies for leads table
CREATE POLICY "Users can view own leads" ON leads
    FOR SELECT USING (user_id::text = current_setting('app.current_user_id', true));

CREATE POLICY "Users can insert own leads" ON leads
    FOR INSERT WITH CHECK (user_id::text = current_setting('app.current_user_id', true));

CREATE POLICY "Users can update own leads" ON leads
    FOR UPDATE USING (user_id::text = current_setting('app.current_user_id', true))
    WITH CHECK (user_id::text = current_setting('app.current_user_id', true));

CREATE POLICY "Users can delete own leads" ON leads
    FOR DELETE USING (user_id::text = current_setting('app.current_user_id', true));

-- 9. Create functions for updating timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 10. Create triggers for auto-updating timestamps
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_conversations_updated_at BEFORE UPDATE ON conversations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 11. Create function to generate conversation titles from first message
CREATE OR REPLACE FUNCTION generate_conversation_title(first_message TEXT)
RETURNS TEXT AS $$
BEGIN
    IF LENGTH(first_message) <= 50 THEN
        RETURN first_message;
    ELSE
        RETURN LEFT(first_message, 47) || '...';
    END IF;
END;
$$ LANGUAGE plpgsql;

-- 12. Verify admin user creation and setup
DO $$
DECLARE
    user_count INTEGER;
    admin_email TEXT;
BEGIN
    SELECT COUNT(*) INTO user_count 
    FROM users 
    WHERE email = 'admin@crm.local' AND is_admin = true;
    
    IF user_count > 0 THEN
        SELECT email INTO admin_email 
        FROM users 
        WHERE email = 'admin@crm.local' AND is_admin = true;
        
        RAISE NOTICE '✅ Admin user created successfully!';
        RAISE NOTICE '📧 Email: %', admin_email;
        RAISE NOTICE '🔑 Password: admin123';
        RAISE NOTICE '🔒 RLS enabled with proper authentication policies';
    ELSE
        RAISE NOTICE '❌ Failed to create admin user';
    END IF;
END $$;

-- 13. Display final setup status
SELECT 
    '✅ SETUP COMPLETE' as status,
    email as login_email,
    'admin123' as login_password,
    is_admin as admin_privileges,
    first_name || ' ' || last_name as full_name,
    created_at as created_on
FROM users 
WHERE email = 'admin@crm.local';

-- Verification queries (uncomment to run additional checks)
-- SELECT 'Tables created successfully' as status;
-- SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name IN ('users', 'conversations', 'messages');
-- SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'leads' AND column_name = 'user_id'; 