# -*- coding: utf-8 -*-

#pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib

import datetime
from Google import Create_Service
from googleapiclient.http import MediaFileUpload

def create_service() :
    CLIENT_SECRET_FILE = 'client_secret.json'
    API_NAME = 'youtube'
    API_VERSION = 'v3'
    SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
    service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)
    
    return service
def video_body(title,description,tags_list,privacyStatus):
    request_body = {
        'snippet': {
            'categoryI': 19,
            'title': title,
            'description': description,
            'tags': tags_list
        },
        'status': {
            'privacyStatus': privacyStatus,
            'selfDeclaredMadeForKids': False 
        },
        'notifySubscribers': False
    }
    return request_body
        
def upload_video_to_youtube(videopath,imagepath,title,description,tags_list,privacyStatus):
    service = create_service()
    mediaFile = MediaFileUpload(videopath)
    imageFile = MediaFileUpload(imagepath)
    request_body=video_body(title,description,tags_list,privacyStatus)
    response_upload = service.videos().insert(
        part='snippet,status',
        body=request_body,
        media_body=mediaFile
    ).execute()
    service.thumbnails().set(
        videoId=response_upload.get('id'),
        media_body= imageFile
    ).execute()
    
#upload_video_to_youtube(videopath='trailers/tt0095953/tt0095953.mp4',imagepath='trailers/tt0095953/tt0095953.jpg',title="test",description="test",tags_list=['test','testt'],privacyStatus='Private')    