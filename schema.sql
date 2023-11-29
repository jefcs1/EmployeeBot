CREATE TABLE IF NOT EXISTS TradeAds (
        have TEXT,
        want TEXT,
        tradelink TEXT,
        channel_id INTEGER,
        user_id INTEGER,
        next_post TEXT DEFAULT (datetime(CURRENT_TIMESTAMP, '+3 hours')),
        PRIMARY KEY(channel_id, user_id)
    );

CREATE TABLE IF NOT EXISTS Giveaways (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        prize TEXT,
        end_time TEXT,
        completed BOOLEAN DEFAULT FALSE,
        channel_id INTEGER,
        message_id INTEGER,
        req_roles TEXT
    );

CREATE TABLE IF NOT EXISTS GiveawayEntries (
        user_id INTEGER,
        giveaway_id INTEGER,
        FOREIGN KEY(giveaway_id) REFERENCES giveaways(id) ON DELETE CASCADE
    );


CREATE TABLE IF NOT EXISTS Bumps (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        guild_id INTEGER,
        channel_id INTEGER,
        user_id INTEGER,
        timestamp TEXT NOT NULL DEFAULT (datetime(CURRENT_TIMESTAMP))
    );

CREATE TABLE IF NOT EXISTS Inventories (
        discord_id INTEGER,
        steam_id INTEGER
    );

CREATE TABLE IF NOT EXISTS Counting (
        last_sender INTEGER,
        last_number INTEGER
    );

CREATE TABLE IF NOT EXISTS Tempban (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        unban_time TEXT
    );

CREATE TABLE IF NOT EXISTS Warns (
        warn_id INTEGER PRIMARY KEY AUTOINCREMENT,
        moderator_id INTEGER,
        user_id INTEGER,
        warn_reason TEXT,
        timestamp TEXT NOT NULL DEFAULT (datetime(CURRENT_TIMESTAMP))
    );