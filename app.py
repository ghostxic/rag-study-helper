from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from werkzeug.utils import secure_filename
import magic
import os
from datetime import datetime, timedelta
from pdf_to_db import pdf_path_to_chromadb
from supabase_insert import insert_metadata
from question_to_answer import question_to_answer
from supabase import create_client
import uuid


app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = os.environ["UPLOAD_FOLDER"]
app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=5)
app.config["SESSION_PERMANENT"] = True

supabase = create_client(
        os.environ["SUPABASE_URL"],
        os.environ["SUPABASE_API_KEY"]
    )

# Create uploads folder if it doesn't exist
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

def allowed_file_extension(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() == "pdf"

def allowed_file_mimetype(file_stream):
    buffer_size = 4100
    mime_detector = magic.Magic(mime=True)
    
    # Read the buffer and reset the file pointer afterward
    file_content_buffer = file_stream.read(buffer_size)
    file_stream.seek(0) # Reset stream pointer to the beginning for later saving/processing
    
    file_type = mime_detector.from_buffer(file_content_buffer)
    
    return file_type == "application/pdf"

def get_size(fobj):
    if fobj.content_length:
        return fobj.content_length
    try:
        # Save current position
        pos = fobj.tell()
        # Seek to the end of the file
        fobj.seek(0, 2)
        size = fobj.tell()
        # Seek back to original position
        fobj.seek(pos)
        return size
    except (AttributeError, IOError):
        # Handle in-memory files that don't support seeking or tell
        return 0 # Assume small enough

def validate_file_upload(file):
    if not file or file.filename == "":
        return False, "No file selected", 400
    
    if not allowed_file_extension(file.filename):
        return False, "Only PDF files are allowed", 400
    
    if not allowed_file_mimetype(file.stream):
        return False, "File MIME type is not PDF", 400
    
    file_size = get_size(file)
    max_size = 100 * 1024 * 1024  # 100MB
    if file_size > max_size:
        return False, "File too large (max 100MB)", 413
    
    return True, None, None


def save_uploaded_file(file):
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    return filepath


def process_pdf_document(filepath):
    all_data = pdf_path_to_chromadb(filepath)
    insert_metadata(all_data)
    return all_data


def cleanup_temp_file(filepath):
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            print(f"Cleaned up temporary file: {os.path.basename(filepath)}")
    except Exception as e:
        print(f"Warning: Could not delete temporary file {filepath}: {str(e)}")

@app.route("/", methods=["GET"])
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        try:
            auth = supabase.auth.sign_up({"email": email, "password": password})
            user = supabase.auth.sign_in_with_password({"email": email, "password": password})
            session["id"] = user.user.id
            session["email"] = user.user.email
            return redirect(url_for("home"))
        except Exception as e:
            session["redirect_data"] = f"Unable to register with Supabase, please try again. Error: {e}"
            return redirect(url_for("register"))
    redirect_data = session.pop("redirect_data", None)
    return render_template("register.html", redirect_data = redirect_data)

@app.route("/login", methods=["GET", "POST"])
def login():
    if "id" in session:
        return redirect(url_for("home"))
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        try:
            user = supabase.auth.sign_in_with_password({"email": email, "password": password})
            session["id"] = user.user.id
            session["email"] = user.user.email
            return redirect(url_for("home"))
        except Exception as e:
            session["redirect_data"] = f"Unable to login with Supabase, please try again. Error: {e}"
            return redirect(url_for("login"))
    redirect_data = session.pop("redirect_data", None)
    return render_template("login.html", redirect_data = redirect_data)

@app.route("/logout", methods=["GET", "POST"])
def logout():
    try:
        supabase.auth.sign_out()
    except:
        pass
    
    session.clear()
    session["redirect_data"] = "Successfully logged out!"
    return redirect(url_for('login'))

@app.route("/upload", methods=["POST"])
def upload_document():
    filepath = None
    
    try:
        if "file" not in request.files:
            session["pdf_json"] = {"error": "No file provided"}
            return redirect(url_for("home"))
        
        file = request.files["file"]
        
        is_valid, error_message, status_code = validate_file_upload(file)
        if not is_valid:
            session["pdf_json"] = {"error": error_message}
            return redirect(url_for("home"))
        
        filepath = save_uploaded_file(file)
        
        # Process PDF and store in databases
        all_data = process_pdf_document(filepath)
        
        # Clean up temporary file
        cleanup_temp_file(filepath)
        
        # Return success response
        session["pdf_json"] = {
            "success": True,
            "message": "PDF processed successfully",
            "document_id": all_data.doc_id,
            "filename": all_data.filename,
            "num_chunks": all_data.num_chunks,
        }
        return redirect(url_for("home"))
        
    except Exception as e:
        # Clean up temp file on error
        if filepath:
            cleanup_temp_file(filepath)
        session["pdf_json"] = {"error": f"Error processing file: {str(e)}"}
        return redirect(url_for("home"))

@app.route("/ask", methods=["POST"])
def ask_question():
    question = request.form.get("question")
    response = question_to_answer(question)
    message_id = str(uuid.uuid4())

    user_id = session.get("id")

    supabase.table("chat_history").insert({
            "chat_id": message_id,
            "user_id": user_id,
            "question": question,
            "answer": response,
            "timestamp": datetime.now().isoformat()
    }).execute()
    session["response_json"] = jsonify(response).get_json()
    return redirect(url_for("home"))

@app.route("/home")
def home():
    if "id" not in session:
        session["redirect_data"] = "Please login in to access this page."
        return redirect(url_for("register"))
    pdf_json = session.pop("pdf_json", None)
    response_json = session.pop("response_json", None)
    redirect_data = session.pop("redirect_data", None)
    return render_template("home.html", pdf_json = pdf_json, response_json = response_json, redirect_data = redirect_data, username = session["email"].split("@")[0])

if __name__ == "__main__":
    with app.app_context():
        app.run(port=8080, debug=True)