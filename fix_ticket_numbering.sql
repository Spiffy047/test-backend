-- Fix ticket numbering to TKT-1001, TKT-1002 format
-- Run this script on your PostgreSQL database

BEGIN;

-- Step 1: Create a temporary table to store the mapping
CREATE TEMP TABLE ticket_id_mapping AS
SELECT 
    id as old_id,
    'TKT-' || LPAD((ROW_NUMBER() OVER (ORDER BY created_at))::text + 1000, 4, '0') as new_id
FROM tickets
ORDER BY created_at;

-- Step 2: Add new_id column to tickets table temporarily
ALTER TABLE tickets ADD COLUMN new_id VARCHAR(20);

-- Step 3: Update tickets with new IDs
UPDATE tickets 
SET new_id = mapping.new_id
FROM ticket_id_mapping mapping
WHERE tickets.id = mapping.old_id;

-- Step 4: Update foreign key references in ticket_messages
UPDATE ticket_messages 
SET ticket_id = mapping.new_id
FROM ticket_id_mapping mapping
WHERE ticket_messages.ticket_id = mapping.old_id;

-- Step 5: Update foreign key references in ticket_activities
UPDATE ticket_activities 
SET ticket_id = mapping.new_id
FROM ticket_id_mapping mapping
WHERE ticket_activities.ticket_id = mapping.old_id;

-- Step 6: Update foreign key references in alerts (if table exists)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'alerts') THEN
        UPDATE alerts 
        SET ticket_id = mapping.new_id
        FROM ticket_id_mapping mapping
        WHERE alerts.ticket_id = mapping.old_id;
    END IF;
END $$;

-- Step 7: Drop the old primary key constraint and update the id column
ALTER TABLE tickets DROP CONSTRAINT tickets_pkey;
UPDATE tickets SET id = new_id;
ALTER TABLE tickets DROP COLUMN new_id;
ALTER TABLE tickets ADD PRIMARY KEY (id);

-- Step 8: Create sequence for future ticket numbering
DROP SEQUENCE IF EXISTS ticket_id_seq CASCADE;
CREATE SEQUENCE ticket_id_seq 
START WITH (SELECT COUNT(*) + 1001 FROM tickets)
INCREMENT BY 1;

-- Step 9: Show the results
SELECT 
    COUNT(*) as total_tickets,
    MIN(id) as first_ticket,
    MAX(id) as last_ticket,
    'TKT-' || LPAD((nextval('ticket_id_seq'))::text, 4, '0') as next_ticket_will_be
FROM tickets;

-- Reset sequence to correct value (nextval incremented it)
SELECT setval('ticket_id_seq', (SELECT COUNT(*) + 1001 FROM tickets), false);

COMMIT;

-- Verify the results
SELECT 'Verification:' as status;
SELECT id, title, created_at FROM tickets ORDER BY created_at LIMIT 5;
SELECT 'Next ticket ID will be: TKT-' || LPAD((nextval('ticket_id_seq'))::text, 4, '0') as next_ticket;