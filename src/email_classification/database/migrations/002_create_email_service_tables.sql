-- Create email_accounts table for storing email account credentials
CREATE TABLE IF NOT EXISTS email_accounts (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    server TEXT NOT NULL,
    port INTEGER NOT NULL,
    use_ssl BOOLEAN NOT NULL DEFAULT TRUE,
    username TEXT NOT NULL,
    password TEXT NOT NULL,  -- In production, consider encrypting this
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create email_folders table for tracking which folders to monitor
CREATE TABLE IF NOT EXISTS email_folders (
    id SERIAL PRIMARY KEY,
    account_id INTEGER NOT NULL REFERENCES email_accounts(id) ON DELETE CASCADE,
    folder_name TEXT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    last_checked TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create email_processing_log table for tracking email processing
CREATE TABLE IF NOT EXISTS email_processing_log (
    id SERIAL PRIMARY KEY,
    email_id INTEGER REFERENCES emails(id) ON DELETE SET NULL,
    account_id INTEGER NOT NULL REFERENCES email_accounts(id),
    message_id TEXT,  -- Original email message-id header
    status TEXT NOT NULL,  -- 'success', 'error', 'duplicate', etc.
    error_message TEXT,
    processing_time FLOAT,  -- Time in seconds
    processed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indices
CREATE INDEX IF NOT EXISTS email_folders_account_id_idx ON email_folders(account_id);
CREATE INDEX IF NOT EXISTS email_processing_log_email_id_idx ON email_processing_log(email_id);
CREATE INDEX IF NOT EXISTS email_processing_log_account_id_idx ON email_processing_log(account_id);
CREATE INDEX IF NOT EXISTS email_processing_log_status_idx ON email_processing_log(status);
CREATE INDEX IF NOT EXISTS email_processing_log_processed_at_idx ON email_processing_log(processed_at);