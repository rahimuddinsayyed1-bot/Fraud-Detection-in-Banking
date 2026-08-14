import sqlite3
from pathlib import Path
from werkzeug.security import generate_password_hash, check_password_hash

# -------------------------------------------------
# Database Location
# -------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_DIR = BASE_DIR / "database"

DATABASE_DIR.mkdir(exist_ok=True)

DB = DATABASE_DIR / "fraud.db"


# -------------------------------------------------
# Database Connection
# -------------------------------------------------

def connect():

    conn = sqlite3.connect(DB)

    conn.row_factory = sqlite3.Row

    return conn


# -------------------------------------------------
# Create Tables
# -------------------------------------------------

def create_tables():

    conn = connect()

    cur = conn.cursor()

    # ---------------- Users ----------------

    cur.execute("""

    CREATE TABLE IF NOT EXISTS users(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        full_name TEXT NOT NULL,

        email TEXT UNIQUE NOT NULL,

        password TEXT NOT NULL,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

    )

    """)

    # ------------- Transactions -------------

    cur.execute("""

    CREATE TABLE IF NOT EXISTS transactions(

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    email TEXT,

    customer_name TEXT,

    account_number TEXT,

    amount REAL,

    hour INTEGER,

    device TEXT,

    city TEXT,

    risk REAL,

    status TEXT,

    reason TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

)

""")

    cur.execute("PRAGMA table_info(transactions)")

    existing_cols = [row[1] for row in cur.fetchall()]

    required_cols = {
        "email": "TEXT",
        "customer_name": "TEXT",
        "account_number": "TEXT",
        "amount": "REAL",
        "hour": "INTEGER",
        "device": "TEXT",
        "city": "TEXT",
        "risk": "REAL",
        "status": "TEXT",
        "reason": "TEXT"
    }

    for col_name, col_type in required_cols.items():
        if col_name not in existing_cols:
            try:
                cur.execute(f"ALTER TABLE transactions ADD COLUMN {col_name} {col_type}")
            except sqlite3.OperationalError:
                pass

    conn.commit()

    conn.close()



# -------------------------------------------------
# USER FUNCTIONS
# -------------------------------------------------

def register_user(

    full_name,

    email,

    password

):

    conn = connect()

    cur = conn.cursor()

    try:

        email = email.strip().lower()

        hashed = generate_password_hash(password)

        cur.execute(

        """

        INSERT INTO users(

        full_name,

        email,

        password

        )

        VALUES(

        ?,?,?

        )

        """,

        (

        full_name,

        email,

        hashed

        )

        )

        conn.commit()

        return True

    except sqlite3.IntegrityError:

        return False

    finally:

        conn.close()


# -------------------------------------------------

def login_user(

    email,

    password

):

    email = email.strip().lower()

    conn = connect()

    cur = conn.cursor()

    cur.execute(

    """

    SELECT *

    FROM users

    WHERE LOWER(email)=?

    """,

    (email,)

    )

    user = cur.fetchone()

    conn.close()

    if user:

        if check_password_hash(

        user["password"],

        password

        ):

            return user

    return None


# -------------------------------------------------

def get_user(

email

):

    if not email:

        return None

    email = email.strip().lower()

    conn = connect()

    cur = conn.cursor()

    cur.execute(

    """

    SELECT *

    FROM users

    WHERE LOWER(email)=?

    """,

    (email,)

    )

    user = cur.fetchone()

    conn.close()

    return user


# -------------------------------------------------
# TRANSACTION FUNCTIONS
# -------------------------------------------------

def save_transaction(

email,
customer_name,
account_number,
amount,
hour,
device,
city,
risk,
status,
reason

):

    if email:

        email = email.strip().lower()

    conn = connect()

    cur = conn.cursor()

    cur.execute(

    """

    INSERT INTO transactions(

    email,

    customer_name,

    account_number,

    amount,

    hour,

    device,

    city,

    risk,

    status,

    reason

    )

    VALUES(

    ?,?,?,?,?,?,?,?,?,?

    )

    """,

    (

    email,

    customer_name,

    account_number,

    amount,

    hour,

    device,

    city,

    risk,

    status,

    reason

    )

    )

    conn.commit()

    conn.close()


# -------------------------------------------------

def seed_user_transactions(email):
    sample_data = [
        ("Mumbai", "Rajesh Sharma", "ACC-1001", 12500.00, 2, "Unknown", 88.5, "🚨 HIGH RISK", "Unusually high volume, Anomalous late-night window, Unrecognized hardware signature"),
        ("Mumbai", "Sunita Rao", "ACC-1002", 450.00, 14, "Known", 12.0, "✅ APPROVED", "Nominal behavior"),
        ("Delhi", "Amitabh Verma", "ACC-1003", 8200.00, 3, "Unknown", 84.0, "🚨 HIGH RISK", "Unusually high volume, Anomalous late-night window"),
        ("Delhi", "Priya Singh", "ACC-1004", 120.00, 11, "Known", 8.5, "✅ APPROVED", "Nominal behavior"),
        ("Bangalore", "Vikram Patel", "ACC-1005", 15400.00, 1, "Unknown", 92.0, "🚨 HIGH RISK", "Unusually high volume, Anomalous late-night window"),
        ("Bangalore", "Ananya Hegde", "ACC-1006", 680.00, 16, "Known", 15.0, "✅ APPROVED", "Nominal behavior"),
        ("Hyderabad", "Karthik Reddy", "ACC-1007", 9800.00, 4, "Unknown", 86.5, "🚨 HIGH RISK", "Unusually high volume, Anomalous late-night window"),
        ("Hyderabad", "Lakshmi Prasanna", "ACC-1008", 340.00, 10, "Known", 11.0, "✅ APPROVED", "Nominal behavior"),
        ("Chennai", "Srinivasan Iyer", "ACC-1009", 6500.00, 23, "Unknown", 78.0, "🚨 HIGH RISK", "Unusually high volume"),
        ("Chennai", "Meenakshi Sundaram", "ACC-1010", 210.00, 12, "Known", 9.0, "✅ APPROVED", "Nominal behavior"),
        ("Kolkata", "Subhash Ganguly", "ACC-1011", 4900.00, 2, "Unknown", 72.5, "🚨 HIGH RISK", "Anomalous late-night window"),
        ("Kolkata", "Debjani Roy", "ACC-1012", 180.00, 15, "Known", 7.0, "✅ APPROVED", "Nominal behavior"),
        ("Pune", "Deshmukh Kulkarni", "ACC-1013", 11200.00, 4, "Unknown", 89.0, "🚨 HIGH RISK", "Unusually high volume, Anomalous late-night window"),
        ("Pune", "Sneha Joshi", "ACC-1014", 520.00, 18, "Known", 14.0, "✅ APPROVED", "Nominal behavior"),
        ("Ahmedabad", "Hardik Shah", "ACC-1015", 7400.00, 1, "Unknown", 81.0, "🚨 HIGH RISK", "Unusually high volume"),
        ("Ahmedabad", "Bhakti Mehta", "ACC-1016", 290.00, 13, "Known", 10.0, "✅ APPROVED", "Nominal behavior"),
        ("Jaipur", "Rathore Chauhan", "ACC-1017", 5100.00, 3, "Unknown", 74.0, "🚨 HIGH RISK", "Anomalous late-night window"),
        ("Jaipur", "Kavita Kanwar", "ACC-1018", 150.00, 17, "Known", 6.5, "✅ APPROVED", "Nominal behavior"),
        ("Surat", "Ghanshyam Patel", "ACC-1019", 13600.00, 2, "Unknown", 90.5, "🚨 HIGH RISK", "Unusually high volume"),
        ("Surat", "Bhavna Vora", "ACC-1020", 410.00, 14, "Known", 13.0, "✅ APPROVED", "Nominal behavior"),
        ("Lucknow", "Alok Srivastava", "ACC-1021", 3800.00, 5, "Unknown", 68.0, "🚨 HIGH RISK", "Anomalous late-night window"),
        ("Lucknow", "Zainab Fatima", "ACC-1022", 190.00, 9, "Known", 8.0, "✅ APPROVED", "Nominal behavior"),
        ("Chandigarh", "Gurpreet Singh", "ACC-1023", 6900.00, 4, "Unknown", 79.5, "🚨 HIGH RISK", "Anomalous late-night window"),
        ("Chandigarh", "Simran Kaur", "ACC-1024", 310.00, 19, "Known", 11.5, "✅ APPROVED", "Nominal behavior"),
        ("Noida", "Deepak Gupta", "ACC-1025", 14200.00, 2, "Unknown", 91.0, "🚨 HIGH RISK", "Unusually high volume"),
        ("Noida", "Neha Agarwal", "ACC-1026", 890.00, 11, "Known", 42.0, "⚠️ SUSPICIOUS", "Standard heuristic trigger"),
        ("Gurgaon", "Manish Malhotra", "ACC-1027", 18500.00, 3, "Unknown", 95.0, "🚨 HIGH RISK", "Unusually high volume"),
        ("Gurgaon", "Ritu Kapur", "ACC-1028", 1250.00, 15, "Known", 48.0, "⚠️ SUSPICIOUS", "Standard heuristic trigger"),
        ("Kochi", "Thomas Kurian", "ACC-1029", 5600.00, 1, "Unknown", 75.0, "🚨 HIGH RISK", "Anomalous late-night window"),
        ("Kochi", "Anitha Menon", "ACC-1030", 270.00, 10, "Known", 9.5, "✅ APPROVED", "Nominal behavior"),
        ("Indore", "Varun Chhabra", "ACC-1031", 4200.00, 4, "Unknown", 70.0, "🚨 HIGH RISK", "Anomalous late-night window"),
        ("Indore", "Shweta Tiwari", "ACC-1032", 160.00, 16, "Known", 7.5, "✅ APPROVED", "Nominal behavior"),
        ("Bhopal", "Pradeep Saxena", "ACC-1033", 3500.00, 2, "Unknown", 66.0, "🚨 HIGH RISK", "Anomalous late-night window"),
        ("Bhopal", "Rashmi Mishra", "ACC-1034", 140.00, 12, "Known", 6.0, "✅ APPROVED", "Nominal behavior"),
        ("Nagpur", "Chetan Deshpande", "ACC-1035", 6100.00, 3, "Unknown", 76.5, "🚨 HIGH RISK", "Anomalous late-night window"),
        ("Nagpur", "Pooja Wankhede", "ACC-1036", 230.00, 14, "Known", 9.0, "✅ APPROVED", "Nominal behavior"),
        ("Coimbatore", "Murugan Swamy", "ACC-1037", 8700.00, 1, "Unknown", 85.0, "🚨 HIGH RISK", "Unusually high volume"),
        ("Coimbatore", "Divya Nambiar", "ACC-1038", 380.00, 11, "Known", 12.5, "✅ APPROVED", "Nominal behavior"),
        ("Visakhapatnam", "Venkatesh Raju", "ACC-1039", 7900.00, 5, "Unknown", 82.5, "🚨 HIGH RISK", "Unusually high volume"),
        ("Visakhapatnam", "Sailaja Naidu", "ACC-1040", 320.00, 13, "Known", 11.0, "✅ APPROVED", "Nominal behavior"),
        ("Patna", "Ramanand Yadav", "ACC-1041", 2900.00, 2, "Unknown", 64.0, "⚠️ SUSPICIOUS", "Standard heuristic trigger"),
        ("Patna", "Sunita Kumari", "ACC-1042", 110.00, 10, "Known", 5.0, "✅ APPROVED", "Nominal behavior"),
        ("Vadodara", "Jitin Solanki", "ACC-1043", 5800.00, 4, "Unknown", 75.5, "🚨 HIGH RISK", "Anomalous late-night window"),
        ("Vadodara", "Komal Shah", "ACC-1044", 260.00, 17, "Known", 10.0, "✅ APPROVED", "Nominal behavior"),
        ("Ludhiana", "Harbhajan Gill", "ACC-1045", 6400.00, 3, "Unknown", 77.5, "🚨 HIGH RISK", "Anomalous late-night window"),
        ("Ludhiana", "Jasleen Dhillon", "ACC-1046", 280.00, 15, "Known", 10.5, "✅ APPROVED", "Nominal behavior"),
        ("Agra", "Shivendra Kushwaha", "ACC-1047", 4100.00, 1, "Unknown", 69.5, "🚨 HIGH RISK", "Anomalous late-night window"),
        ("Agra", "Archana Sharma", "ACC-1048", 170.00, 12, "Known", 7.0, "✅ APPROVED", "Nominal behavior"),
        ("Nashik", "Dnyaneshwar Patil", "ACC-1049", 5300.00, 4, "Unknown", 73.5, "🚨 HIGH RISK", "Anomalous late-night window"),
        ("Nashik", "Vandana Pawar", "ACC-1050", 220.00, 18, "Known", 9.0, "✅ APPROVED", "Nominal behavior"),
    ]
    for city, cust, acc, amt, hr, dev, risk, status, reason in sample_data:
        save_transaction(email, cust, acc, amt, hr, dev, city, risk, status, reason)


def get_transactions(

email

):

    if not email:

        return []

    email = email.strip().lower()

    conn = connect()

    cur = conn.cursor()

    cur.execute(

    """

    SELECT *

    FROM transactions

    WHERE LOWER(email)=?

    ORDER BY id DESC

    """,

    (email,)

    )

    rows = cur.fetchall()

    conn.close()

    return rows



# -------------------------------------------------

def clear_transactions(

email

):

    if not email:

        return

    email = email.strip().lower()

    conn = connect()

    cur = conn.cursor()

    cur.execute(

    """

    DELETE FROM transactions

    WHERE LOWER(email)=?

    """,

    (email,)

    )

    conn.commit()

    conn.close()


# -------------------------------------------------

create_tables()