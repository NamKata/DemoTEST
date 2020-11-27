from django.urls import path, include
from . import views
urlpatterns=[
    # path('', views.Uploads.as_view(), name='upload'),
    path('', views.upload_final, name='1123'),
    path('getBucket/', views.getBucketinS3, name='get'),
    path('postFile/', views.uploadFile, name='post'),
    path('createBucket/', views.createBucket, name='create'),
    path('uploaddemo/', views.upload_file_demo, name='postupload'),
    path('upload-N-N-Images/', views.upload_mutiple_file, name ='upload-mutiple'),
    path('search_bucket/',views.search_bucket, name='search'),
    path('list/', views.list_image, name='list'),
    path('test/', views.upload_in_request, name='test')
]