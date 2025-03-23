import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def ask_with_context(question, pdf_text, chat_history):
    messages = [
        {"role": "system", "content": "You are an assistant helping with PDF content. Answer clearly and helpfully."},
        {"role": "user", "content": f"Here is the PDF content:\n\n{pdf_text}"}
    ]

    for item in chat_history:
        messages.append({"role": "user", "content": item['question']})
        messages.append({"role": "assistant", "content": item['answer']})

    messages.append({"role": "user", "content": question})

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"Error: {str(e)}"
