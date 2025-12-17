from flask import Flask, request, jsonify, json, render_template
from chroma import get_chroma_collection

app = Flask(__name__)

@app.route("/api/documents/", methods=["POST"])
def add_documents():
    try:
        request_body = request.get_json()
        ids = request_body.get('ids')
        documents = request_body.get('documents')
        metadatas = request_body.get('metadatas')
        
        collection = get_chroma_collection()

        collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
        )
        return jsonify({"message": "Documents added successfully", "ids": ids}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/")
def home():
    return render_template("home.html")

if __name__ == "__main__":
    with app.app_context():
        app.run(port=8080, debug=True)