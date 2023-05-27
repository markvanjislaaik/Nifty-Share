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

    provider = 'AWS'
    file_to_send = 'upload_tests/testfile5.txt'
    recipient_email = 'markvanjislaaik@gmail.com'
    template = 'mailer.html'
    file_basename = os.path.basename(file_to_send)

    # File upload and get shareable link
    f = FileUploaderClass()
    uploader = f.create_file_uploader(provider)
    uploader.upload_file(file_to_send, f"testfolder/{file_basename}")
    link = uploader.get_shareable_link(f"testfolder/{file_basename}")
    logger.debug(f"Shareable link: {link}")

    # Email templating
    mail_context = {
        "sender_name": MailerConfig.SES_SENDER_NAME,
        "file_basename": os.path.basename(file_to_send),
        "sender_address": MailerConfig.SES_SENDER_ADDRESS,
        "download_link": link,
        "recipent_email": recipient_email
    }
    
    template_renderer = EmailTemplateRenderer(template_dir='mail_templates')
    email_content = template_renderer.render_template(template, recipient_email, **mail_context)

    with open('rendered_email.html', 'w') as f:
        f.write(email_content)

    # Email sending
    email_sender = EmailSender()
    email_sender.send_email(
        recipient_email, 'File Shared With You', email_content
        # attachments=[zip_path]
    )