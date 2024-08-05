# gdrive_utils.py
# from googleapiclient.discovery import build
# from googleapiclient.http import MediaIoBaseUpload
# from io import BytesIO
# from config import GOOGLE_CREDENTIALS_FILE, GOOGLE_API_KEY

# def get_drive_service():
#     scopes = ['https://www.googleapis.com/auth/drive']
#     credentials = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_CREDENTIALS_FILE, scopes)
#     return build('drive', 'v3', credentials=credentials)

# drive_service = get_drive_service()

# def save_attachment_to_drive(attachment, filename, folder_id):
#     file_metadata = {'name': filename, 'parents': [folder_id]}
#     media = MediaIoBaseUpload(BytesIO(attachment), mimetype='application/pdf', resumable=True)
#     file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
#     return file.get('id')
