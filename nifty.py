import argparse
import os
from cloud.file_upload import FileUploaderClass
from zipper.file_zipper import FileZipper
from mailer.email_formatter import EmailTemplateRenderer
from mailer.email_sender import EmailSender

from settings import MailerConfig

import logging
import sys

from datetime import datetime, timedelta

log_format = ('[%(asctime)s] - %(levelname)s %(name)s %(funcName)s %(message)s')
logging.basicConfig(
    level=logging.INFO,
    format=log_format,
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Share a link to a file via email.')
    parser.add_argument('file_path', type=str, help='path/to/your/file')
    parser.add_argument('recipient', type=str, help='Email address of the recipient')
    parser.add_argument('-p', '--provider', type=str, default='AWS', help='Cloud provider (default: AWS)')
    parser.add_argument('-t', '--template', type=str, default='mailer.html', help='Email template filename (default: mailer.html)')
    args = parser.parse_args()

    # use Zipper if file_path is a directory
    if os.path.isdir(args.file_path):
        logger.info(f"Zipping {args.file_path}")
        zipper = FileZipper()
        files_list = zipper.list_files(args.file_path)
        prepped_file_path = zipper.create_zip(args.file_path, f"{os.path.basename(args.file_path)}.zip")
    else:
        files_list = [args.file_path]
        prepped_file_path = args.file_path

    # File upload and get shareable link
    uploader_factory = FileUploaderClass()
    uploader = uploader_factory.create_file_uploader(args.provider)
    logger.debug(f"Target Storage Subfolder: {uploader.root_folder}")
    uploader.upload_file(prepped_file_path, f"{uploader.root_folder}/{os.path.basename(prepped_file_path)}")
    link = uploader.get_shareable_link(f"{uploader.root_folder}/{os.path.basename(prepped_file_path)}")
    logger.debug(f"Shareable link: {link}")

    expiry_date = datetime.now() + timedelta(days=7)
    expiry_date = expiry_date.strftime("%A, %B %d, %Y")

    # Email formatting
    file_count = len(files_list)

    if file_count != 1:
        plural = "Files"
    else:
        plural = "File"

    mail_context = {
        "sender_name": MailerConfig.MAIL_HOST_SENDER_NAME,
        "file_basename": os.path.basename(prepped_file_path),
        "sender_address": MailerConfig.MAIL_HOST_SENDER_ADDRESS,
        "download_link": link,
        "recipent_email": args.recipient,
        "expiry_date": expiry_date,
        "file_size_mb": round(os.path.getsize(prepped_file_path) / 1024 / 1024, 2),
        "files_list": files_list,
        "file_count": file_count,
        "plural": plural
    }

    logger.info(f"Rendering email template {args.template}")
    template_renderer = EmailTemplateRenderer(template_dir='mail_templates')
    email_content = template_renderer.render_template(args.template, args.recipient, **mail_context)

    # Email send
    logger.info(f"Sending email to {args.recipient}")
    email_sender = EmailSender()
    email_sender.send_email(args.recipient, 'File Shared With You', email_content)

    # Clean up
    if prepped_file_path.endswith('.zip'):
        logger.info(f"Removing {prepped_file_path}")
        zipper.remove(prepped_file_path)