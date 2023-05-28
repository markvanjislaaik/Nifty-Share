

class AwsConfig:

    DEFAULT_ROOT_FOLDER = 'testfolder'

    AWS_ACCESS_KEY = ""
    AWS_SECRET_ACCESS_KEY = ""
    AWS_BUCKET_NAME = ""
    AWS_DEFAULT_REGION = ""

    # for AWS in South Africa region "af-south-1" I've found it's important to provide
    # an endpoint url for any other region, you can comment out the endpoint url
    AWS_ENDPOINT_URL = "https://s3.af-south-1.amazonaws.com"

    # for Wasabi (AWS Backed) you NEED to provide an endpoint url
    # AWS_ENDPOINT_URL = "https://s3.us-east-1.wasabisys.com"


class GoogleConfig:

    DEFAULT_ROOT_FOLDER = 'testfolder'

    GGL_BUCKET_NAME = 'nifty-storage'
    GGL_CREDENTIALS_PATH = 'google.json'


class MailerConfig:

    # You can use either AWS SES or Gmail to send emails, just insert the details below,
    # the required variables are the same for either service but for AWS, 
    # the MAIL_HOST_USERNAME must be your ACCESS_KEY and the MAIL_PASSWORD must be your SECRET_ACCESS_KEY

    # MAIL_HOST_USERNAME = "access_key"
    # MAIL_PASSWORD = "secret_access_key"
    # MAIL_SMTP_SERVER = "email-smtp.eu-west-1.amazonaws.com"
    # MAIL_SMTP_PORT = 587
    # MAIL_HOST_SENDER_NAME = "The mame you want to show on the email"
    # MAIL_HOST_SENDER_ADDRESS = "youremail@example.com"


    # FOR GMAIL, since 'less secure apps' was deprecated, you need to use an App Password:
    # Make sure 2-Step Authentication is enabled on your account,
    # then generate a 16-char App Password for the app you're using to send email.
    # https://support.google.com/accounts/answer/185833?hl=en

    MAIL_HOST_USERNAME = "youremail@example.com"
    MAIL_PASSWORD = "your16charAppPassword"
    MAIL_SMTP_SERVER = "smtp.gmail.com"
    MAIL_SMTP_PORT = 587
    MAIL_HOST_SENDER_NAME = "The mame you want to show on the email"
    MAIL_HOST_SENDER_ADDRESS = "youremail@example.com"
