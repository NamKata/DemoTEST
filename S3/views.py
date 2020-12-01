
from django.views.generic.edit import FormView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render
from rest_framework.decorators import api_view
import boto3
import uuid
import os
from Main import settings
from django.core.files.storage import FileSystemStorage
from .utils import handle_check_exists_bucket, handle_create_bucket_request, \
    handle_upload_mutiplefile_in_bucket, handle_check_is_empty, handle_presigned_url, \
    handle_download_file_s3, handle_presigned_url_set_timeout
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

@api_view(['GET'])
def getBucketinS3(request):
    s3 = boto3.resource('s3')
    contains = []
    # Print out bucket names
    for bucket in s3.buckets.all():
        print(bucket.name)
        contains.append(bucket.name)
    return Response(contains, status=status.HTTP_201_CREATED)

@api_view(['POST'])
def uploadFile(request):
    s3 = boto3.resource('s3')
    if request.method == "POST":
        for bucket in s3.buckets.all():
            # print(request.FILES['file'])
            if bucket.name == 'django-demo-1234':
                print(bucket)
                file_name = request.FILES['file']
                if upload_to_aws(file_name, bucket.name, 'media/posts/None/') == True:
                    return Response(status=status.HTTP_200_OK)
                return Response(status=status.HTTP_400_BAD_REQUEST) 

def upload_to_aws(local_file, bucket, s3_file):
    s3 = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)

    try:
        s3.upload_file(local_file, bucket, s3_file)
        print("Upload Successful")
        return True
    except FileNotFoundError:
        print("The file was not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False

@api_view(['POST'])
def createBucket(request):
    bucketname = request.POST['bucket']
    filename = request.FILES['file']
    print("Bucket name : ", bucketname)
    s3 = boto3.resource('s3')
    client = boto3.client('s3')
    bucket = bucketname+"-%s"% uuid.uuid4()
    print(bucket)
    responseBucket= client.create_bucket(Bucket=bucket, CreateBucketConfiguration={
        'LocationConstraint':settings.AWS_S3_REGION_NAME
    },ACL=settings.AWS_DEFAULT_ACL
    )
    fs = FileSystemStorage()
    # createFile = fs.save(filename.name, filename)
    # responseUploadFile =fs.url(createFile)
    return Response(responseBucket,status=status.HTTP_201_CREATED)

@api_view(['POST'])
def upload_file_demo(request):
    s3 = boto3.client('s3')
    files = request.FILES['file']
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    link = os.path.join(BASE_DIR)
    fs = FileSystemStorage()
    downFile =fs.save(files.name, files)
    urlImg = link+fs.url(downFile)
    content = files.name

    print(urlImg)
    responses =s3.upload_file(urlImg,'django-demo-1234',content)
    return Response(responses, status= status.HTTP_201_CREATED)
@api_view(['POST'])
def upload_mutiple_file(request):
    s3=boto3.client('s3')
    files = request.FILES.getlist('files')
    print(files)
    link = os.path.join(BASE_DIR)
    fs = FileSystemStorage()
    for photo in files:
        try:
            downFile =fs.save(photo.name, photo)
            urlImg = link+fs.url(downFile)
            content = photo.name
            responses =s3.upload_file(urlImg,'django-demo-1234',content)
        except Exception as ex:
            print(ex)
            return Response(status=status.HTTP_400_BAD_REQUEST)
    return Response(status=status.HTTP_201_CREATED)

def upload_final(request):
    print(BASE_DIR)
    if request.method == "POST":
        bucketname = request.POST['bucket']
        files = request.FILES.getlist('files')
        print(files)
        s3 = boto3.resource('s3')
        # Check exists bucket 
        # print(s3.Bucket(bucketname) in s3.buckets.all())
        if (s3.Bucket(bucketname) in s3.buckets.all()) == True:
            return HttpResponse("Da ton tai")
        else:
            try:
                s3.create_bucket(Bucket=bucketname, CreateBucketConfiguration={
                    'LocationConstraint':settings.AWS_S3_REGION_NAME
                },ACL=settings.AWS_DEFAULT_ACL)
            except Exception as e:
                print(e)
                return HttpResponse(e)
        # for bucket in s3.buckets.all():
        #     print(bucket.name)
        #     if bucket.name == bucketname:
        #         return HttpResponse("Loi1")
        try:
            client = boto3.client('s3')
            link = os.path.join(BASE_DIR)
            fs = FileSystemStorage()
            for photo in files:
                try:
                    downFile =fs.save(photo.name, photo)
                    urlImg = link+fs.url(downFile)
                    content = photo.name
                    client.upload_file(urlImg,bucketname,content)
                except Exception as ex:
                    print(ex)
                    return HttpResponse("Loi3")
            return redirect('/')
        except Exception as ex:
            print(ex)
            return HttpResponse("Loi4")
    else:
        return render(request,'upload.html')

def search_bucket(request):
    if request.method == "POST":
        bucket = request.POST['search']
        if handle_check_exists_bucket(bucket) == True:
            return redirect('list', bucket)
        else:
            return render(request, 'search_bucket.html', {'message':True})
    else:
        return render(request, 'search_bucket.html')
def list_image(request, bucket):
    result = {
        'Success':False,
        'message':''
    }
    # -- generate presigned post
    # pre_sign= handle_presigned_url(bucket)
    # -- generate presigned url
    pre_sign = handle_presigned_url_set_timeout(bucket)
    print(pre_sign)
    if pre_sign is None:
        return Response(result, status= status.HTTP_400_BAD_REQUEST)
    else:
        # -- generate presigned post
        # url =[]
        result['Success'] = True 
        result['message']=''
        # for pre in pre_sign:
        #     link = '%s%s'%(pre['url'], pre['fields']['key'])
        #     # print(link)
        #     url.append(link)
        # result['data']= {
        #     'urlimages':url,
        #     'bucket':bucket,
        #     'presigned':pre_sign
        # }

        # -- generate presinged url set time out
        result['data']={
            'urlimages':pre_sign,
            'bucket':bucket
        }

        return render(request, 'listImages.html', result)


def upload_in_request(request):
    # Config boto3, aws key+ aws credentital -> done
    # Create a templates have upload form -> done
    # Create view function  -> done
    # Create handle request from templates
    # Create a bucket can contain files
    # When user upload file from template response the file to binary file send to view function, function upload to s3
    # Upload then return Success or 
    if request.method == "POST":
        bucketname = request.POST['bucket']
        files = request.FILES.getlist('files')
        
        if handle_check_is_empty(files, bucketname) == False:
            return render(request,'upload.html', {'message':"Empty!"})

        if handle_upload_mutiplefile_in_bucket(files, bucketname.lower()) == True:
            return render(request,'upload.html', {'message':"Success!"})
        else:
            return render(request,'upload.html', {'message':"Faluire!"})
    else:
        return render(request,'upload.html')


@api_view(['POST'])
def list_url_demo(request):
    result = {
        'Success':False,
        'message':''
    }
    bucket = request.POST['bucket']
    pre_sign= handle_presigned_url_set_timeout(bucket)
    print(pre_sign)
    # return Response(pre_sign)
    if pre_sign is None:
        return Response(result, status= status.HTTP_400_BAD_REQUEST)
    else:
        url =[]
        result['Success'] = True 
        result['message']=''
        # for pre in pre_sign:
        #     link = '%s%s'%(pre['url'], pre['fields']['key'])
        #     url.append(link)
        result['data']= {
            'urlimages':pre_sign,
            'bucket':bucket,
            'presigned':pre_sign
        }
        return Response(result, status = status.HTTP_200_OK)

def download_file(request, bucket):
    if handle_download_file_s3(bucket) == True:
        return redirect('test')
    return redirect('list', bucket)
import json
@api_view(['POST'])
def get_location_request(request):
    upload = request.FILES['files']
    # path= os.path.abspath(upload.name)
    path = json.dumps(upload)
    print(path)
    return Response(path)