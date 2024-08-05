# email_processor.py
import imaplib
import email
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from io import BytesIO
from pdf2image import convert_from_bytes
import json
import ast
import requests
from config import EMAIL_HOST_IMAP, EMAIL_USER, EMAIL_PASS, DRIVE_FOLDER_ID
from gdrive_utils import save_attachment_to_drive
from gemini_utils import convert_pdf_to_jpeg_in_memory, gemini_output, SYSTEM_PROMPT, USER_PROMPT
from excel_utils import input_to_excel2, send_approval_request

def process_email():
    mail = imaplib.IMAP4_SSL(EMAIL_HOST_IMAP)
    mail.login(EMAIL_USER, EMAIL_PASS)
    mail.select('inbox')

    _, data = mail.search(None, '(UNSEEN SUBJECT "invoice")')
    mail_ids = data[0].split()

    for mail_id in mail_ids:
        _, data = mail.fetch(mail_id, '(RFC822)')
        msg = email.message_from_bytes(data[0][1])
        for part in msg.walk():
            if part.get_content_maintype() == 'multipart':
                continue
            if part.get('Content-Disposition') is None:
                continue
            if part.get_filename().endswith('.pdf'):
                attachment = part.get_payload(decode=True)

                # Convert PDF to JPEG
                images = convert_pdf_to_jpeg_in_memory(attachment)

                # Save PDF to Google Drive
                # file_id = save_attachment_to_drive(attachment, part.get_filename(), DRIVE_FOLDER_ID)

                for image in images:
                    output_str = gemini_output(image, SYSTEM_PROMPT, USER_PROMPT)
                    output_str = output_str.replace('`json', '').replace('`', '').strip()
                    data_dict = ast.literal_eval(output_str)

                    total_str = data_dict['Total'].replace("$", "").replace(",", "")
                    data_dict['Total'] = float(total_str)
                    data_dict['Bill to'] = data_dict['Bill to'].split('\n')[0]

                    current_invoice_number = data_dict['Invoice Number']
                    date = data_dict['Date']
                    due_date = data_dict['Due Date']
                    bill_to = data_dict['Bill to']
                    total = data_dict['Total']

                    input_to_excel2(current_invoice_number, date, due_date, total, bill_to)
                    send_approval_request(current_invoice_number, date, due_date, total, bill_to)

    mail.logout()
