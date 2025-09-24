from django.core.files.storage import FileSystemStorage
from django.conf import settings
from datetime import datetime

def upload_file_to_local(file):
    fs = FileSystemStorage()
    filename = fs.save(datetime.now().strftime("%Y%m%d%H%M%S") + file.name, file)
    return fs.url(filename)
