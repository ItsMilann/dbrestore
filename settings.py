import datetime

def backup_filename(databasename, servername, datetime, extension, content_type="db"):
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M")
    return f"backup-{timestamp}.sql"


EXTENSION = "sql"
CONNECTOR="dbbackup.db.postgresql.PgDumpConnector"
DBBACKUP_FILENAME_TEMPLATE = backup_filename
DBBACKUP_STORAGE = "django.core.files.storage.FileSystemStorage"
DBBACKUP_STORAGE_OPTIONS = {"location": "/usr/src/app/media/backup/"}