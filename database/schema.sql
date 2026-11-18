CREATE TABLE IF NOT EXISTS inventory_items (
    item_id INTEGER PRIMARY KEY AUTOINCREMENT,

    product_name TEXT NOT NULL,
    barcode TEXT,
    category TEXT,

    quantity REAL NOT NULL DEFAULT 1,
    unit TEXT,

    purchase_date TEXT,
    expiration_date TEXT,

    date_confirmed INTEGER NOT NULL DEFAULT 0
        CHECK (date_confirmed IN (0, 1)),

    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS scan_candidates (
    scan_id INTEGER PRIMARY KEY AUTOINCREMENT,

    product_name TEXT,
    barcode TEXT,

    image_path TEXT,
    raw_ocr_text TEXT NOT NULL,

    candidate_date TEXT,
    confidence REAL
        CHECK (confidence IS NULL OR confidence BETWEEN 0 AND 1),

    status TEXT NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'accepted', 'rejected')),

    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS inventory_events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,

    item_id INTEGER,

    action TEXT NOT NULL
        CHECK (action IN (
            'created',
            'quantity_updated',
            'date_updated',
            'deleted'
        )),

    quantity_changed REAL,

    timestamp TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (item_id)
        REFERENCES inventory_items(item_id)
        ON DELETE SET NULL
);