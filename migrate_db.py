import json
import sqlite3
import pymysql

print("Memulai migrasi dari SQLite (gym.db) ke MySQL (bisagym_biometrics)...")

sqlite_conn = sqlite3.connect("gym.db")
sqlite_conn.row_factory = sqlite3.Row
sqlite_cur = sqlite_conn.cursor()

mysql_conn = pymysql.connect(
    host="127.0.0.1",
    port=3306,
    user="root",
    password="",
    database="bisagym_biometrics",
    charset="utf8mb4",
    cursorclass=pymysql.cursors.DictCursor
)
mysql_cur = mysql_conn.cursor()

# Matikan foreign key check sementara agar urutan insert aman
mysql_cur.execute("SET FOREIGN_KEY_CHECKS = 0;")

tables = [
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

for table in tables:
    try:
        rows = sqlite_cur.execute(f"SELECT * FROM {table}").fetchall()
    except sqlite3.OperationalError:
        continue

    if not rows:
        print(f"- {table}: 0 baris (dilewati)")
        continue

    # Kosongkan tabel tujuan di MySQL dulu jika ada
    mysql_cur.execute(f"TRUNCATE TABLE {table};")

    cols = list(rows[0].keys())
    placeholders = ", ".join(["%s"] * len(cols))
    col_names = ", ".join([f"`{c}`" for c in cols])
    sql = f"INSERT INTO `{table}` ({col_names}) VALUES ({placeholders})"

    count = 0
    for row in rows:
        vals = []
        for c in cols:
            val = row[c]
            # Kolom JSON di sqlite disimpan sebagai string JSON, di MySQL bisa langsung string JSON
            vals.append(val)
        mysql_cur.execute(sql, vals)
        count += 1

    print(f"✓ {table}: berhasil memindahkan {count} baris")

mysql_cur.execute("SET FOREIGN_KEY_CHECKS = 1;")
mysql_conn.commit()

sqlite_conn.close()
mysql_conn.close()

print("\nMigrasi selesai dengan sukses!")

