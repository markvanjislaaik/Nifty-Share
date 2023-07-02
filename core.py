import os
from datetime import datetime, timedelta

from integrations.file_upload import FileUploaderClass
from zipper.file_zipper import FileZipper
from mailer.email_formatter import EmailTemplateRenderer
from mailer.email_sender import EmailSender
from settings import MailerConfig
from database.database import get_db_connection

import logging_config
import logging

logger = logging.getLogger(__name__)


class NiftyCore:

    def __init__(self, file_path: str, recipient: str, provider: str='Google', template: str = 'mailer.html') -> None:
        self.file_path = file_path
        if not self.file_path:
            raise ValueError("File path is required.")

        self.recipient_email = recipient
        if not self.recipient_email:
            raise ValueError("Recipient is required.")
        
        self.target_file = f"{os.path.basename(self.file_path)}.zip"
        self.cloud_provider = provider
        self.template = template

        self.expiry_date_dt = datetime.now() + timedelta(days=7)
        self.expiry_date = self.expiry_date_dt.strftime("%A, %B %d, %Y")

        self.sender_name = MailerConfig.MAIL_HOST_SENDER_NAME
        self.sender_address = MailerConfig.MAIL_HOST_SENDER_ADDRESS
        self.file_basename = os.path.basename(self.file_path)

        self.zipped_here = False

    def _package(self) -> None:
        if os.path.isdir(self.file_path):
            if os.path.exists(self.target_file):
                os.remove(self.target_file)
            zipper = FileZipper()
            self.files_list = zipper.list_files(self.file_path)
            self.file_path = zipper.create_zip(self.file_path, self.target_file)
            self.zipped_here = True
        else:
            self.files_list = [self.file_path]

    def _upload(self) -> None:
        uploader_factory = FileUploaderClass()
        uploader = uploader_factory.create_file_uploader(self.cloud_provider)
        uploader.upload_file(self.file_path, f"{uploader.root_folder}/{os.path.basename(self.file_path)}")
        self.download_link = uploader.get_shareable_link(f"{uploader.root_folder}/{os.path.basename(self.file_path)}")

    def _complete_context(self) -> None:
        self.file_size_bytes = os.path.getsize(self.file_path)
        self.file_size_mb = round(self.file_size_bytes / 1024 / 1024, 2)
        self.file_count = len(self.files_list)

        if self.file_count != 1:
            self.plural = "Files"
        else:
            self.plural = "File"

        self.local_datetime = str(datetime.now())[:19]

    def _create_mail_content(self) -> str:
        self._complete_context()
        renderer = EmailTemplateRenderer(template_dir='mail_templates')
        return renderer.render_template(self.template, **self.as_dict())

    def _send_mail(self) -> None:
        sender = EmailSender()
        sender.send_email(self.recipient_email, 'File Shared With You', self._create_mail_content())

    def _save_to_db(self) -> None:
        connection = get_db_connection()
        with connection as db:
            db.insert_data("transfers", self.as_dict())

    def _cleanup(self) -> None:
        if self.zipped_here:
            try:
                os.remove(self.target_file)
            except FileNotFoundError:
                pass
            except PermissionError:
                logger.warning(f"Could not delete {self.target_file}")
            except Exception as e:
                logger.error(f"Could not delete {self.target_file} - {e}")

    def as_dict(self) -> dict:
        return self.__dict__

    def share(self) -> None:
        self._package()
        self._upload()
        self._send_mail()
        self._save_to_db()
        self._cleanup()
