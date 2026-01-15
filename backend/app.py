import os
import tempfile
import time
import threading
import csv

from flask import Flask, jsonify, request, render_template, send_file
from flask_cors import CORS
from parallel_engine import scan_file_parallel
from report_generator import generate_report
from scanner import scan_file_sequential_with_progress

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)
CORS(app)
# 🔥 GLOBAL STATE
scan_state = {
    "progress": 0,
    "stage": "Idle",
    "status": "Idle",
    "result": None,
}

last_scan_matches = []


@app.route("/")
def index():
    return jsonify({"status": "Backend is running"})


def _get_selected_categories(form_data):
    categories = []
    if form_data.get("scan_sensitive"):
        categories.append("sensitive")
    if form_data.get("scan_forbidden"):
        categories.append("forbidden")
    if form_data.get("scan_policy"):
        categories.append("policy")
    if not categories:
        categories = ["sensitive", "forbidden", "policy"]
    return categories


@app.route("/start_scan", methods=["POST"])
def start_scan():
    global scan_state

    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    upload_file = request.files["file"]
    if not upload_file or upload_file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    categories = _get_selected_categories(request.form)

    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_path = temp_file.name
    upload_file.save(temp_path)
    temp_file.close()

    # Reset state
    scan_state = {
        "progress": 0,
        "stage": "Starting",
        "status": "Running",
        "result": None,
    }

    def run_scan():
        global scan_state, last_scan_matches

        try:
            scan_state["stage"] = "Sequential scan"

            start_seq = time.perf_counter()
            sequential_matches = scan_file_sequential_with_progress(
                temp_path, categories, scan_state
            )
            time_sequential = time.perf_counter() - start_seq

            scan_state["stage"] = "Parallel scan"

            start_par = time.perf_counter()
            parallel_matches = scan_file_parallel(temp_path, categories)
            last_scan_matches = parallel_matches  # ✅ STORE RESULTS
            time_parallel = time.perf_counter() - start_par

            scan_state["stage"] = "Generating report"
            scan_state["progress"] = 95

            report = generate_report(
                sequential_matches=sequential_matches,
                parallel_matches=parallel_matches,
                time_taken_sequential=time_sequential,
                time_taken_parallel=time_parallel,
            )

            scan_state["progress"] = 100
            scan_state["status"] = "Completed"
            scan_state["result"] = report

        except Exception as e:
            scan_state["status"] = "Error"
            scan_state["result"] = {"error": str(e)}

        finally:
            try:
                os.remove(temp_path)
            except:
                pass

    threading.Thread(target=run_scan).start()

    return jsonify({"ok": True})


@app.route("/scan_progress")
def scan_progress():
    return jsonify(scan_state)


# ✅ CSV DOWNLOAD ENDPOINT
@app.route("/download_csv")
def download_csv():
    global last_scan_matches

    if not last_scan_matches:
        return jsonify({"error": "No scan data available"}), 400

    temp_path = tempfile.NamedTemporaryFile(delete=False, suffix=".csv").name

    with open(temp_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["line", "category", "matched_text", "rule"])

        for item in last_scan_matches:
            writer.writerow([
                item.get("line"),
                item.get("type"),
                item.get("match"),
                item.get("rule"),
            ])

    return send_file(
        temp_path,
        as_attachment=True,
        download_name="scan_results.csv",
        mimetype="text/csv",
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)