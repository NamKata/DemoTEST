import boto3
import logging
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
import re
import os
from django.core.files.storage import FileSystemStorage
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


session = boto3.Session(aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                        region_name=settings.AWS_S3_REGION_NAME)

s3 = session.client('s3')
s3_rs = boto3.resource('s3')
sqs = session.client('sqs')

RE_S3_URL = re.compile(r'^s3://(?P<bucket>[^/]+)/(?P<key>.*)$')

def handle_check_is_empty(files, bucket):
    if len(files) == 0 or bucket == "" or bucket is None or files is None:
        return False
    else:
        return True

def handle_check_exists_bucket(bucket):
    if (s3_rs.Bucket(bucket) in s3_rs.buckets.all()) == True:
        return True
    return False
def handle_create_bucket_request(bucket):
    if handle_check_exists_bucket(bucket) == True:
        return False
    else:
        try:
            s3_rs.create_bucket(Bucket= bucket, CreateBucketConfiguration={
                        'LocationConstraint':settings.AWS_S3_REGION_NAME
                    },ACL=settings.AWS_DEFAULT_ACL)
            return True
        except Exception as e:
            print(e)
            return None

def handle_upload_mutiplefile_in_bucket(files, bucket):
    link = os.path.join(BASE_DIR)
    fs = FileSystemStorage()
    if handle_create_bucket_request(bucket) is None:
        return False;
    else:
        for photo in files:
                try:
                    downFile =fs.save(photo.name, photo)
                    urlImg = '%s%s'%(link,fs.url(downFile))
                    content = photo.name
                    s3.upload_file(urlImg,bucket,content)
                except Exception as ex:
                    print(ex)
                    return None
        return True