import io
import mimetypes
from datetime import datetime
from django.conf import settings
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google.oauth2 import service_account

def get_drive_service():
    scopes = ["https://www.googleapis.com/auth/drive.file"]
    creds = service_account.Credentials.from_service_account_file(
        str(settings.GDRIVE_SERVICE_ACCOUNT_FILE),
        scopes=scopes
    )
    return build("drive", "v3", credentials=creds)

def upload_image_to_drive(file, folder_id=None, make_public=True):
    service = get_drive_service()
    ts = datetime.now().strftime("%Y%m%d%H%M%S")
    safe_name = f"{ts}_{getattr(file, 'name', 'upload')}"
    mime = getattr(file, "content_type", None) or mimetypes.guess_type(safe_name)[0] or "application/octet-stream"
    metadata = {"name": safe_name}
    parent = settings.GDRIVE_DEFAULT_FOLDER_ID

    if parent:
        metadata["parents"] = [parent]

    if hasattr(file, "open"):
        file.open("rb")

    if hasattr(file, "seek"):
        file.seek(0)

    media = MediaIoBaseUpload(file, mimetype=mime, resumable=True)
    created = service.files().create(
        body=metadata,
        media_body=media,
        fields="id, webViewLink, webContentLink",
        supportsAllDrives=True
    ).execute()

    if make_public:
        service.permissions().create(
            fileId=created["id"],
            body={"role": "reader", "type": "anyone"},
            supportsAllDrives=True
        ).execute()


    return created.get("webViewLink")
