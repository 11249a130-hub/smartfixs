"""
SmartFix – NLP-Based Smart Campus & Hostel Complaint Management System
Backend Application (Flask)
"""

import os
from flask import Flask, render_template, request, jsonify
import database
from nlp_engine import nlp_engine

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    static_folder=os.path.join(BASE_DIR, "static"),
    static_url_path="/static",
    template_folder=os.path.join(BASE_DIR, "templates")
)
app.secret_key = os.environ.get("SECRET_KEY", "smartfix-campus-secret-key-2026")

# Ensure database is initialized on boot
with app.app_context():
    database.init_db()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/nlp/analyze", methods=["POST"])
def analyze_complaint_nlp():
    """Real-time NLP analysis endpoint using TF-IDF and Linear SVM."""
    data = request.get_json() or {}
    text = data.get("text", "")
    result = nlp_engine.classify_complaint(text)
    return jsonify({
        "success": True,
        "analysis": result
    })


@app.route("/api/complaints", methods=["GET"])
def list_complaints():
    role = request.args.get("role", "admin")
    user_id = request.args.get("user_id")
    filter_status = request.args.get("status")
    filter_category = request.args.get("category")
    search = request.args.get("search")

    uid = int(user_id) if user_id and user_id.isdigit() else None
    complaints = database.get_complaints(
        role=role,
        user_id=uid,
        filter_status=filter_status,
        filter_category=filter_category,
        search=search
    )
    return jsonify({"success": True, "complaints": complaints})


@app.route("/api/complaints", methods=["POST"])
def submit_complaint():
    data = request.get_json() or {}
    description = data.get("description", "").strip()

    if not description:
        return jsonify({"success": False, "error": "Complaint description is required."}), 400

    # Execute NLP pipeline to predict category, asset, priority, and SLA
    nlp_res = nlp_engine.classify_complaint(description)

    # Allow student to use auto-detected values or override
    category = data.get("category") or nlp_res["category"]
    asset = data.get("asset") or nlp_res["asset"]
    priority = data.get("priority") or nlp_res["priority"]
    sla_hours = nlp_res["sla_hours"]
    is_safety_critical = nlp_res["is_safety_critical"]

    payload = {
        "student_id": data.get("student_id", 1),
        "student_name": data.get("student_name", "Rahul Verma"),
        "student_email": data.get("student_email", "rahul.verma@college.edu"),
        "hostel_block": data.get("hostel_block", "Hostel Block A"),
        "room_number": data.get("room_number", "204"),
        "contact_number": data.get("contact_number", "+91 9876543210"),
        "title": data.get("title") or f"{asset} issue in {data.get('room_number', 'room')}",
        "description": description,
        "category": category,
        "asset": asset,
        "priority": priority,
        "sla_hours": sla_hours,
        "is_safety_critical": is_safety_critical
    }

    new_complaint = database.create_complaint(payload)
    return jsonify({
        "success": True,
        "complaint": new_complaint,
        "nlp_analysis": nlp_res
    }), 201


@app.route("/api/complaints/<int:cid>", methods=["GET"])
def get_single_complaint(cid):
    complaint = database.get_complaint_by_id(cid)
    if not complaint:
        return jsonify({"success": False, "error": "Complaint not found"}), 404
    logs = database.get_complaint_logs(cid)
    return jsonify({"success": True, "complaint": complaint, "logs": logs})


@app.route("/api/complaints/<int:cid>/assign", methods=["POST"])
def assign_complaint_staff(cid):
    data = request.get_json() or {}
    staff_id = data.get("staff_id")
    staff_name = data.get("staff_name")
    admin_name = data.get("admin_name", "Campus Estate Admin")

    if not staff_id or not staff_name:
        return jsonify({"success": False, "error": "Staff ID and Name are required"}), 400

    database.assign_complaint(cid, int(staff_id), staff_name, admin_name)
    updated = database.get_complaint_by_id(cid)
    return jsonify({"success": True, "complaint": updated})


@app.route("/api/complaints/<int:cid>/status", methods=["POST"])
def update_complaint_status_endpoint(cid):
    data = request.get_json() or {}
    new_status = data.get("status")
    updated_by = data.get("updated_by", "Maintenance Staff")
    notes = data.get("notes", "")

    if not new_status:
        return jsonify({"success": False, "error": "Status is required"}), 400

    database.update_complaint_status(cid, new_status, updated_by, notes)
    updated = database.get_complaint_by_id(cid)
    return jsonify({"success": True, "complaint": updated})


@app.route("/api/complaints/<int:cid>/confirm", methods=["POST"])
def confirm_complaint_fix(cid):
    data = request.get_json() or {}
    rating = int(data.get("rating", 5))
    feedback = data.get("feedback", "Issue successfully resolved.")
    student_name = data.get("student_name", "Student")

    database.confirm_resolution(cid, rating, feedback, student_name)
    updated = database.get_complaint_by_id(cid)
    return jsonify({"success": True, "complaint": updated})


@app.route("/api/staff", methods=["GET"])
def get_staff():
    staff_list = database.get_staff_members()
    return jsonify({"success": True, "staff": staff_list})


@app.route("/api/users", methods=["GET"])
def get_users():
    users = database.get_all_users()
    return jsonify({"success": True, "users": users})


@app.route("/api/analytics", methods=["GET"])
def get_analytics():
    data = database.get_dashboard_analytics()
    return jsonify({"success": True, "analytics": data})


@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy",
        "system": "SmartFix – Campus & Hostel Complaint Management System",
        "nlp_engine": "Linear SVM (TF-IDF)",
        "database": "MySQL / SQLite Hybrid",
        "version": "1.0.0"
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
