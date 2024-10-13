from typing import List

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import (
    MediaFileUpload,
    MediaIoBaseUpload,
)


class GoogleDriveServiceGenerator:
    def __init__(self, account_file_path: str, scopes: List[str]):
        self.account_file_path = account_file_path
        self.scopes = scopes

    def generate_service(self):
        creds = Credentials.from_service_account_file(
            filename=self.account_file_path,
            scopes=self.scopes,
        )
        service = build('drive', 'v3', credentials=creds)
        return service


class GoogleDriveService:
    def __init__(self, service):
        self.service = service

    def get_file_list(self, query: str, page_size: int = 1000) -> List[dict]:
        results = self.service.files().list(
            q=query,
            pageSize=page_size,
            fields="nextPageToken, files(id, name, mimeType)"
        ).execute()
        items = results.get('files', [])
        return items

    def upload_file_by_file_path(self, file_name: str, upload_target_file_path: str, upload_drive_folder_target: str) -> str:
        file_metadata = {
            'name': file_name,
            'parents': [upload_drive_folder_target]
        }
        media = MediaFileUpload(upload_target_file_path, mimetype='application/octet-stream')
        file = self.service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        return file.get('id')

    def upload_file_by_file_obj(self, file_obj, upload_drive_folder_target: str) -> str:
        file_metadata = {
            'name': file_obj.name,
            'parents': [upload_drive_folder_target]
        }
        media = MediaIoBaseUpload(file_obj, mimetype='application/octet-stream')
        file = self.service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        return file.get('id')

    def delete_file(self, file_id: str):
        self.service.files().delete(fileId=file_id).execute()
