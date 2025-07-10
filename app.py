# app.py
from flask import Flask, request, jsonify, send_from_directory
import os

# ✅ 从 backend 子目录引入
from backend.pdf_parser import parse_pdf

from backend.qa_engine import (
    retrieve_relevant_context,
    answer_question,
    is_figure_question,
    handle_figure_question
)
from backend.vision_ask import image_to_base64, ask_qwen_vl_sdk


app = Flask(__name__)

UPLOAD_FOLDER = 'uploaded_files'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def serve_index():
    return send_from_directory('frontend', 'index.html')


@app.route('/upload', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and file.filename.endswith('.pdf'):
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)
        
        
        # 🧪 加入 PDF 解析测试
        text, images = parse_pdf(filepath)
        print(f"提取文本页数: {len(text)}")
        print(f"提取图片数量: {len(images)}")

        return jsonify({
            "message": "File uploaded successfully",
            "filename": file.filename,
            "text_pages": len(text),
            "image_count": len(images)
        }), 200
    
    return jsonify({"error": "Only PDF files are allowed"}), 400


@app.route('/ask', methods=['POST'])
def ask_question():
    data = request.json
    filename = data.get("filename")
    question = data.get("question")

    if not filename or not question:
        return jsonify({"error": "Missing filename or question"}), 400

    filepath = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(filepath):
        return jsonify({"error": "File not found"}), 404

    text, images = parse_pdf(filepath)

    # ✅ 判断是否是图像问题
    if is_figure_question(question):
        result = handle_figure_question(question, images)
        return jsonify(result)

    # 普通问答流程
    context_blocks = retrieve_relevant_context(question, text)
    answer = answer_question(question, context_blocks)

    return jsonify({
        "answer": answer,
        "reference": context_blocks
    })

@app.route('/vision_ask', methods=['POST'])
def vision_ask():
    if 'image' not in request.files or 'question' not in request.form:
        return jsonify({"error": "Missing image or question"}), 400

    image = request.files['image']
    question = request.form['question']

    image_base64 = image_to_base64(image)
    answer = ask_qwen_vl_sdk(image_base64, question)

    return jsonify({"answer": answer})



if __name__ == '__main__':
    app.run(debug=True, port=5000)
