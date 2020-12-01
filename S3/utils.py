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
            s3.put_public_access_block(
                        Bucket=bucket,
                        PublicAccessBlockConfiguration={
                        'BlockPublicAcls': False,
                        'IgnorePublicAcls': False,
                        'BlockPublicPolicy': False,
                        'RestrictPublicBuckets': False
                        })
            return True
        except Exception as e:
            print(e)
            return None

def handle_upload_mutiplefile_in_bucket(files, bucket):
    link = os.path.join(BASE_DIR)+'/media/'+bucket
    fs = FileSystemStorage(BASE_DIR+'/media/'+bucket)
    if handle_create_bucket_request(bucket) is None:
        return False;
    else:
        for photo in files:
            try:
                downFile =fs.save(photo.name.replace(' ','_').replace('-','_').replace('(','_'), photo)
                print(fs.url(downFile))
                urlImg = '%s%s'%(link,fs.url(downFile).replace('/media',''))
                content = photo.name.replace(' ','_').replace('-','_').replace('(','_')
                s3.upload_file(urlImg,bucket,content,ExtraArgs={"ACL": "public-read"})
            except Exception as ex:
                print(ex)
                return None
        return True

def handle_presigned_url(bucket):
    if handle_check_exists_bucket(bucket) == True:
        url =[]
        buckets = s3_rs.Bucket(bucket)
        for k in buckets.objects.all():
            url.append(create_presigned_url(bucket, k.key))
        return url
    return None
def handle_presigned_url_set_timeout(bucket):
    if handle_check_exists_bucket(bucket) == True:
        url =[]
        buckets = s3_rs.Bucket(bucket)
        for k in buckets.objects.all():
            url.append(create_presigned_url_set_timeout(bucket, k.key))
        return url
    return None
def create_presigned_url(bucket, object_name):
    try:
        response = s3.generate_presigned_post(bucket, object_name)
    except Exception as e:
        print(e)
        return None
    return response
def create_presigned_url_set_timeout(bucket, object_name):
    try:
        # ExpiresIn = 1 min
        response = s3.generate_presigned_url('get_object', Params={'Bucket':bucket,'Key':object_name}, ExpiresIn=60)
    except Exception as e:
        print(e)
        return None
    return response
def handle_download_file_s3(bucket):
    if handle_check_exists_bucket(bucket) == True:
        bucket_obj = s3_rs.Bucket(bucket)
        try:
            for file in bucket_obj.objects.all():
                bucket_obj.download_file(file.key, BASE_DIR+"/media/download/"+file.key)
            return True
        except Exception as e:
            print(e)
            return False
    return None

