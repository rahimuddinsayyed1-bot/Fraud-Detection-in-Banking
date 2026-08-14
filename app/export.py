from flask import Blueprint
from flask import send_file
from flask import session
from flask import redirect

import csv
import sqlite3
import os

export = Blueprint(
    "export",
    __name__
)

BASE_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        ".."
    )
)

DB = os.path.join(
    BASE_DIR,
    "database",
    "fraud.db"
)

REPORT_FOLDER = os.path.join(
    BASE_DIR,
    "reports"
)

os.makedirs(
    REPORT_FOLDER,
    exist_ok=True
)


@export.route("/export/csv")
def export_csv():

    if "user" not in session:
        return redirect("/login")

    user_email = session["user"].strip().lower()

    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""
    SELECT
    customer_name,
    account_number,
    amount,
    hour,
    device,
    city,
    risk,
    status,
    reason,
    created_at
    FROM transactions
    WHERE LOWER(email)=?
    ORDER BY id DESC
    """, (user_email,))

    rows = cur.fetchall()
    conn.close()

    file_path = os.path.join(
        REPORT_FOLDER,
        "transactions.csv"
    )

    with open(
        file_path,
        "w",
        newline="",
        encoding="utf-8"
    ) as f:
        writer = csv.writer(f)
        writer.writerow([
            "Customer",
            "Account",
            "Amount",
            "Hour",
            "Device",
            "Location",
            "Risk",
            "Status",
            "Reason",
            "Date"
        ])
        writer.writerows(rows)

    return send_file(
        file_path,
        as_attachment=True
    )


@export.route("/export/pdf")
def export_pdf():

    if "user" not in session:
        return redirect("/login")

    user_email = session["user"].strip().lower()

    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""
    SELECT
    customer_name,
    account_number,
    amount,
    hour,
    device,
    city,
    risk,
    status,
    reason,
    created_at
    FROM transactions
    WHERE LOWER(email)=?
    ORDER BY id DESC
    """, (user_email,))

    rows = cur.fetchall()
    conn.close()

    file_path = os.path.join(
        REPORT_FOLDER,
        "transactions_report.txt"
    )

    with open(file_path, "w", encoding="utf-8") as f:
        f.write("=========================================\n")
        f.write("  FRAUD DETECTION SYSTEM - USER REPORT   \n")
        f.write("=========================================\n\n")
        f.write(f"Account Email: {user_email}\n")
        f.write(f"Total Transactions: {len(rows)}\n\n")
        f.write("-----------------------------------------\n")

        for idx, row in enumerate(rows, 1):
            f.write(f"Transaction #{idx}\n")
            f.write(f"  Customer: {row[0]}\n")
            f.write(f"  Account: {row[1]}\n")
            f.write(f"  Amount: ${row[2]}\n")
            f.write(f"  Hour: {row[3]}:00\n")
            f.write(f"  Device: {row[4]}\n")
            f.write(f"  Location: {row[5]}\n")
            f.write(f"  Risk: {row[6]}%\n")
            f.write(f"  Status: {row[7]}\n")
            f.write(f"  Reason: {row[8]}\n")
            f.write(f"  Date: {row[9]}\n")
            f.write("-----------------------------------------\n")

    return send_file(
        file_path,
        as_attachment=True,
        download_name="fraud_report.txt"
    )