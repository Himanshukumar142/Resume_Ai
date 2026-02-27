from flask import Blueprint, request, jsonify
from flask_login import login_required
import os
from config import allowed_file

resume_bp = Blueprint("resume", __name__)


@resume_bp.route("/ats_score", methods=["POST"])
def ats_score():
    if "resume" not in request.files or "job_description" not in request.form:
        return jsonify({"error": "Please upload a resume file and provide job description text."}), 400

    resume_file      = request.files["resume"]
    job_description_text = request.form.get("job_description", "").strip()

    if not resume_file or not job_description_text:
        return jsonify({"error": "Both resume file and job description text are required."}), 400

    if not allowed_file(resume_file.filename):
        return jsonify({"error": "Unsupported file type. Please upload a PDF or DOCX file."}), 400

    upload_folder = os.path.join(os.path.dirname(__file__), "uploads")
    os.makedirs(upload_folder, exist_ok=True)
    resume_path = os.path.join(upload_folder, resume_file.filename)
    resume_file.save(resume_path)

    try:
        try:
            from backend.resume_parser import extract_text
            from backend.scoring import compute_score
        except Exception:
            from resume_parser import extract_text
            from scoring import compute_score
    except Exception as e:
        if os.path.exists(resume_path):
            os.remove(resume_path)
        return jsonify({"error": f"Server dependency error: {e}"}), 500

    resume_text = extract_text(resume_path)

    if os.path.exists(resume_path):
        os.remove(resume_path)

    if not resume_text.strip():
        return jsonify({"error": "Could not extract text from the uploaded file."}), 422

    score = compute_score(resume_text, job_description_text)
    return jsonify({"score": float(score)})


@resume_bp.route("/process_resume", methods=["POST"])
@login_required
def process_resume():
    """Full analysis — requires login. Returns score + retrieved tips + AI suggestions."""
    if "resume" not in request.files or "job_description" not in request.form:
        return jsonify({"error": "Please upload a resume file and provide job description text."}), 400

    resume_file          = request.files["resume"]
    job_description_text = request.form.get("job_description", "").strip()

    if not resume_file or not job_description_text:
        return jsonify({"error": "Both resume file and job description text are required."}), 400

    if not allowed_file(resume_file.filename):
        return jsonify({"error": "Unsupported file type. Please upload a PDF or DOCX file."}), 400

    upload_folder = os.path.join(os.path.dirname(__file__), "uploads")
    os.makedirs(upload_folder, exist_ok=True)
    resume_path = os.path.join(upload_folder, resume_file.filename)
    resume_file.save(resume_path)

    try:
        try:
            from backend.resume_parser import extract_text
            from backend.rag import get_suggestions
        except Exception:
            from resume_parser import extract_text
            from rag import get_suggestions
    except Exception as e:
        if os.path.exists(resume_path):
            os.remove(resume_path)
        return jsonify({"error": f"Server dependency error: {e}"}), 500

    resume_text = extract_text(resume_path)

    if not resume_text.strip():
        if os.path.exists(resume_path):
            os.remove(resume_path)
        return jsonify({"error": "Could not extract text from the uploaded file."}), 422

    result = get_suggestions(resume_text, job_description_text)

    if os.path.exists(resume_path):
        os.remove(resume_path)

    return jsonify(result)
