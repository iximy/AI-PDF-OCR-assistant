import PyPDF2
import easyocr
from PIL import Image
import os
import json

with open('config/config.json') as config_file:
    config = json.load(config_file)

def extract_text_from_pdf(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page in reader.pages:
            text += page.extract_text()
        return text

def extract_text_from_image(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Инициализация EasyOCR
    reader = easyocr.Reader(['ru', 'en'])  # Поддержка русского и английского языков
    result = reader.readtext(file_path)
    
    # Извлекаем текст из результата
    text = ' '.join([detection[1] for detection in result])
    return text

def save_document(file, filename):
    documents_path = config['documents_path']
    if not os.path.exists(documents_path):
        os.makedirs(documents_path)
    file_path = os.path.join(documents_path, filename)
    with open(file_path, 'wb') as f:
        f.write(file.read())
    return file_path