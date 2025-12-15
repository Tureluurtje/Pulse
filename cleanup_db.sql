-- SQL script to remove all data from the database (except test users)
-- Deletes in reverse order of foreign key dependencies
-- Preserves: test@test.com and botuser@test.com

DELETE FROM messages
WHERE sender_id NOT IN (
    SELECT id FROM users WHERE email IN ('test@test.com')
);

DELETE FROM participants
WHERE conversation_id IN (
    SELECT c.id FROM conversations c
    WHERE c.created_by NOT IN (
        SELECT id FROM users WHERE email IN ('test@test.com', 'botuser@test.com')
    )
);

DELETE FROM conversations
WHERE created_by NOT IN (
    SELECT id FROM users WHERE email IN ('test@test.com', 'botuser@test.com')
);

DELETE FROM tokens
WHERE user_id NOT IN (
    SELECT id FROM users WHERE email IN ('test@test.com', 'botuser@test.com')
);

DELETE FROM user_profiles
WHERE user_id NOT IN (
    SELECT id FROM users WHERE email IN ('test@test.com', 'botuser@test.com')
);

DELETE FROM users
WHERE email NOT IN ('test@test.com', 'botuser@test.com');

-- Verify cleanup
SELECT 'users' as table_name, COUNT(*) as record_count FROM users
UNION ALL
SELECT 'tokens', COUNT(*) FROM tokens
UNION ALL
SELECT 'user_profiles', COUNT(*) FROM user_profiles
UNION ALL
SELECT 'conversations', COUNT(*) FROM conversations
UNION ALL
SELECT 'participants', COUNT(*) FROM participants
UNION ALL
SELECT 'messages', COUNT(*) FROM messages;
