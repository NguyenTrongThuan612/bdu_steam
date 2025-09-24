from django.core.files.storage import FileSystemStorage
from django.conf import settings

def upload_file_to_local(file):
    fs = FileSystemStorage()
    filename = fs.save(file.name, file)
    return fs.url(filename)
