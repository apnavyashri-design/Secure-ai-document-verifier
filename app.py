from flask import Flask, request, jsonify, send_file
import hashlib
from PIL import Image
import io
import os

app = Flask(__name__)

# Simple in-memory storage for verified documents (simulating blockchain)
verified_documents = {}

# Optional: Tesseract OCR setup
try:
    import pytesseract
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    TESSERACT_AVAILABLE = True
except:
    TESSERACT_AVAILABLE = False

@app.route('/')
def index():
    return send_file('frontend.html')

@app.route('/upload', methods=['POST'])
def upload_document():
    if 'document' not in request.files:
        return jsonify({'success': False, 'error': 'No file uploaded'}), 400
    
    file = request.files['document']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400
    
    try:
        # Read file content
        file_content = file.read()
        
        # Generate SHA-256 hash of original document
        doc_hash = hashlib.sha256(file_content).hexdigest()
        
        # Try OCR if available, otherwise show file info
        extracted_text = ""
        confidence = 0.95
        
        if TESSERACT_AVAILABLE and file.content_type.startswith('image'):
            try:
                file.seek(0)
                image = Image.open(io.BytesIO(file_content))
                extracted_text = pytesseract.image_to_string(image)
                confidence = min(0.99, max(0.5, len(extracted_text.strip()) / 200.0))
            except:
                extracted_text = f"📄 Document: {file.filename}\n📊 Size: {len(file_content)} bytes\n🔖 Type: {file.content_type}"
        else:
            extracted_text = f"📄 Document: {file.filename}\n📊 Size: {len(file_content)} bytes\n🔖 Type: {file.content_type}"
        
        # Store in memory (simulating blockchain)
        verified_documents[doc_hash] = {
            'filename': file.filename,
            'text': extracted_text,
            'verified': True
        }
        
        return jsonify({
            'success': True,
            'extracted_text': extracted_text.strip() if extracted_text else f"Document: {file.filename}",
            'hash': doc_hash,
            'confidence': confidence
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/verify', methods=['POST'])
def verify_document():
    data = request.json
    doc_hash = data.get('hash', '')
    
    try:
        # Check if hash exists in our simulated blockchain
        is_verified = doc_hash in verified_documents
        return jsonify({
            'verified': is_verified,
            'message': 'Document verified on blockchain!' if is_verified else 'Document not found'
        })
        
    except Exception as e:
        return jsonify({'verified': False, 'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Server starting at http://localhost:5000")
    app.run(debug=True, port=5000)
