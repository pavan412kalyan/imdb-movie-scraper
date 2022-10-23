import json
import requests
from bs4 import BeautifulSoup
'''
Lambda function for scraping video url.

{
  "video_id": "vi324468761"
}

'''
def lambda_handler(event, context):
    video_id = event['video_id']
    video_url= "https://www.imdb.com/video/"+video_id
    print(video_url)
    try :
        r = requests.get(url=video_url)
        soup = BeautifulSoup(r.text, 'html.parser')
        script =soup.find("script",{'type': 'application/json'})
        json_object = json.loads(script.string)
        # print(json_object["props"]["pageProps"]["videoPlaybackData"]["video"]["playbackURLs"])
        videos = json_object["props"]["pageProps"]["videoPlaybackData"]["video"]["playbackURLs"]
        # links video quality order auto,1080,720

        for video in videos[1:] :
            video_link = video["url"]
            print("video_link",video_link)  
            break
        Video_info= videos[1:]
        video_link = Video_info[1]["url"]
        output=video_link
    except Exception as e:
        output = {'error' : f'video not found, check here https://www.imdb.com/video/{video_id}', 'stack': str(e)}
    return {
        'statusCode': 200,
        'body':  {'url': output}
    }
