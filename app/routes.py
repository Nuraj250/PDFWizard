from flask import Blueprint, render_template, request, redirect, url_for, flash, session, send_file
from werkzeug.utils import secure_filename
from config import UPLOAD_FOLDER, allowed_file
from services.pdf_reader import extract_text_from_pdf
from services.ai_engine import ask_with_context
import os
from io import BytesIO
from fpdf import FPDF

main = Blueprint('main', __name__)

@main.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        files = request.files.getlist('pdf')
        all_texts = []

        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)
                all_texts.append(extract_text_from_pdf(filepath))

        if not all_texts:
            flash('Please upload at least one valid PDF.')
            return redirect(request.url)

        session['pdf_text'] = "\n\n".join(all_texts)
        session['chat_history'] = []  # reset chat
        return redirect(url_for('main.chat'))

    return render_template('index.html')


@main.route('/chat', methods=['GET', 'POST'])
def chat():
    if request.method == 'POST':
        question = request.form.get('question')
        pdf_text = session.get('pdf_text', '')
        chat_history = session.get('chat_history', [])

        if not question or not pdf_text:
            flash("Missing question or PDF content.")
            return redirect(url_for('main.index'))

        answer = ask_with_context(question, pdf_text, chat_history)
        chat_history.append({'question': question, 'answer': answer})
        session['chat_history'] = chat_history

    return render_template('chat.html', chat_history=session.get('chat_history', []))


@main.route('/export/<fmt>')
def export_chat(fmt):
    chat = session.get('chat_history', [])
    if not chat:
        flash("No chat history to export.")
        return redirect(url_for('main.chat'))

    output = BytesIO()

    if fmt == 'txt':
        content = "\n\n".join([f"You: {c['question']}\nPDFWizard: {c['answer']}" for c in chat])
        output.write(content.encode('utf-8'))
        output.seek(0)
        return send_file(output, download_name="chat.txt", as_attachment=True, mimetype='text/plain')

    elif fmt == 'pdf':
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        for c in chat:
            pdf.multi_cell(0, 10, f"You: {c['question']}\nPDFWizard: {c['answer']}\n")
        pdf.output(output)
        output.seek(0)
        return send_file(output, download_name="chat.pdf", as_attachment=True, mimetype='application/pdf')

    flash("Invalid export format.")
    return redirect(url_for('main.chat'))
