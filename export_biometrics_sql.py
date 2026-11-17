import sqlite3
import json
import os
import sys

# Tambahkan root path
sys.path.insert(0, os.path.dirname(__file__))

from app.database import Base
from app import models
from sqlalchemy.schema import CreateTable
from sqlalchemy.dialects import mysql

sql_file_path = os.path.join(os.path.dirname(__file__), "..", "database_biometrics_citra.sql")

with open(sql_file_path, "w", encoding="utf-8") as f:
    f.write("-- =========================================================\n")
    f.write("-- BisaGym - Database Biometrik & Pengenalan Citra Wajah (AI)\n")
    f.write("-- Untuk diimport ke phpMyAdmin Niagahoster\n")
    f.write("-- =========================================================\n\n")
    f.write("SET FOREIGN_KEY_CHECKS = 0;\n\n")

    # 1. Tulis Schema (CREATE TABLE)
    for table in Base.metadata.sorted_tables:
        ddl = str(CreateTable(table).compile(dialect=mysql.dialect())).strip()
        # Ubah CREATE TABLE menjadi CREATE TABLE IF NOT EXISTS
        ddl = ddl.replace("CREATE TABLE", "CREATE TABLE IF NOT EXISTS", 1)
        f.write(ddl + ";\n\n")

    # 2. Tulis Data dari gym.db (INSERT INTO)
    db_path = os.path.join(os.path.dirname(__file__), "gym.db")
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        tables_to_dump = [
            "branches",
            "users",
            "membership_plans",
            "members",
            "memberships",
            "biometric_consents",
            "devices",
            "enrollment_sessions",
            "face_profiles",
            "face_enrollment_samples",
            "system_settings",
            "checkin_attempts",
            "access_events",
            "audit_logs",
            "auth_sessions",
            "kiosk_sessions",
        ]

        for t in tables_to_dump:
            try:
                rows = cur.execute(f"SELECT * FROM {t}").fetchall()
            except Exception:
                continue

            if not rows:
                continue

            cols = list(rows[0].keys())
            col_list = ", ".join([f"`{c}`" for c in cols])
            f.write(f"-- Data untuk tabel `{t}` ({len(rows)} baris)\n")
            
            for row in rows:
                vals = []
                for c in cols:
                    val = row[c]
                    if val is None:
                        vals.append("NULL")
                    elif isinstance(val, (int, float)):
                        vals.append(str(val))
                    else:
                        escaped = str(val).replace("\\", "\\\\").replace("'", "''")
                        vals.append(f"'{escaped}'")
                val_str = ", ".join(vals)
                f.write(f"INSERT INTO `{t}` ({col_list}) VALUES ({val_str});\n")
            f.write("\n")

        conn.close()

    f.write("SET FOREIGN_KEY_CHECKS = 1;\n")

print(f"Berhasil dibuat: {sql_file_path} ({os.path.getsize(sql_file_path)} bytes)")
