-- QuickDealr v6 -- Multi-port modular schema
-- All tables shared between admin_app (5001) and user_app (5000)
PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT    UNIQUE NOT NULL,
    password      TEXT    NOT NULL,
    email         TEXT    NOT NULL DEFAULT '',
    role          TEXT    NOT NULL DEFAULT 'buyer'
                          CHECK(role IN ('buyer','seller','admin')),
    is_active     INTEGER NOT NULL DEFAULT 1,
    session_token TEXT    DEFAULT NULL,
    avatar        TEXT    DEFAULT '',
    wallet        REAL    NOT NULL DEFAULT 0.0,
    phone         TEXT    DEFAULT '',
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sessions (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token      TEXT    UNIQUE NOT NULL,
    ip_address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    is_valid   INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS categories (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    icon TEXT DEFAULT '[box]'
);

CREATE TABLE IF NOT EXISTS products (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT    NOT NULL,
    description     TEXT    DEFAULT '',
    price           REAL    NOT NULL CHECK(price > 0),
    category        TEXT    NOT NULL,
    image           TEXT    DEFAULT '',
    seller_id       INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    seller_name     TEXT    NOT NULL,
    approved        INTEGER NOT NULL DEFAULT 0,
    status          TEXT    NOT NULL DEFAULT 'pending'
                            CHECK(status IN ('pending','approved','rejected','inactive')),
    stock           INTEGER NOT NULL DEFAULT 1 CHECK(stock >= 0),
    views           INTEGER NOT NULL DEFAULT 0,
    is_auction      INTEGER NOT NULL DEFAULT 0,
    auction_end     TIMESTAMP,
    start_price     REAL    DEFAULT 0,
    current_bid     REAL    DEFAULT 0,
    bid_count       INTEGER DEFAULT 0,
    highest_bidder  TEXT    DEFAULT '',
    highest_bid_uid INTEGER,
    is_live         INTEGER DEFAULT 0,
    watcher_count   INTEGER DEFAULT 0,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS bids (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    user_id    INTEGER NOT NULL REFERENCES users(id)    ON DELETE CASCADE,
    username   TEXT    NOT NULL,
    amount     REAL    NOT NULL CHECK(amount > 0),
    ip_address TEXT    DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS orders (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    buyer_id        INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    buyer_name      TEXT    NOT NULL,
    product_id      INTEGER REFERENCES products(id) ON DELETE SET NULL,
    product_name    TEXT    NOT NULL,
    product_image   TEXT    DEFAULT '',
    amount          REAL    NOT NULL CHECK(amount > 0),
    quantity        INTEGER NOT NULL DEFAULT 1,
    delivery_fee    REAL    NOT NULL DEFAULT 49.0,
    discount        REAL    NOT NULL DEFAULT 0.0,
    total_amount    REAL    NOT NULL DEFAULT 0.0,
    payment_method  TEXT    NOT NULL DEFAULT 'cod'
                            CHECK(payment_method IN ('cod','card','qr','upi','wallet')),
    payment_status  TEXT    NOT NULL DEFAULT 'pending'
                            CHECK(payment_status IN ('pending','paid','failed')),
    status          TEXT    NOT NULL DEFAULT 'Placed'
                            CHECK(status IN ('Placed','Confirmed','Shipped','Delivered','Cancelled')),
    transaction_id  TEXT    DEFAULT '',
    address_id      INTEGER REFERENCES addresses(id) ON DELETE SET NULL,
    address_snapshot TEXT   DEFAULT '',
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS addresses (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id      INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    full_name    TEXT    NOT NULL,
    phone        TEXT    NOT NULL,
    city         TEXT    NOT NULL,
    state        TEXT    NOT NULL,
    pincode      TEXT    NOT NULL,
    landmark     TEXT    DEFAULT '',
    full_address TEXT    NOT NULL,
    is_default   INTEGER DEFAULT 0,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS cart (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    buyer_id   INTEGER NOT NULL REFERENCES users(id)    ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    quantity   INTEGER NOT NULL DEFAULT 1 CHECK(quantity > 0),
    UNIQUE(buyer_id, product_id)
);

CREATE TABLE IF NOT EXISTS wishlist (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    buyer_id   INTEGER NOT NULL REFERENCES users(id)    ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    UNIQUE(buyer_id, product_id)
);

CREATE TABLE IF NOT EXISTS watchers (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER NOT NULL REFERENCES users(id)    ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    UNIQUE(user_id, product_id)
);

CREATE TABLE IF NOT EXISTS notifications (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    message    TEXT    NOT NULL,
    ntype      TEXT    DEFAULT 'info',
    read       INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Wallet transactions: full detail with method and status
CREATE TABLE IF NOT EXISTS wallet_transactions (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    amount      REAL    NOT NULL CHECK(amount > 0),
    type        TEXT    NOT NULL CHECK(type IN ('credit','debit')),
    method      TEXT    NOT NULL DEFAULT 'system',
    status      TEXT    NOT NULL DEFAULT 'success' CHECK(status IN ('success','pending','failed')),
    description TEXT    DEFAULT '',
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS bid_rate_log (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    ip_address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS auction_tokens (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id      INTEGER NOT NULL,
    product_id   INTEGER NOT NULL,
    token        TEXT    UNIQUE NOT NULL,
    issued_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    interacted   INTEGER DEFAULT 0,
    bid_count    INTEGER DEFAULT 0,
    UNIQUE(user_id, product_id)
);

CREATE TABLE IF NOT EXISTS security_log (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER,
    ip_address TEXT,
    action     TEXT,
    detail     TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS blocked_ips (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    ip_address  TEXT UNIQUE NOT NULL,
    reason      TEXT,
    blocked_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at  TIMESTAMP
);

CREATE TABLE IF NOT EXISTS chat_messages (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    user_id    INTEGER,
    username   TEXT    NOT NULL,
    message    TEXT    NOT NULL,
    is_system  INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS messages (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    auction_id  INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    sender_id   INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    receiver_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    message     TEXT    NOT NULL,
    read        INTEGER DEFAULT 0,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS qr_settings (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    qr_image   TEXT DEFAULT '',
    upi_id     TEXT DEFAULT '',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE UNIQUE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_products_seller    ON products(seller_id, approved);
CREATE INDEX IF NOT EXISTS idx_products_category  ON products(category, approved);
CREATE INDEX IF NOT EXISTS idx_products_auction   ON products(is_auction, auction_end);
CREATE INDEX IF NOT EXISTS idx_bids_product       ON bids(product_id);
CREATE INDEX IF NOT EXISTS idx_bids_user          ON bids(user_id);
CREATE INDEX IF NOT EXISTS idx_orders_buyer       ON orders(buyer_id);
CREATE INDEX IF NOT EXISTS idx_cart_buyer         ON cart(buyer_id);
CREATE INDEX IF NOT EXISTS idx_wishlist_buyer     ON wishlist(buyer_id);
CREATE INDEX IF NOT EXISTS idx_notif_user         ON notifications(user_id, read);
CREATE INDEX IF NOT EXISTS idx_sessions_token     ON sessions(token);
CREATE INDEX IF NOT EXISTS idx_rate_log           ON bid_rate_log(user_id, created_at);
CREATE INDEX IF NOT EXISTS idx_addresses_user     ON addresses(user_id);
CREATE INDEX IF NOT EXISTS idx_wallet_user        ON wallet_transactions(user_id, created_at);

-- Seed categories
INSERT OR IGNORE INTO categories (name, icon) VALUES
    ('Electronics',  '[laptop]'),
    ('Accessories',  '[bag]'),
    ('Mens Wear',    '[shirt]'),
    ('Womens Wear',  '[dress]'),
    ('Shoes',        '[shoe]'),
    ('Toys',         '[toy]'),
    ('Home Garden',  '[home]'),
    ('Sports',       '[ball]'),
    ('Books',        '[books]'),
    ('Collectibles', '[vase]');

-- Default QR settings
INSERT OR IGNORE INTO qr_settings (id, qr_image, upi_id) VALUES (1, '', 'quickdealr@upi');

-- Promo codes
CREATE TABLE IF NOT EXISTS promo_codes (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    code          TEXT    UNIQUE NOT NULL,
    discount_type TEXT    NOT NULL DEFAULT 'percentage' CHECK(discount_type IN ('percentage','fixed')),
    value         REAL    NOT NULL CHECK(value > 0),
    min_order     REAL    NOT NULL DEFAULT 0,
    max_uses      INTEGER DEFAULT NULL,
    used_count    INTEGER DEFAULT 0,
    is_active     INTEGER DEFAULT 1,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Wallet top-up requests (approval-based)
CREATE TABLE IF NOT EXISTS wallet_requests (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id        INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    amount         REAL    NOT NULL CHECK(amount > 0),
    method         TEXT    NOT NULL DEFAULT 'card',
    transaction_id TEXT    DEFAULT '',
    card_last4     TEXT    DEFAULT '',
    status         TEXT    NOT NULL DEFAULT 'pending' CHECK(status IN ('pending','approved','rejected')),
    admin_note     TEXT    DEFAULT '',
    reviewed_by    INTEGER REFERENCES users(id),
    reviewed_at    TIMESTAMP,
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Contact messages
CREATE TABLE IF NOT EXISTS contact_messages (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT    NOT NULL,
    email      TEXT    NOT NULL,
    subject    TEXT    DEFAULT '',
    message    TEXT    NOT NULL,
    is_resolved INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Seed demo promo codes
INSERT OR IGNORE INTO promo_codes (code, discount_type, value, min_order, is_active)
VALUES
    ('WELCOME10', 'percentage', 10, 0,    1),
    ('SAVE50',    'fixed',      50, 500,  1),
    ('DEAL20',    'percentage', 20, 1000, 1);

CREATE INDEX IF NOT EXISTS idx_wallet_req_user   ON wallet_requests(user_id, status);
CREATE INDEX IF NOT EXISTS idx_wallet_req_status ON wallet_requests(status, created_at);
CREATE INDEX IF NOT EXISTS idx_promo_code        ON promo_codes(code);

-- Auction winner/payment tracking
CREATE TABLE IF NOT EXISTS auction_winners (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id      INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    winner_user_id  INTEGER NOT NULL REFERENCES users(id),
    winner_username TEXT    NOT NULL,
    bid_amount      REAL    NOT NULL,
    rank            INTEGER NOT NULL DEFAULT 1,  -- 1=primary, 2=fallback, etc.
    status          TEXT    NOT NULL DEFAULT 'pending_payment'
                            CHECK(status IN ('pending_payment','paid','failed','skipped')),
    payment_deadline TIMESTAMP,
    paid_at         TIMESTAMP,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add payment deadline to products

-- v7 Enhancement: Whitelist support & uploaded files tracking
-- Run these manually if upgrading an existing database:
-- ALTER TABLE users ADD COLUMN is_whitelisted INTEGER NOT NULL DEFAULT 0;
-- CREATE TABLE IF NOT EXISTS uploaded_files (
--   id INTEGER PRIMARY KEY AUTOINCREMENT,
--   user_id INTEGER NOT NULL,
--   original_name TEXT NOT NULL,
--   file_path TEXT NOT NULL,
--   size_bytes INTEGER DEFAULT 0,
--   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
-- );
