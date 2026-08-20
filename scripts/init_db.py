#!/usr/bin/env python3
"""Create Penny's local ledger mirror.

QuickBooks and Xero remain the system of record. This database is Penny's
working memory: what she has already seen, what she proposed, what the owner
answered, and which receipts are already booked.

Its main job is preventing double-booking -- the same charge arriving once from
a receipt photo and again from the bank feed.

Safe to re-run: every statement is CREATE ... IF NOT EXISTS.
"""
import sqlite3
import sys
from pathlib import Path

DB = Path(__file__).resolve().parent.parent / "ledger.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS transactions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    external_id     TEXT UNIQUE,           -- QBO/Xero transaction id
    external_type   TEXT,                  -- Purchase | Deposit | Transfer | BankTransaction
    txn_date        TEXT NOT NULL,
    vendor          TEXT COLLATE NOCASE,
    description     TEXT,
    amount          REAL NOT NULL,
    account_id      TEXT,                  -- account it currently sits in
    account_name    TEXT,
    status          TEXT NOT NULL DEFAULT 'uncategorized',
                    -- uncategorized | proposed | approved | posted | asked | skipped
    confidence      TEXT,                  -- high | medium | low | none
    matched_rule    TEXT,                  -- which rule produced the proposal
    proposed_account_id   TEXT,
    proposed_account_name TEXT,
    has_receipt     INTEGER NOT NULL DEFAULT 0,
    sync_token      TEXT,                  -- QBO optimistic-concurrency token
    first_seen_at   TEXT NOT NULL DEFAULT (datetime('now')),
    posted_at       TEXT,
    notes           TEXT
);

CREATE TABLE IF NOT EXISTS receipts (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    local_path      TEXT NOT NULL,
    source          TEXT,                  -- telegram | email | file
    vendor          TEXT COLLATE NOCASE,
    receipt_date    TEXT,
    amount          REAL,
    tax             REAL,
    last4           TEXT,
    transaction_id  INTEGER REFERENCES transactions(id) ON DELETE SET NULL,
    external_attachment_id TEXT,           -- QBO Attachable id, once linked
    attached        INTEGER NOT NULL DEFAULT 0,
    received_at     TEXT NOT NULL DEFAULT (datetime('now')),
    raw_text        TEXT
);

CREATE TABLE IF NOT EXISTS questions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id  INTEGER REFERENCES transactions(id) ON DELETE CASCADE,
    asked_at        TEXT NOT NULL DEFAULT (datetime('now')),
    question        TEXT NOT NULL,
    answer          TEXT,
    answered_at     TEXT,
    became_rule     INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS rule_hits (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_name    TEXT NOT NULL,
    transaction_id INTEGER REFERENCES transactions(id) ON DELETE CASCADE,
    outcome      TEXT NOT NULL,   -- accepted | corrected | rejected
    hit_at       TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS anomalies (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id INTEGER REFERENCES transactions(id) ON DELETE CASCADE,
    kind           TEXT NOT NULL,   -- duplicate | out_of_range | cancelled_sub | personal | new_vendor
    detail         TEXT,
    flagged_at     TEXT NOT NULL DEFAULT (datetime('now')),
    -- flagged once, never nagged again
    acknowledged   INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_txn_status     ON transactions(status);
CREATE INDEX IF NOT EXISTS idx_txn_vendor     ON transactions(vendor);
CREATE INDEX IF NOT EXISTS idx_txn_date       ON transactions(txn_date);
CREATE INDEX IF NOT EXISTS idx_txn_external   ON transactions(external_id);
-- The duplicate-detection index: vendor + amount + date is how a receipt photo
-- gets matched to the bank-feed line for the same charge.
CREATE INDEX IF NOT EXISTS idx_txn_dedupe     ON transactions(vendor, amount, txn_date);
CREATE INDEX IF NOT EXISTS idx_receipts_txn   ON receipts(transaction_id);
CREATE INDEX IF NOT EXISTS idx_questions_open ON questions(answered_at);

-- Keep has_receipt honest without the agent having to remember.
CREATE TRIGGER IF NOT EXISTS trg_receipt_attached
AFTER UPDATE OF transaction_id ON receipts
FOR EACH ROW WHEN NEW.transaction_id IS NOT NULL
BEGIN
    UPDATE transactions SET has_receipt = 1 WHERE id = NEW.transaction_id;
END;
"""


def main() -> int:
    conn = sqlite3.connect(DB)
    try:
        conn.executescript(SCHEMA)
        conn.commit()
        tables = [
            r[0]
            for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            )
        ]
    finally:
        conn.close()
    print(f"Penny's ledger mirror ready: {DB}")
    print(f"Tables: {', '.join(tables)}")
    print("\nQuickBooks/Xero stay the system of record. This is Penny's working memory.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
