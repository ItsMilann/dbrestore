import os, subprocess
import datetime
from rest_framework.decorators import action
from rest_framework.exceptions import NotAcceptable
from rest_framework.viewsets import ViewSet
from django.apps import apps
from django.utils.translation import gettext_lazy as _
from rest_framework.response import Response
from typing import List


class BackupRestore(ViewSet):
    queryset = None
    permission_classes = []

    def list(self, request, *args, **kwargs):
        backups = os.listdir("media/backup/")
        return Response(backups, status=200)

    @staticmethod
    def _exclude_tables(tables: List, action: str):
        join = lambda x: ",".join(x)
        if action == "exclude":
            return join(tables)  # fmt: skip
        models = apps.get_models()
        tnames = [model._meta.db_table for model in models]
        excluded_tables = list(filter(lambda x: x not in tables, tnames))
        return join(excluded_tables)

    @action(["GET"], detail=False)
    def tables(self, *args, **kwargs):
        models = apps.get_models()
        data = [
            {"name": model._meta.verbose_name, "table": model._meta.db_table} for model in models
        ]
        return Response(data, status=200)

    @action(["POST"], detail=False, url_path="perform-backup")
    def backupdb(self, request):
        tables = request.data.get("tables", [])
        action = request.data.get("action", "include")
        date = datetime.datetime.now().strftime("%Y%m%d%H%M")
        filename = f"backup-{date}.sql"
        cmd = f"python manage.py dbbackup -o={filename}"
        if tables:
            exclude = self._exclude_tables(tables, action)
            cmd = f"{cmd} -x={exclude}"
        subprocess.run(cmd, shell=True, check=True)
        # management.call_command(cmd)
        path = f"/media/backup/{filename}"
        uri = request.build_absolute_uri(path)
        return Response({"path": uri}, status=200)

    @action(["POST"], detail=False, url_path="perform-restore")
    def restoredb(self, request):
        filename = request.data.get("filename")
        cmd = f"python manage.py dbrestore -i={filename} --noinput"
        try:
            with open("backup.stderr.log", "w+") as file:
                subprocess.run(cmd, shell=True, check=True, stderr=file)
                return Response({}, status=200)
        except subprocess.CalledProcessError:
            raise NotAcceptable(
                _(
                    "Something went wrong while restoring backup. Please, use different backup file. Check backup.stderr.log for more information."
                )
            )
