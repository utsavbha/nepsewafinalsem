#!/usr/bin/env python3
"""
Load GPS-enabled sample providers into MySQL.

  python3 seed_providers.py           # insert 120 if table is empty; otherwise print hint
  python3 seed_providers.py replace  # DELETE all providers, then insert 120 (fresh seed)
  python3 seed_providers.py append    # add another 120 (new phones / names)

Uses DB settings from mysql_config / DB_* env (same as main.py).
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import (  # noqa: E402
    SAMPLE_SERVICE_CATEGORIES,
    generate_seed_providers,
    get_db,
    init_db,
)

_INSERT_SQL = """
    INSERT INTO service_providers
    (name, service, service_key, location, district, latitude, longitude,
     rating, experience, completed_jobs, cancellation_rate, response_time_hours,
     is_verified, review_count, image, phone, availability)
    VALUES (%(name)s, %(service)s, %(service_key)s, %(location)s, %(district)s,
            %(latitude)s, %(longitude)s, %(rating)s, %(experience)s, %(completed_jobs)s,
            %(cancellation_rate)s, %(response_time_hours)s, %(is_verified)s,
            %(review_count)s, %(image)s, %(phone)s, %(availability)s)
"""


def _insert_rows(cur, rows):
    for p in rows:
        cur.execute(_INSERT_SQL, p)


def cmd_replace():
    rows = generate_seed_providers(12)
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM service_providers")
            _insert_rows(cur, rows)
        conn.commit()
    finally:
        conn.close()
    print(f"Replaced with {len(rows)} providers ({len(SAMPLE_SERVICE_CATEGORIES)} × 12), all with GPS.")


def cmd_append():
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COALESCE(MAX(id), 0) AS max_id FROM service_providers")
            max_id = int(cur.fetchone()["max_id"])
            name_start = max_id + 50
            phone_start = 9812000000 + (max_id % 10000)
            rows = generate_seed_providers(12, name_start=name_start, phone_start=phone_start)
            _insert_rows(cur, rows)
        conn.commit()
    finally:
        conn.close()
    print(f"Appended {len(rows)} providers with GPS.")


def cmd_init_if_empty():
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS c FROM service_providers")
            n = int(cur.fetchone()["c"])
        if n > 0:
            print(
                f"Table already has {n} row(s). Run one of:\n"
                "  python3 seed_providers.py replace   # wipe + 120 GPS providers\n"
                "  python3 seed_providers.py append  # add 120 more\n"
            )
            return
    finally:
        conn.close()

    init_db()
    print("Database was empty: ran init_db() + sample insert (120 GPS providers if schema was new).")


def main():
    p = argparse.ArgumentParser(description="Seed NepSewa providers with GPS coordinates.")
    p.add_argument(
        "action",
        nargs="?",
        choices=("replace", "append"),
        default=None,
        help="replace = delete all then insert 120; append = add 120 more",
    )
    args = p.parse_args()

    if args.action == "replace":
        cmd_replace()
    elif args.action == "append":
        cmd_append()
    else:
        cmd_init_if_empty()


if __name__ == "__main__":
    main()
