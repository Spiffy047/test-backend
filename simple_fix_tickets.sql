-- Simple ticket ID fix - run this on your PostgreSQL database
-- This will update existing tickets to TKT-XXXX format

-- Step 1: Update existing tickets to proper format
UPDATE tickets 
SET id = 'TKT-' || LPAD(ROW_NUMBER() OVER (ORDER BY created_at)::text + 1000, 4, '0')
WHERE id NOT LIKE 'TKT-%';

-- Step 2: Create sequence for new tickets
CREATE SEQUENCE IF NOT EXISTS ticket_id_seq 
START WITH 1002 
INCREMENT BY 1;

-- Verify results
SELECT id, title, created_at FROM tickets ORDER BY created_at LIMIT 5;