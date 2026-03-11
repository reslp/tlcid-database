#!/usr/bin/env python3
"""Build `tlcid_database.db` from `chemical_data.csv` and lichen-substance links."""

from __future__ import annotations

import argparse
import csv
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


SUBSTANCES_SCHEMA_SQL = """
CREATE TABLE Substances (
    name TEXT(100) PRIMARY KEY,
    A INTEGER,
    B INTEGER,
    Bprime INTEGER,
    C INTEGER,
    E INTEGER,
    F INTEGER,
    G INTEGER,
    HPLC INTEGER,
    BefVis TEXT(2),
    BefUVS TEXT(2),
    BefUVL TEXT(20),
    Archers TEXT(20),
    AftVis TEXT(20),
    AftUV TEXT(20),
    M INTEGER,
    F1 INTEGER,
    F2 INTEGER,
    F3 INTEGER,
    KResult TEXT(20),
    CResult TEXT(20),
    KCResult TEXT(20),
    PDResult TEXT(20),
    Cortex TEXT(20),
    Medulla TEXT(20),
    Notes TEXT,
    Reference TEXT,
    Related TEXT,
    Lichens TEXT,
    Synonyms TEXT,
    Path TEXT,
    GroupName TEXT,
    Class TEXT,
    GLossID TEXT DEFAULT NULL
);
"""

LICHENS_SCHEMA_SQL = """
CREATE TABLE Lichens (
    Lichen TEXT NOT NULL DEFAULT '',
    Substance TEXT NOT NULL DEFAULT '',
    Genus TEXT NOT NULL DEFAULT ''
);
"""

METADATA_SCHEMA_SQL = """
CREATE TABLE metadata (
    table_name TEXT PRIMARY KEY,
    row_count INTEGER NOT NULL,
    created_at TEXT NOT NULL
);
"""

RF_INTEGER_COLUMNS = ["A", "B", "Bprime", "C", "E", "F", "G", "HPLC", "M", "F1", "F2", "F3"]
TEXT_COLUMNS = [
    "BefVis",
    "BefUVS",
    "BefUVL",
    "Archers",
    "AftVis",
    "AftUV",
    "KResult",
    "CResult",
    "KCResult",
    "PDResult",
    "Cortex",
    "Medulla",
    "Notes",
    "Reference",
    "Related",
    "Lichens",
    "Synonyms",
    "Path",
    "GroupName",
    "Class",
    "GLossID",
]


def parse_int(value: str) -> int | None:
    raw = (value or "").strip()
    if not raw:
        return None
    try:
        return int(raw)
    except ValueError:
        return None


def clean_text(value: str) -> str | None:
    text = (value or "").strip()
    return text or None


def normalize_substance_name(name: str) -> str:
    return " ".join((name or "").strip().lower().split())


def extract_genus(species_name: str) -> str:
    parts = (species_name or "").strip().split()
    return parts[0] if parts else ""


def iter_split_substances(substances_field: str) -> Iterable[str]:
    for part in (substances_field or "").split(","):
        cleaned = normalize_substance_name(part)
        if cleaned:
            yield cleaned


def read_substances_rows(substances_csv: Path) -> list[tuple]:
    rows: list[tuple] = []
    with substances_csv.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = normalize_substance_name(row.get("name", ""))
            if not name:
                continue

            int_values = {column: parse_int(row.get(column, "")) for column in RF_INTEGER_COLUMNS}
            text_values = {column: clean_text(row.get(column, "")) for column in TEXT_COLUMNS}

            rows.append(
                (
                    name,
                    int_values["A"],
                    int_values["B"],
                    int_values["Bprime"],
                    int_values["C"],
                    int_values["E"],
                    int_values["F"],
                    int_values["G"],
                    int_values["HPLC"],
                    text_values["BefVis"],
                    text_values["BefUVS"],
                    text_values["BefUVL"],
                    text_values["Archers"],
                    text_values["AftVis"],
                    text_values["AftUV"],
                    int_values["M"],
                    int_values["F1"],
                    int_values["F2"],
                    int_values["F3"],
                    text_values["KResult"],
                    text_values["CResult"],
                    text_values["KCResult"],
                    text_values["PDResult"],
                    text_values["Cortex"],
                    text_values["Medulla"],
                    text_values["Notes"],
                    text_values["Reference"],
                    text_values["Related"],
                    text_values["Lichens"],
                    text_values["Synonyms"],
                    text_values["Path"],
                    text_values["GroupName"],
                    text_values["Class"],
                    text_values["GLossID"],
                )
            )
    return rows


def build_database(substances_csv: Path, lichens_csv: Path, out_db: Path) -> tuple[int, int]:
    if out_db.exists():
        out_db.unlink()

    con = sqlite3.connect(out_db)
    try:
        cur = con.cursor()
        cur.execute(SUBSTANCES_SCHEMA_SQL)
        cur.execute(LICHENS_SCHEMA_SQL)
        cur.execute(METADATA_SCHEMA_SQL)

        cur.executemany(
            """
            INSERT OR REPLACE INTO Substances (
                name, A, B, Bprime, C, E, F, G, HPLC,
                BefVis, BefUVS, BefUVL, Archers, AftVis, AftUV,
                M, F1, F2, F3,
                KResult, CResult, KCResult, PDResult,
                Cortex, Medulla, Notes, Reference, Related, Lichens, Synonyms, Path,
                GroupName, Class, GLossID
            ) VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?,
                ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?, ?, ?,
                ?, ?, ?
            )
            """,
            read_substances_rows(substances_csv),
        )

        lichen_rows = set()
        with lichens_csv.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f, delimiter=";")
            for row in reader:
                species = " ".join((row.get("species", "") or "").strip().split())
                if not species:
                    continue
                genus = extract_genus(species)
                for substance in iter_split_substances(row.get("substances", "")):
                    lichen_rows.add((species, substance, genus))

        cur.executemany(
            "INSERT INTO Lichens (Lichen, Substance, Genus) VALUES (?, ?, ?)",
            sorted(lichen_rows),
        )

        cur.execute('CREATE UNIQUE INDEX "Name" ON Substances(name)')
        cur.execute('CREATE INDEX "LichenIndex" ON Lichens(Lichen)')
        cur.execute('CREATE INDEX "Genus Index" ON Lichens(Genus)')

        con.commit()

        cur.execute("SELECT COUNT(*) FROM Substances")
        substances_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM Lichens")
        lichens_count = cur.fetchone()[0]

        created_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        cur.executemany(
            "INSERT INTO metadata (table_name, row_count, created_at) VALUES (?, ?, ?)",
            [
                ("Substances", substances_count, created_at),
                ("Lichens", lichens_count, created_at),
            ],
        )

        con.commit()

        return substances_count, lichens_count
    finally:
        con.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Build tlcid SQLite database")
    parser.add_argument(
        "--substances",
        default="chemical_data.csv",
        help="Input CSV with chemical/substance data",
    )
    parser.add_argument(
        "--lichen-links",
        default="lichen_substance_data.csv",
        help="Input lichen-substance mapping CSV (';' separated)",
    )
    parser.add_argument(
        "--output",
        default="tlcid_database.db",
        help="Output SQLite database path",
    )
    args = parser.parse_args()

    out_db = Path(args.output)
    substances_count, lichens_count = build_database(
        Path(args.substances),
        Path(args.lichen_links),
        out_db,
    )

    print(f"Created {out_db}")
    print(f"Substances rows: {substances_count}")
    print(f"Lichens rows: {lichens_count}")


if __name__ == "__main__":
    main()
