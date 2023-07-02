import argparse
from datetime import datetime, timedelta

import logging_config
import logging

from core import NiftyCore

logger = logging.getLogger(__name__)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Share a link to a file via email.')
    parser.add_argument('file_path', type=str, help='path/to/your/file')
    parser.add_argument('recipient', type=str, help='Email address of the recipient')
    parser.add_argument('-p', '--provider', type=str, default='Google', help='Cloud provider (default: Google)')
    parser.add_argument('-t', '--template', type=str, default='mailer.html', help='Email template filename (default: mailer.html)')
    args = parser.parse_args()

    nifty = NiftyCore(**vars(args))
    nifty.share()
