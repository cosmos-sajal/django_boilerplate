from botocore.exceptions import NoCredentialsError
from django.conf import settings

import boto3

from helpers.misc_helper import get_random_string


def upload_to_aws(file, folder='general'):
    """
    Uploads a given file to s3, if it is not able to
    it returns False, otherwise it returns the filepath
    of the uploaded file on s3
    """
    aws_access_key = getattr(settings, 'AWS_ACCESS_KEY')
    aws_secret_key = getattr(settings, 'AWS_SECRET_KEY')
    bucket_folders = getattr(settings, 'AWS_BUCKET_FOLDERS')
    bucket = getattr(settings, 'AWS_BUCKET')

    s3 = boto3.client(
        's3',
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key
    )

    try:
        s3_upload_path = bucket_folders[folder] + \
            get_random_string(20) + file.name
        s3.upload_fileobj(file, bucket, s3_upload_path)

        return s3_upload_path
    except FileNotFoundError:
        return False
    except NoCredentialsError:
        return False
