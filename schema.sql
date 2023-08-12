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
        prize TEXT,
        end_time TEXT,
        completed BOOLEAN DEFAULT FALSE,
        channel_id INTEGER,
        message_id INTEGER,
        PRIMARY KEY(channel_id, message_id)
    );


CREATE TABLE IF NOT EXISTS Bumps (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        guild_id INTEGER,
        channel_id INTEGER,
        user_id INTEGER,
        timestamp TEXT NOT NULL DEFAULT (datetime(CURRENT_TIMESTAMP))
    );