# app.py
from flask import Flask, request, jsonify, render_template
from email_processor import process_email
from threading import Thread
import os
import signal
import time
from config import WEBHOOK_URL

app = Flask(__name__, template_folder='templates')

responses = []
is_running = False
timer_seconds = 0
invoices_processed = 0
current_invoice_number = None
is_paused = False
process_thread = None

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    action = data.get('action')
    invoice_number = data.get('invoice_number')

    if action and invoice_number:
        responses.append(action)
        status = "Approved" if action == "Approve" else "Rejected"
        update_payload = {
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "themeColor": "0076D7",
            "summary": "Approval Status",
            "sections": [
                {
                    "activityTitle": f"Data {invoice_number} telah di {status}",
                }
            ]
        }

        # Update Excel status based on response
        from excel_utils import update_excel_status
        update_excel_status(invoice_number, status)
        requests.post(WEBHOOK_URL, json=update_payload)

    return jsonify({'status': 'Processed'}), 200

@app.route('/')
def index():
    return render_template('index6.html')

@app.route('/start', methods=['POST'])
def start():
    global is_running, is_paused, process_thread, timer_seconds, invoices_processed
    if not is_running or is_paused:
        is_running = True
        is_paused = False
        timer_seconds = int(request.form.get('hours', 0)) * 3600 + \
                        int(request.form.get('minutes', 0)) * 60 + \
                        int(request.form.get('seconds', 0))
        invoices_processed = 0
        if not process_thread or not process_thread.is_alive():
            process_thread = Thread(target=process_emails)
            process_thread.start()
    return jsonify({'status': 'Started', 'time': timer_seconds})

@app.route('/pause', methods=['POST'])
def pause():
    global is_paused
    is_paused = not is_paused
    return jsonify({'status': 'Paused' if is_paused else 'Resumed'})

@app.route('/stop', methods=['POST'])
def stop():
    global is_running
    is_running = False
    stop_flask_server()
    return jsonify({'status': 'Stopped'})

@app.route('/reset', methods=['POST'])
def reset():
    global timer_seconds, invoices_processed, is_running, is_paused
    timer_seconds = 0
    invoices_processed = 0
    is_running = False
    is_paused = False
    time.sleep(5)
    return jsonify({'status': 'Reset', 'time': timer_seconds})

@app.route('/status', methods=['GET'])
def status():
    return jsonify({'time_remaining': timer_seconds, 'invoices_processed': invoices_processed})

def stop_flask_server():
    os.kill(os.getpid(), signal.SIGINT)

def process_emails():
    global invoices_processed, timer_seconds
    while is_running and timer_seconds > 0:
        if not is_paused:
            process_email()
            invoices_processed += 1
            timer_seconds -= 1
            time.sleep(1)

if __name__ == '__main__':
    # Adjust public URL for deployment
    public_url = "https://your-pythonanywhere-username.pythonanywhere.com"
    app.run(port=5000)
