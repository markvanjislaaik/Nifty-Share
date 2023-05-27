import argparse
import os
from cloud.file_upload import FileUploaderClass
# from zipper.file_zipper import FileZipper
from mailer.email_formatter import EmailTemplateRenderer
from mailer.email_sender import EmailSender

from settings import MailerConfig

import logging
import sys

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

    parser = argparse.ArgumentParser(description='Share a file via email.')
    parser.add_argument('file_path', type=str, help='Path to the file')
    parser.add_argument('-to', '--recipient', type=str, help='Email address of the recipient')
    parser.add_argument('-p', '--provider', type=str, default='AWS', help='Cloud provider (default: AWS)')
    parser.add_argument('--template', type=str, default='mailer.html', help='Email template filename (default: mailer.html)')
    args = parser.parse_args()

    # File upload and get shareable link
    uploader_factory = FileUploaderClass()
    uploader = uploader_factory.create_file_uploader(args.provider)
    uploader.upload_file(args.file_path, f"testfolder/{os.path.basename(args.file_path)}")
    link = uploader.get_shareable_link(f"testfolder/{os.path.basename(args.file_path)}")
    logger.debug(f"Shareable link: {link}")

    # Email formatting
    mail_context = {
        "sender_name": MailerConfig.MAIL_HOST_SENDER_NAME,
        "file_basename": os.path.basename(args.file_path),
        "sender_address": MailerConfig.MAIL_HOST_SENDER_ADDRESS,
        "download_link": link,
        "recipent_email": args.recipient
    }

    template_renderer = EmailTemplateRenderer(template_dir='mail_templates')
    email_content = template_renderer.render_template(args.template, args.recipient, **mail_context)

    # Email send
    logger.info(f"Sending email to {args.recipient}")
    email_sender = EmailSender()
    email_sender.send_email(args.recipient, 'File Shared With You', email_content)