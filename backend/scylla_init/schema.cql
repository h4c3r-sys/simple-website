-- Create the keyspace
CREATE KEYSPACE IF NOT EXISTS discord_clone WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

USE discord_clone;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id uuid PRIMARY KEY,
    username text,
    password_hash text,
    public_key text, -- Public key for E2EE
    created_at timestamp
);

-- Servers table
CREATE TABLE IF NOT EXISTS servers (
    id uuid PRIMARY KEY,
    name text,
    owner_id uuid,
    created_at timestamp
);

-- Channels table
CREATE TABLE IF NOT EXISTS channels (
    id uuid PRIMARY KEY,
    server_id uuid,
    name text,
    created_at timestamp
);
CREATE INDEX IF NOT EXISTS ON channels (server_id);

-- DMs table (maps users to a DM channel)
CREATE TABLE IF NOT EXISTS dm_channels (
    id uuid PRIMARY KEY,
    user1_id uuid,
    user2_id uuid,
    created_at timestamp
);
CREATE INDEX IF NOT EXISTS ON dm_channels (user1_id);
CREATE INDEX IF NOT EXISTS ON dm_channels (user2_id);

-- Messages table (optimized for fetching messages by channel chronologically)
CREATE TABLE IF NOT EXISTS messages (
    channel_id uuid,
    id timeuuid, -- Used for chronological ordering
    author_id uuid,
    ciphertext text, -- The AES-256-GCM encrypted message
    nonce text, -- Nonce used for encryption
    created_at timestamp,
    PRIMARY KEY (channel_id, id)
) WITH CLUSTERING ORDER BY (id ASC);
