
# gdrive_connector.py
# This is an example that lists files in a Google Drive folder and downloads text content for ingestion.
# You need to create OAuth credentials and place the JSON in path from config.GOOGLE_CREDENTIALS_JSON_PATH
from googleapiclient.discovery import build
from google.oauth2 import service_account
from ..config import GOOGLE_CREDENTIALS_JSON_PATH
from ..vector_store import upsert_document
import io
from googleapiclient.http import MediaIoBaseDownload

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def list_and_ingest(folder_id=None, page_size=50):
    creds = service_account.Credentials.from_service_account_file(GOOGLE_CREDENTIALS_JSON_PATH, scopes=SCOPES)
    service = build('drive', 'v3', credentials=creds)
    q = f"'{folder_id}' in parents" if folder_id else None
    results = service.files().list(q=q, pageSize=page_size, fields="files(id,name,mimeType)").execute()
    files = results.get('files', [])
    ingested = []
    for f in files:
        fid = f['id']
        name = f['name']
        mime = f.get('mimeType','')
        # For Google Docs, export as text
        if 'google-apps.document' in mime:
            request = service.files().export_media(fileId=fid, mimeType='text/plain')
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done=False
            while not done:
                status, done = downloader.next_chunk()
            text = fh.getvalue().decode('utf-8')
            upsert_document(name, text, {'source':'gdrive', 'id': fid})
            ingested.append(name)
    return ingested
