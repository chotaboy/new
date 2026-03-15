from flask import Flask, render_template, request, jsonify
import sqlite3
import os

app = Flask(__name__)

# ---------------- DATABASE ---------------- #

def db():
    conn = sqlite3.connect("hospital.db")
    conn.row_factory = sqlite3.Row
    return conn


def init():
    conn = db()
    c = conn.cursor()

    # Patient table
    c.execute("""
    CREATE TABLE IF NOT EXISTS patients(
    id TEXT PRIMARY KEY,
    name TEXT,
    age TEXT,
    mobile TEXT,
    problem TEXT,
    notes TEXT
    )
    """)

    # Queue table
    c.execute("""
    CREATE TABLE IF NOT EXISTS queue(
    token INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id TEXT
    )
    """)

    conn.commit()
    conn.close()

init()

# ---------------- DASHBOARD ---------------- #

@app.route("/")
def home():
    return render_template("dashboard.html")

# ---------------- ADD PATIENT ---------------- #

@app.route("/add_patient", methods=["POST"])
def add_patient():

    data = request.json

    conn = db()
    c = conn.cursor()

    c.execute(
        "INSERT OR REPLACE INTO patients VALUES (?,?,?,?,?,?)",
        (data["id"], data["name"], data["age"],
         data["mobile"], data["problem"], "")
    )

    conn.commit()
    conn.close()

    return jsonify({"status":"ok"})


# ---------------- GET ALL PATIENTS ---------------- #

@app.route("/get_patients")
def get_patients():

    conn = db()
    c = conn.cursor()

    c.execute("SELECT * FROM patients")

    rows = [dict(r) for r in c.fetchall()]

    conn.close()

    return jsonify(rows)


# ---------------- ADD QUEUE MANUALLY ---------------- #

@app.route("/add_queue", methods=["POST"])
def add_queue():

    data = request.json

    conn = db()
    c = conn.cursor()

    c.execute(
        "INSERT INTO queue(patient_id) VALUES (?)",
        (data["patient_id"],)
    )

    conn.commit()
    conn.close()

    return jsonify({"status":"ok"})


# ---------------- QR SCAN TOKEN ---------------- #

@app.route("/scan_token", methods=["POST"])
def scan_token():

    data = request.json
    pid = data["patient_id"]

    print("QR SCANNED:", pid)

    conn = db()
    c = conn.cursor()

    # Check patient exists
    c.execute("SELECT * FROM patients WHERE id=?", (pid,))
    patient = c.fetchone()

    if not patient:
        conn.close()
        return jsonify({"status":"error","message":"Patient not found"})

    # Insert into queue
    c.execute("INSERT INTO queue(patient_id) VALUES (?)",(pid,))
    conn.commit()

    conn.close()

    return jsonify({"status":"token added"})


# ---------------- GET QUEUE ---------------- #

@app.route("/get_queue")
def get_queue():

    conn = db()
    c = conn.cursor()

    c.execute("""
    SELECT queue.token, queue.patient_id, patients.name
    FROM queue
    JOIN patients ON patients.id = queue.patient_id
    ORDER BY queue.token
    """)

    rows = [dict(r) for r in c.fetchall()]

    conn.close()

    return jsonify(rows)


# ---------------- PATIENT DETAILS ---------------- #

@app.route("/get_patient/<pid>")
def get_patient(pid):

    conn = db()
    c = conn.cursor()

    c.execute("SELECT * FROM patients WHERE id=?", (pid,))
    row = c.fetchone()

    conn.close()

    return jsonify(dict(row))


# ---------------- SAVE DOCTOR NOTES ---------------- #

@app.route("/save_notes", methods=["POST"])
def save_notes():

    data = request.json

    conn = db()
    c = conn.cursor()

    c.execute(
        "UPDATE patients SET notes=? WHERE id=?",
        (data["notes"], data["id"])
    )

    conn.commit()
    conn.close()

    return jsonify({"status":"ok"})


# ---------------- NEXT PATIENT ---------------- #

@app.route("/next_patient", methods=["POST"])
def next_patient():

    conn = db()
    c = conn.cursor()

    c.execute("""
    DELETE FROM queue
    WHERE token = (
        SELECT token FROM queue
        ORDER BY token
        LIMIT 1
    )
    """)

    conn.commit()
    conn.close()

    return jsonify({"status":"ok"})

@app.route("/status")
def status():
    return jsonify({"status":"online"})

# ---------------- RUN SERVER ---------------- #
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
