from flask import Flask, request, jsonify, render_template
from utils.document_processor import extract_text_from_pdf, extract_text_from_image, save_document
from utils.rag import generate_response
import os
import json

app = Flask(__name__, template_folder='../web/templates', static_folder='../web/static')

# Маршрут для корневой страницы
@app.route('/')
def index():
    return render_template('index.html')

# Маршрут для загрузки документа
@app.route('/upload', methods=['POST'])
def upload_document():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    file_path = save_document(file, file.filename)
    return jsonify({"message": "File uploaded successfully", "file_path": file_path}), 200

# Маршрут для запроса к модели
@app.route('/ask', methods=['POST'])
def ask_question():
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400

    query = data.get('query')
    file_path = data.get('file_path')
    role = data.get('role', 'assistant')  # По умолчанию роль "Ассистент"

    if not query or not file_path:
        return jsonify({"error": "Missing query or file_path"}), 400

    try:
        # Определяем тип файла и извлекаем текст
        if file_path.endswith('.pdf'):
            context = extract_text_from_pdf(file_path)
        elif file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
            context = extract_text_from_image(file_path)
        else:
            return jsonify({"error": "Unsupported file type"}), 400

        # Генерируем ответ
        response = generate_response(query, context, role)
        return jsonify({"response": response}), 200
    except Exception as e:
        print("Error in ask_question:", str(e))
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    with open('../config/config.json') as config_file:
        config = json.load(config_file)
    app.run(host=config['server']['host'], port=config['server']['port'])