
from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os
from config import UPLOAD_FOLDER, allowed_file
from services.pdf_reader import extract_text_from_pdf
from services.ai_engine import ask_question

main = Blueprint('main', __name__)

@main.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'pdf' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['pdf']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)

            text = extract_text_from_pdf(filepath)
            request.session_text = text  # Store in request context

            return render_template('chat.html', text=text)
        else:
            flash('Invalid file type. Only PDFs are allowed.')
    return render_template('index.html')


@main.route('/ask', methods=['POST'])
def ask():
    user_question = request.form.get('question')
    pdf_text = request.form.get('pdf_text')

    if not user_question or not pdf_text:
        return "Missing data", 400

    answer = ask_question(user_question, pdf_text)
    return render_template('chat.html', text=pdf_text, question=user_question, answer=answer)
