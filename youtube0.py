import urllib
import json
import requests

#https://www.googleapis.com/youtube/v3/videos?part=statistics&id={YOUR_VIDEO_ID}&key={YOUR_API_KEY}

api_key='AIzaSyBaJ1dGoRdqwnMqkxERJDax2avnKsjkHhg'   #constant for all

def store_youtube_account_data(c_tokken,channel_link):
    x=channel_link.split('/')
    channel_name=x[-1]
    url='https://www.googleapis.com/youtube/v3/channels?part=statistics&forUsername='+channel_name+'&key='+api_key
    uResponse = requests.get(url)
    Jresponse = uResponse.text
    d = json.loads(Jresponse)
    subscriber_count=d['items'][0]['statistics']['subscriberCount']
    if int(subscriber_count)>150:
        user=Influencer_details.query.filter_by(c_tokken=c_tokken).first()
        yt_user=Youtube(influencer_id=user.influencer_id,channel_link=channel_link,subscriber_count=subscriber_count,verified=True)
        db.session.add(yt_user)
        db.session.commit()
        return True
    else:
        return False

def getyoutubevideodata(c_tokken,link):
    x=link.split('/')
    video_id=x[-1]
    url='https://www.googleapis.com/youtube/v3/videos?part=statistics&id='+video_id+'&key='+api_key
    uResponse = requests.get(url)
    Jresponse = uResponse.text
    d = json.loads(Jresponse)
    viewCount=(d['items'][0]['statistics']['viewCount'])
    likeCount=(d['items'][0]['statistics']['likeCount'])
    user=Influencer_details.query.filter_by(c_tokken=c_tokken).first()
    yt_post=Posts_done(inf_inv_id=user.influencer_id,platform=4,post_url=link,likes=likeCount,views=viewCount)
    db.session.add(yt_post)
    db.session.commit()
    
