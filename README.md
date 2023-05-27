# Nifty Share

You can use Nifty Share to send small or large files with your own cloud provider.


## Usage

```bash
python nifty.py "path/to/file" -to recipient@example.com --provider AWS --template mailer.html

OR

python nifty.py "path/to/file" -to recipient@example.com --provider Google
```

Just create a `settings.py` file (in the same directory as `nifty.py`) that looks like this and use your own credentials:


*./settings.py*
```python

class AwsConfig:

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

    GGL_BUCKET_NAME = 'nifty-storage'
    GGL_CREDENTIALS_PATH = 'google.json'


class MailerConfig:

    # You can use either AWS SES or Gmail to send emails, just insert the details below,
    # the required variables are the same for either service but for AWS, 
    # the MAIL_HOST_USERNAME must be your ACCESS_KEY and the MAIL_PASSWORD must be your SECRET_ACCESS_KEY

    # FOR GMAIL, since 'less secure apps' was deprecated, you need to use an App Password:
    # Make sure 2-Step Authentication is enabled on your account,
    # then generate a 16-char App Password for the app you're using to send email.
    # https://support.google.com/accounts/answer/185833?hl=en

    MAIL_HOST_USERNAME = "aws_access_key OR youremail@example.com"
    MAIL_PASSWORD = "aws_secret_access_key OR your16charAppPassword"
    MAIL_SMTP_SERVER = "smtp.gmail.com OR email-smtp.eu-west-1.amazonaws.com"
    MAIL_SMTP_PORT = 587
    MAIL_HOST_SENDER_NAME = "The mame you want to show on the email"
    MAIL_HOST_SENDER_ADDRESS = "youremail@example.com"

```

***
## Email Templates

You can create your own custom templates, they're just Jinja2 formatted HTML, very similar to Django, however you'll need to use inline css as most email clients don't seem to allow CSS.


## Cloud Providers
AWS S3 is available as a Cloud Storage provider which also supports Wasabi (ensure you use the wasabi endpoint url).
Google Cloud Storage is also available, you'll need to need to create your service-account.json in the Google Cloud Console and then add the path to GoogleConfig.GGL_CREDENTIALS_PATH.

## To Do:

- [X] Improve coverage of logging and Exception handling
- [X] Add Google Cloud Storage
    - [ ] Adapt for Threaded Multipart Uploads for GCS
- [ ] Add Azure
- [ ] Add ability to select multiple files/folder and zip them before sending
- [ ] Add Database options for tracking your sends and expiry dates
    - [ ] Add ability to re-share expired links
