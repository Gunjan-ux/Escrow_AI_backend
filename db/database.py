import json
import logging
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Iterator, Optional

from config import DB_PATH
from schemas import Deed, ExtractedFields, Rule

logger = logging.getLogger(__name__)


@contextmanager
def _conn() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    logger.info("[db] Initializing SQLite at %s", DB_PATH)
    with _conn() as c:
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS deeds (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_hash TEXT NOT NULL UNIQUE,
                raw_text TEXT NOT NULL,
                extracted_fields TEXT NOT NULL,
                rules TEXT NOT NULL,
                model_version TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )


def save_deed(
    *,
    file_hash: str,
    raw_text: str,
    fields: ExtractedFields,
    rules: list[Rule],
    model_version: str,
) -> int:
    payload = (
        file_hash,
        raw_text,
        fields.model_dump_json(),
        json.dumps([r.model_dump() for r in rules]),
        model_version,
        datetime.now(timezone.utc).isoformat(),
    )
    with _conn() as c:
        cur = c.execute(
            "INSERT INTO deeds (file_hash, raw_text, extracted_fields, rules, model_version, created_at)"
            " VALUES (?, ?, ?, ?, ?, ?)",
            payload,
        )
        deed_id = cur.lastrowid
    logger.info("[db] Saved deed_id=%s hash=%s rules=%d", deed_id, file_hash[:12], len(rules))
    return deed_id


def get_deed_by_hash(file_hash: str) -> Optional[Deed]:
    with _conn() as c:
        row = c.execute("SELECT * FROM deeds WHERE file_hash = ?", (file_hash,)).fetchone()
    return _row_to_deed(row) if row else None


def get_deed_by_id(deed_id: int) -> Optional[Deed]:
    with _conn() as c:
        row = c.execute("SELECT * FROM deeds WHERE id = ?", (deed_id,)).fetchone()
    return _row_to_deed(row) if row else None


def _row_to_deed(row: sqlite3.Row) -> Deed:
    return Deed(
        id=row["id"],
        file_hash=row["file_hash"],
        raw_text=row["raw_text"],
        extracted_fields=ExtractedFields.model_validate_json(row["extracted_fields"]),
        rules=[Rule.model_validate(r) for r in json.loads(row["rules"])],
        model_version=row["model_version"],
        created_at=row["created_at"],
    )
