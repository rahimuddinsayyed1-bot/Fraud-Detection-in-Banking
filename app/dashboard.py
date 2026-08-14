from collections import Counter
import json
import csv
import io
import os
import pickle
import numpy as np
from flask import Flask, redirect, render_template, request, session

try:
    from auth import auth
    from export import export
    from database import (
        save_transaction,
        get_transactions,
        create_tables,
        get_user,
        clear_transactions
    )
except ImportError:
    from .auth import auth
    from .export import export
    from .database import (
        save_transaction,
        get_transactions,
        create_tables,
        get_user,
        clear_transactions
    )

app = Flask(
    __name__,
    template_folder="../templates",
    static_folder="../static"
)
app.secret_key = "Super_Secure_Key_2026"
app.register_blueprint(auth)
app.register_blueprint(export)
create_tables()

MODEL_PATH = os.path.join(
    os.path.dirname(__file__), "../model/fraud_model_v2.pkl"
)
with open(MODEL_PATH, "rb") as f:
  model = pickle.load(f)

LOCATION_MAP = {
    "Mumbai": 0, "Delhi": 1, "Bangalore": 2, "Hyderabad": 3,
    "Chennai": 4, "Kolkata": 5, "Pune": 6, "Ahmedabad": 7,
    "Jaipur": 8, "Surat": 9, "Lucknow": 10, "Chandigarh": 11,
    "Noida": 12, "Gurgaon": 13, "Kochi": 14, "Indore": 15,
    "Bhopal": 16, "Nagpur": 17, "Coimbatore": 18, "Visakhapatnam": 19,
    "Patna": 20, "Vadodara": 21, "Ludhiana": 22, "Agra": 23, "Nashik": 24
}



def dashboard_statistics(rows):
    total = len(rows)
    fraud = len([r for r in rows if "HIGH" in r["status"]])
    suspicious = len([r for r in rows if "SUSPICIOUS" in r["status"]])
    safe = total - fraud - suspicious

    avg_risk = 0.0
    if total:
        avg_risk = round(sum(r["risk"] for r in rows) / total, 1)

    cities = Counter()
    for row in rows:
        cities[row["city"]] += 1

    chart_labels = list(cities.keys())
    chart_values = list(cities.values())

    return {
        "total": total,
        "fraud": fraud,
        "safe": safe,
        "suspicious": suspicious,
        "avg": avg_risk,
        "labels": json.dumps(chart_labels),
        "values": json.dumps(chart_values),
        "pie_data": json.dumps([safe, suspicious, fraud])
    }


def calculate_risk(amount, hour, device_val, loc_str):
  loc_code = LOCATION_MAP.get(loc_str, 0)
  features = np.array([[float(amount), int(hour), int(device_val), loc_code]])

  prob = model.predict_proba(features)[0][1]
  risk_pct = round(prob * 100, 1)

  reasons = []
  if float(amount) > 1000:
    reasons.append("Unusually high volume")
  if int(hour) < 6 or int(hour) > 23:
    reasons.append("Anomalous late-night window")
  if int(device_val) == 0:
    reasons.append("Unrecognized hardware signature")

  if risk_pct >= 65.0:
    status = "🚨 HIGH RISK"
    reason = ", ".join(reasons) if reasons else "Pattern matches known vectors"
  elif risk_pct >= 35.0:
    status = "⚠️ SUSPICIOUS"
    reason = "Standard heuristic trigger - verify manually"
  else:
    status = "✅ APPROVED"
    reason = "Nominal behavior"

  return risk_pct, status, reason


@app.route("/")
def home():

    if "user" not in session:
        return redirect("/login")

    rows = get_transactions(session["user"])
    stats = dashboard_statistics(rows)

    user = get_user(session["user"])
    name = session.get("name") or (user["full_name"] if user else "User")

    return render_template(
        "dashboard.html",
        rows=rows,
        name=name,
        total=stats["total"],
        fraud=stats["fraud"],
        safe=stats["safe"],
        suspicious=stats["suspicious"],
        avg=stats["avg"],
        labels=stats["labels"],
        values=stats["values"],
        pie_data=stats["pie_data"],
        active_tab="dashboard"
    )


@app.route("/predict", methods=["POST"])
def predict():

    if "user" not in session:
        return redirect("/login")

    # Read form values
    cust = request.form["customer_name"]
    acc = request.form["account_number"]
    amt = float(request.form["amount"])
    hr = int(request.form["hour"])
    dev = int(request.form["device"])
    loc = request.form["location"]

    # ML Prediction
    risk_pct, status, reason = calculate_risk(amt, hr, dev, loc)

    dev_label = "Known" if dev == 1 else "Unknown"

    # Save transaction
    save_transaction(
        session["user"],
        cust,
        acc,
        amt,
        hr,
        dev_label,
        loc,
        risk_pct,
        status,
        reason
    )

    rows = get_transactions(session["user"])
    stats = dashboard_statistics(rows)

    user = get_user(session["user"])
    name = session.get("name") or (user["full_name"] if user else "User")

    result = {
        "status": status,
        "risk": f"{risk_pct}%",
        "reason": reason
    }

    return render_template(
        "dashboard.html",
        rows=rows,
        result=result,
        name=name,
        total=stats["total"],
        fraud=stats["fraud"],
        safe=stats["safe"],
        suspicious=stats["suspicious"],
        avg=stats["avg"],
        labels=stats["labels"],
        values=stats["values"],
        pie_data=stats["pie_data"],
        active_tab="transaction"
    )



@app.route("/upload_csv", methods=["POST"])
def upload_csv():
  if "csv_file" not in request.files:
    return redirect("/")
  file = request.files["csv_file"]
  if file.filename == "":
    return redirect("/")

  stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
  reader = csv.DictReader(stream)

  for row in reader:
    # Safely look for Customer/Account, default if missing
    cust = row.get("Customer", "Batch Ingest")
    acc = row.get("Account", "SYS-BATCH")
    amt = float(row.get("Amount", 0))
    hr = int(row.get("Hour", 12))
    dev = int(row.get("Device", 1))
    loc = row.get("Location", "Hyderabad")

    risk_pct, status, reason = calculate_risk(amt, hr, dev, loc)
    dev_str = "Known" if dev == 1 else "Unknown"
    save_transaction(
        session["user"],
        cust,
        acc,
        amt,
        hr,
        dev_str,
        loc,
        risk_pct,
        status,
        reason
    )

  return redirect("/")


@app.route("/profile")
def profile():

    if "user" not in session:
        return redirect("/login")

    user = get_user(session["user"])
    rows = get_transactions(session["user"])
    stats = dashboard_statistics(rows)

    return render_template(
        "profile.html",
        user=user,
        stats=stats
    )


@app.route("/logout")
def logout():

    if "user" in session:
        clear_transactions(session["user"])

    session.clear()

    return redirect("/login")


if __name__ == "__main__":
  app.run(debug=True)