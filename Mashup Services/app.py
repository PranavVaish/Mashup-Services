import os
import smtplib
import zipfile
from email.message import EmailMessage
from flask import Flask, render_template, request, send_file
from mashup import create_mashup
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# --- CONFIGURATION ---
SENDER_EMAIL = os.getenv('SENDER_EMAIL') # <--- PUT YOUR EMAIL HERE
SENDER_PASSWORD = os.getenv('SENDER_PASSWORD') # <--- PUT YOUR APP PASSWORD HERE
# ---------------------

def send_email(recipient_email, zip_path):
    msg = EmailMessage()
    msg['Subject'] = "Your Mashup Request is Ready!"
    msg['From'] = SENDER_EMAIL
    msg['To'] = recipient_email
    msg.set_content("Attached is the mashup zip file you requested.")

    with open(zip_path, 'rb') as f:
        file_data = f.read()
        file_name = os.path.basename(zip_path)

    msg.add_attachment(file_data, maintype='application', subtype='zip', filename=file_name)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(SENDER_EMAIL, SENDER_PASSWORD)
        smtp.send_message(msg)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/mashup', methods=['POST'])
def process_mashup():
    try:
        # 1. Get Form Data
        singer = request.form['singer']
        count = int(request.form['count'])
        duration = int(request.form['duration'])
        email = request.form['email']

        # 2. Run Mashup Logic
        output_mp3 = os.path.join(UPLOAD_FOLDER, f"{singer.replace(' ', '_')}_mashup.mp3")
        success = create_mashup(singer, count, duration, output_mp3)

        if not success:
            return "Error: Could not create mashup (Check server logs or internet).", 500

        # 3. Create Zip File
        zip_filename = output_mp3.replace(".mp3", ".zip")
        with zipfile.ZipFile(zip_filename, 'w') as zipf:
            zipf.write(output_mp3, arcname=os.path.basename(output_mp3))

        # 4. Send Email
        try:
            send_email(email, zip_filename)
            return f"Success! Mashup sent to {email}"
        except Exception as e:
            return f"Mashup created, but Email failed: {e}", 500

    except Exception as e:
        return f"An error occurred: {e}", 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)