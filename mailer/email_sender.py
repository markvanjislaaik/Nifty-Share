import logging

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

from settings import MailerConfig

logger = logging.getLogger(__name__)

class EmailSender:

    def __init__(self) -> None:
        self.host_access_key = MailerConfig.MAIL_HOST_USERNAME
        self.sender_email = MailerConfig.MAIL_HOST_SENDER_ADDRESS
        self.sender_password = MailerConfig.MAIL_PASSWORD
        self.smtp_server = MailerConfig.MAIL_SMTP_SERVER
        self.port = MailerConfig.MAIL_SMTP_PORT

    def send_email(self, recipient_email: str, subject: str, content: str, 
                   attachments: list[str]=None) -> None:

        message = MIMEMultipart('alternative')
        message['From'] = self.sender_email
        message['To'] = recipient_email
        message['Subject'] = subject

        message.attach(MIMEText(content, 'html'))

        if attachments:
            for attachment in attachments:
                part = MIMEBase('application', 'octet-stream')
                with open(attachment, 'rb') as file:
                    part.set_payload(file.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename= {attachment}')
                message.attach(part)

        with smtplib.SMTP(self.smtp_server, self.port) as server:
            server.ehlo()
            server.starttls()
            try:
                server.login(self.host_access_key, self.sender_password)
            except smtplib.SMTPAuthenticationError as e:
                logger.critical(f"Authentication error, please check your credentials: {e}")
                return
            except Exception as e:
                logger.critical(f"Authentication error: {e}")
                return
            
            try:
                server.send_message(message)
            except Exception as e:
                logger.critical(f"Error sending email: {e}")
                return


if __name__ == '__main__':
    # Example usage:
    email_sender = EmailSender()
    email_sender.send_email('recipient@example.com', 'File Sharing', 'Please find attached the file.', attachments=['archive.zip'])