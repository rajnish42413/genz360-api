from flask import Flask,render_template,redirect,url_for,request,jsonify,send_file,session,flash
from flask import send_file
from models import *
from flask import json
import uuid
import random
import string
from datetime import datetime,timedelta
from flask_marshmallow import Marshmallow
from passlib.hash import sha256_crypt
import json
import requests
from flask_migrate import Migrate
import base64
import io
import csv
import twitterapi as twapi
import youtube0 as ytapi
from paypalpay import Createpaypalpayment
from pricing import calc_price
from paytm import *
import time
from exponent_server_sdk import DeviceNotRegisteredError
from exponent_server_sdk import PushClient
from exponent_server_sdk import PushMessage
from exponent_server_sdk import PushResponseError
from exponent_server_sdk import PushServerError
from requests.exceptions import ConnectionError
from requests.exceptions import HTTPError
from threading import Thread
from functools import wraps
from flask_sqlalchemy import SQLAlchemy


app=Flask(__name__)

#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:rajnish123@localhost/genz360_db'
#db = SQLAlchemy(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:rajnish123@localhost/genz360_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
db.init_app(app)
db.app=app

ma=Marshmallow(app)

@app.route('/')
def testdb():
    return '<h1>It works.</h1>'
  

@app.route('/messages', methods = ['POST'])
def api_message():

    if request.headers['Content-Type'] == 'text/plain':
        return "Text Message: " + request.data

    elif request.headers['Content-Type'] == 'application/json':
        return "JSON Message: " + json.dumps(request.json)

    elif request.headers['Content-Type'] == 'application/octet-stream':
        f = open('./binary', 'wb')
        f.write(request.data)
        f.close()
        return "Binary message written!"

    else:
        return "415 Unsupported Media Type ;)"

class Brand_details_S(ma.ModelSchema):
	class Meta:
		model = Brand_details

class Spoc_details_S(ma.ModelSchema):
	class Meta:
		model = Spoc_details

class Influencer_details_S(ma.ModelSchema):
	class Meta:
		model = Influencer_details

# class Facebook_S(ma.ModelSchema):
#     class Meta:
#         model = Facebook

# class Instagram_S(ma.ModelSchema):
#     class Meta:
#         model = Instagram

# class Twitter_S(ma.ModelSchema):
#     class Meta:
#         model = Twitter

# class Youtube_S(ma.ModelSchema):
#     class Meta:
#         model = Youtube

class Otp_details_S(ma.ModelSchema):
	class Meta:
		model = Otp_details

# class Influencers_required_S(ma.ModelSchema):
#     class Meta:
#         model = Influencers_required

class Influencers_involved_S(ma.ModelSchema):
	class Meta:
		model = Influencers_involved

class Posts_done_S(ma.ModelSchema):
	class Meta:
		model = Posts_done

class Campaign_S(ma.ModelSchema):
	class Meta:
		model = Campaign

class Location_S(ma.ModelSchema):
	class Meta:
		model = Location


# class Platform_S(ma.ModelSchema):
#     class Meta:
#         model = Platform

class Campaign_posts_S(ma.ModelSchema):
	class Meta:
		model = Campaign_posts

class Pricing_details_S(ma.ModelSchema):
	class Meta:
		model = Pricing_details

class Payments_S(ma.ModelSchema):
	class Meta:
		model = Payments

class Notifications_S(ma.ModelSchema):
	class Meta:
		model = Notifications

class Rel_influencer_notification_S(ma.ModelSchema):
	class Meta:
		model = Rel_influencer_notification

class Rel_brand_notification_S(ma.ModelSchema):
	class Meta:
		model = Rel_brand_notification


status={
    0:"Pending",
    1:"Active",
    2:"Completed"
}


#Push Notification 
def send_push_notif_brand(brand,msg):
	try:
		if brand.not_token:
			send_push_message(brand.not_token,msg)
			nn=Notifications(message=msg)
			db.session.add(nn)
			rr=Rel_brand_notification()
			db.session.add(rr)
			brand.notify.append(rr)
			nn.notifications_for_brand.append(rr)
			db.session.commit()
		else:
			pass
	except:
		pass

def send_push_notif(inf,msg):
	try:
		if inf.not_token:
			send_push_message(inf.not_token,msg)
			nn=Notifications(message=msg)
			db.session.add(nn)
			rr=Rel_influencer_notification()
			db.session.add(rr)
			inf.notify.append(rr)
			nn.notifications_for_inf.append(rr)
			db.session.commit()
		else:
			pass
	except:
		pass

@app.route("/inf-not-token",methods=["GET","POST"])
def inf_notif_token():
	data=request.json
	tokken=data["tokken"]
	inf=Influencer_details.query.filter_by(c_tokken=tokken).first()
	if inf.not_token:	
		return jsonify(valid=True)
	else:
		return jsonify(valid=False)

def send_push_message(token, message, extra=None):
	try:
		response = PushClient().publish(
			PushMessage(to=token,
						body=message,
						data=extra,
						channel_id='reminders'))
	except PushServerError as exc:
		# Encountered some likely formatting/validation error.
		rollbar.report_exc_info(
			extra_data={
				'token': token,
				'message': message,
				'extra': extra,
				'errors': exc.errors,
				'response_data': exc.response_data,
			})
		raise
	except (ConnectionError, HTTPError) as exc:
		# Encountered some Connection or HTTP error - retry a few times in
		# case it is transient.
		rollbar.report_exc_info(
			extra_data={'token': token, 'message': message, 'extra': extra})
		raise self.retry(exc=exc)

	try:
		# We got a response back, but we don't know whether it's an error yet.
		# This call raises errors so we can handle them with normal exception
		# flows.
		response.validate_response()
	except DeviceNotRegisteredError:
		# Mark the push token as inactive
		from notifications.models import PushToken
		PushToken.objects.filter(token=token).update(active=False)
	except PushResponseError as exc:
		# Encountered some other per-notification error.
		rollbar.report_exc_info(
			extra_data={
				'token': token,
				'message': message,
				'extra': extra,
				'push_response': exc.push_response._asdict(),
			})
		raise self.retry(exc=exc)


@app.route("/register/push-token",methods=["GET","POST"])
def register_push_token():
	data=request.json
	return data["tokken"]
	push_tokken=data["push_tokken"]
	inf=Influencer_details.query.filter_by(c_tokken=tokken).first()
	inf.not_token=push_tokken
	db.session.commit()
	return jsonify(valid=True)

@app.route("/register/push-token-brand",methods=["GET","POST"])
def register_push_token_brand():
	data=request.json
	data["tokken"]
	push_tokken=data["push_tokken"]
	inf=Brand_details.query.filter_by(c_tokken=tokken).first()
	if inf.not_token==None:
		send_push_message(push_tokken,"Welcome, To GenZ360.")
	inf.not_token=push_tokken
	db.session.commit()
	return jsonify(valid=True)


@app.route("/send-push-notification-inf",methods=["GET","POST"])
def send_push_notification_inf():
	if request.method=="POST":
		passwd=request.form["passwd"]
		msg=request.form["msg"]
		if passwd=="welcome@genz$360":
			inf_all=Influencer_details.query.filter(Influencer_details.not_token!=None).all()
			c=0
			while (c+1000)<len(inf_all):
				t1=Thread(target=send_push_notification_thread, args=(inf_all[c:c+1000],msg,))
				t1.start()
				c+=1000
			t2=Thread(target=send_push_notification_thread, args=(inf_all[c:],msg,))
			t2.start()
			return "Process Started"
		else:
			return "Wrong Password"
	else:
		return "That Was A Good Fun"


@app.route("/send-notification-inf",methods=["GET","POST"])
def send_notification_inf():
	return render_template("notify.html")

def send_push_notification_thread(alll,msg):
	for inf in alll:
		send_push_notif(inf,msg)
    # print(alll)


    
#End Push Notification


#start inf card

@app.route("/inf-gzid-wallet",methods=["GET","POST"])
def inf_gzid_wallet():
	data=request.json
	tokken=data["tokken"]
	inf=Influencer_details.query.filter_by(c_tokken=tokken).first()
	imgdata=base64.b64decode(data["imageData"])
	filename = 'infcard'+str(inf.influencer_id)+'.jpg'
	with open('./static/storeimg/'+filename, 'wb') as f:
		f.write(imgdata)
	return jsonify(valid=True,msg="http://www.genz360.com:81/get-image/"+filename)

#end inf card



#face-book


@app.route("/fb-authenticate",methods=["GET","POST"])
def fb_authenticate():
	return """<html>
				<head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"></head>
				<body>
					<script>
                          window.fbAsyncInit = function() {
                            FB.init({
                              appId      : '2104571659671346',
                              cookie     : true,
                              xfbml      : true,
                              version    : 'v4.0'
                            });
                              
                            FB.AppEvents.logPageView();   
                              FB.getLoginStatus(function(response) {
                            statusChangeCallback(response);
                        });
                          };
                        
                          (function(d, s, id){
                             var js, fjs = d.getElementsByTagName(s)[0];
                             if (d.getElementById(id)) {return;}
                             js = d.createElement(s); js.id = id;
                             js.src = "https://connect.facebook.net/en_US/sdk.js";
                             fjs.parentNode.insertBefore(js, fjs);
                           }(document, 'script', 'facebook-jssdk'));
                    </script>
                    <script>
                        
                    </script>
                </body>
			</html>"""


@app.route('/check-inf-platform-facebook', methods=['GET',"POST"])
def fb_app_response_token():
	data=request.json
	followers=data['follower']
	fbuserid=data['fbuserid']
	fb=Facebook(access_token=data['fbtoken'],verified=True,follower_count=data['follower'],profile_url=data['fbuserid'])
	db.session.add(fb)
	db.session.commit()
	user=Influencer_details.query.filter_by(c_tokken=data['tokken']).first()
	user.fb_id.append(fb)
	user.use_facebook=True
	db.session.commit()
	return jsonify(valid=True)


#end-face-book




api_key='AIzaSyBaJ1dGoRdqwnMqkxERJDax2avnKsjkHhg'   #constant for all

def store_youtube_account_data(c_tokken,channel_link):
	x=channel_link.split('/')
	channel_name=x[-1]
	url='https://www.googleapis.com/youtube/v3/channels?part=statistics&forUsername='+channel_name+'&key='+api_key
	uResponse = requests.get(url)
	Jresponse = uResponse.text
	d = json.loads(Jresponse)
	subscriber_count=d['items'][0]['statistics']['subscriberCount']
	if int(subscriber_count)>100:
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

def pass_generator(size=8, chars=string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for _ in range(size))

def get_tokken(use_to):
	tokken=""
	while True:
		tokken=pass_generator()
		if use_to=="brands":
			x=Brand_details.query.filter_by(c_tokken=tokken).all()
			if len(x)==0:
				break
		else:
			x=Influencer_details.query.filter_by(c_tokken=tokken).all()
			if len(x)==0:
				break
	return tokken

def send_sms(message, mobile):
		res = requests.get('http://smsalert.co.in/api/push.json?',
						   params={'apikey': "5d3623d8c58fd",
								   'mobileno': mobile,
								   'text': "You OTP for Login/Signup at GenZ360 is "+message+".Please Note this is valid only for 2 minutes.",
								   'sender': "GENZZZ",
								   'response': 'json'})
		return json.loads(res.content)

@app.route("/pricing-calculation",methods=["POST","GET"])
def pricing_calculation():
	if request.method=="POST":
		data=request.json
		dtype,service,inf_number,followers=data["dtype"],data["service"],data["inf_number"],data["followers"]
		return jsonify(calc_price(dtype,service,inf_number,200 if followers<=500 else 1000))



@app.route("/get-posts-details",methods=["GET","POST"])
def get_posts_details():
	try:
		data=request.json
		post=Campaign.query.filter_by(campaign_id=data["campaign_id"]).first().posts[0]
		post_schema=Campaign_posts_S()
		output=post_schema.dump(post).data
		return jsonify(valid=True,data=output)
	except:
		return jsonify(valid=False,err="Something Went Wrong!!!")

@app.route("/entry-location")
def entry_location():
	with open('location.csv', 'r',encoding='windows-1252') as csvfile:
		csvreader = csv.reader(csvfile)
		for row in csvreader:
			val=row[0]
			if row[1]!="":
				val=row[1]
			l=Location(location=val)
			db.session.add(l)
	db.session.commit()
	return val

@app.route("/get-matching-locations",methods=["GET","POST"])
def  get_matching_locations():
	try:
		if request.method=="POST":
			result=Location.query.all()
			final_res=[{"name": '',"id": 0,"icon": { "uri":'' },"children":[]}]
			for r in result:
				final_res[0]["children"].append({"name":r.location,"id":r.location_id})
			return jsonify(valid=True,result=final_res)
	except:
		return jsonify(valid=False,err="Something Went Wrong!!!")

@app.route("/brandlogin",methods=["GET","POST"])
def Login():
	try:
		if request.method=="POST":
			data=request.json
			user=Brand_details.query.filter_by(email=data['email']).all()
			if len(user)==0:
				return jsonify(valid=False,err = "No such User exists")
			user=user[0]
			if not user.verified:
				return jsonify(valid=False,err = "You Have Not Verified Your Account So Please Create Once Again")
			if sha256_crypt.verify(data['password'],user.password) and user.verified:
				tokken=get_tokken("brands")
				user.c_tokken=tokken
				db.session.commit()
				return jsonify(valid=True,tokken=tokken)
			else:
				return jsonify(valid=False,err="Wrong Password Please Try Again")
		else:
			return jsonify(valid=False,err = "Wrong Password")
	except:
		return jsonify(valid=False,err="Something Went Wrong!!!")


@app.route("/brandsignup",methods=["GET","POST"])
def signup():
	try:
		if request.method=="POST":
			data = request.json
			user=Brand_details.query.filter_by(email=data['email']).all()
			if len(user)>0:
				if not user[0].verified:
					db.session.delete(user[0])
					db.session.commit()
				else:
					return jsonify(valid=False,err="Account already exits!!!")
			user=Brand_details.query.filter_by(email=data['email']).all()
			if len(user)==0:
				new_brand=Brand_details(full_name=data['full_name'],brand_name=data['brand_name'],email=data['email'],password=sha256_crypt.encrypt(data['password']),verified=0,b_wallet=0,c_tokken=get_tokken("brands"),contact_no=data["contact"])
				db.session.add(new_brand)
				db.session.commit()
				otp=random.randint(1000,9999)
				otp_obj=Otp_details(otp_for=0,brand_id=new_brand.brand_id,otp_no=otp,purpose=1,valid_till=datetime.now()+timedelta(hours=1))
				db.session.add(otp_obj)
				db.session.commit()
				#msg=Message('From Genz360',sender='smtp.gmail.com',recipients=[new_brand.email])
				#msg.body="Your otp for signup: "+str(otp)
				#mail.send(msg)
				send_sms(str(otp),str(data["contact"]))
				return jsonify(valid=True,tokken=new_brand.c_tokken,purpose=1)
			else:
				return jsonify(valid=False,err="Account already exits!!!")
		else:
			return jsonify(valid=False,err="Method Not Allowed!!!")
	except:
		return jsonify(valid=False,err="Something Went Wrong!!!")

# forgot password

@app.route("/brandchangepass",methods=["GET","POST"])
def brandchangepass():
	try:
		if request.method=="POST":
			data = request.json
			user=Brand_details.query.filter_by(email=data['email']).all()
			if len(user)==0:
				return jsonify(valid=False,err="No Such User exits!!!")
			user=Brand_details.query.filter_by(email=data['email']).first()
			otp=random.randint(1000,9999)
			otp_obj=Otp_details(otp_for=0,brand_id=user.brand_id,otp_no=otp,purpose=1,valid_till=datetime.now()+timedelta(hours=1))
			db.session.add(otp_obj)
			db.session.commit()
			#msg=Message('From Genz360',sender='smtp.gmail.com',recipients=[new_brand.email])
			#msg.body="Your otp for signup: "+str(otp)
			#mail.send(msg)
			send_sms(str(otp),str(user.contact_no))
			return jsonify(valid=True)
		else:
			return jsonify(valid=False,err="Method Not Allowed!!!")
	except:
		return jsonify(valid=False,err="Something Went Wrong!!!")



@app.route("/brandchangepass-update",methods=["GET","POST"])
def brandchangepass_update():
	try:
		if request.method=="POST":
			data = request.json
			this_brand=Brand_details.query.filter_by(email=data["email"]).first()
			otp_no=Otp_details.query.filter_by(brand_id=this_brand.brand_id).all()[-1]
			if otp_no.otp_no==int(data["otp"]):
					db.session.delete(otp_no)
					this_brand.password=sha256_crypt.encrypt(data['passwd'])
					db.session.commit()
					send_push_notif_brand(this_brand,"Congratulations! Your password has been changed successfully.")
					return jsonify(valid=True,verified=True)
			else:
				return jsonify(valid=False,err="Wrong OTP or OTP Expired")
		else:
				return jsonify(valid=False,err="Method Not Allowed!!!")
	except:
		return jsonify(valid=False,err="Some Thing Went Wrong!!!")


# end


@app.route("/infloginstatus",methods=["GET","POST"])
def infloginstatus():
	try:
		if request.method=="POST":
			data = request.json
			c_tokken=data["tokken"]
			this_inf=Influencer_details.query.filter_by(c_tokken=c_tokken).all()
			if len(this_inf)>0:
				return jsonify(valid=True)
			else:
				return jsonify(valid=False)
	except:
		return jsonify(valid=False,err="Something Went Wrong!!!")

@app.route("/brandloginstatus",methods=["GET","POST"])
def brandloginstatus():
	try:
		if request.method=="POST":
			data = request.json
			c_tokken=data["tokken"]
			this_inf=Brand_details.query.filter_by(c_tokken=c_tokken).all()
			if len(this_inf)>0:
				return jsonify(valid=True)
			else:
				return jsonify(valid=False)
	except:
		return jsonify(valid=False,err="Something Went Wrong!!!")
	

@app.route("/inflogin",methods=["GET","POST"])
def inflogin():
	try:
		if request.method=="POST":
			data = request.json
			user=Influencer_details.query.filter_by(mobile_no=data['mobile_no']).all()
			if len(user)==0:
				new_brand=Influencer_details(mobile_no=data["mobile_no"],i_wallet=0,c_tokken=get_tokken("inf"),registration_date=datetime.now())
				db.session.add(new_brand)
				db.session.commit()
				otp=random.randint(1000,9999)
				if str(data["mobile_no"])=='0123456789':
					otp=1234
				otp_obj=Otp_details(otp_for=1,influencer_id=new_brand.influencer_id,otp_no=otp,purpose=1,valid_till=datetime.now()+timedelta(hours=1))
				db.session.add(otp_obj)
				db.session.commit()
				send_sms(str(otp),data["mobile_no"])
				return jsonify(valid=True,tokken=new_brand.c_tokken,updated=False)
			else:
				otp_no=Otp_details.query.filter_by(influencer_id=user[0].influencer_id).all()
				for ot in otp_no:
					db.session.delete(ot)
				db.session.commit()
				c_tokken=get_tokken("inf")
				user[0].c_tokken=c_tokken
				otp=random.randint(1000,9999)
				if str(user[0].mobile_no)=='8808100876' or str(user[0].mobile_no)=='0123456789':
					otp=1234
				otp_obj=Otp_details(otp_for=1,influencer_id=user[0].influencer_id,otp_no=otp,purpose=1,valid_till=datetime.now()+timedelta(hours=1))
				db.session.add(otp_obj)
				db.session.commit()
				send_sms(str(otp),data["mobile_no"])
				return jsonify(valid=True,tokken=user[0].c_tokken,updated=True)
		else:
			return jsonify(valid=False,err="Method Not Allowed!!!")
	except:
		return jsonify(valid=False,err="Some Thing Went Wrong!!!")



@app.route("/verifybrand-otp",methods=["GET","POST"])
def verfiy_otp():
	try:
		if request.method=="POST":
			data = request.json
			c_tokken=data["tokken"]
			this_brand=Brand_details.query.filter_by(c_tokken=c_tokken).first()
			otp_no=Otp_details.query.filter_by(brand_id=this_brand.brand_id).first()
			if otp_no.otp_no==int(data["otp"]):
					this_brand.verified=True
					db.session.delete(otp_no)
					db.session.commit()
					return jsonify(valid=True,verified=True)
			else:
				return jsonify(valid=False,err="Wrong OTP or OTP Expired")
		else:
				return jsonify(valid=False,err="Method Not Allowed!!!")
	except:
		return jsonify(valid=False,err="Some Thing Went Wrong!!!")

@app.route("/verify-otp-inf",methods=["GET","POST"])
def verfiy_otp_inf():
	#try:
		if request.method=="POST":
			data = request.json
			c_tokken=data["tokken"]
			this_brand=Influencer_details.query.filter_by(c_tokken=c_tokken).first()
			updated=this_brand.updated
			otp_no=Otp_details.query.filter_by(influencer_id=this_brand.influencer_id).all()[-1]
			if otp_no.otp_no==int(data["otp"]):
					this_brand.verified=True
					db.session.delete(otp_no)
					db.session.commit()
					return jsonify(valid=True,verified=True,updated=updated)
			else:
				return jsonify(valid=False,err="Wrong OTP or OTP Expired")
		else:
				return jsonify(valid=False,err="Method Not Allowed!!!")
#	except:
#		return jsonify(valid=False,err="Some Thing Went Wrong!!!")




@app.route("/resendotp-<string:typ>",methods=["GET","POST"])
def resend_otp(typ):
	data=request.json
	tokken=data["tokken"]
	if typ=='brand':
		brand=Brand_details.query.filter_by(c_tokken=tokken).first()
		otp_no=Otp_details.query.filter_by(brand_id=brand.brand_id).all()[-1]
		send_sms(str(otp_no.otp_no),str(brand.contact_no))
		return jsonify(valid=True)
	if typ=='inf':
		inf=Influencer_details.query.filter_by(c_tokken=tokken).first()
		otp_no=Otp_details.query.filter_by(influencer_id=inf.influencer_id).all()[-1]
		send_sms(str(otp_no.otp_no),str(inf.mobile_no))
		return jsonify(valid=True)
	if typ=="forgot":
		email=data["email"]
		brand=Brand_details.query.filter_by(email=email).first()
		otp_no=Otp_details.query.filter_by(brand_id=brand.brand_id).all()[-1]
		send_sms(str(otp_no.otp_no),str(brand.contact_no))
		return jsonify(valid=True)
	return jsonify(valid=False)





@app.route("/inf-daily-task-details",methods=["GET","POST"])
def inf_daily_task_details():
	if request.method=="POST":
		data=request.json
		tokken=data["tokken"]
		post=Posts_done.query.filter_by(pd_id=data["pd_id"]).first()
		camp_sch=Campaign_S()
		post_sch=Posts_done_S()
		result=post_sch.dump(post).data
		camp_data=camp_sch.dump(post.by_influencer.registered_campaigns).data
		return jsonify(valid=True,taskdetails=result,campaign=camp_data)


@app.route("/inf-daily-task",methods=["GET","POST"])
def inf_daily_task():
       try:
		if request.method=="POST":
			data=request.json
			tokken=data["tokken"]
			inf=Influencer_details.query.filter_by(c_tokken=tokken).first()
			involve=inf.involved_in
			result=[]
			post_sch=Posts_done_S()
			for i in involve:
				if i.registered_campaigns.status==1:
					for j in i.posts:
					    if j.verified:
					         result.append(post_sch.dump(j).data)
			return jsonify(valid=True,dailytask=result)
	except:
		return jsonify(valid=False,err="Some Thing Went Wrong!!!")

@app.route("/inf-live-campaign",methods=["GET","POST"])
def inf_live_campaign():
	try:
		if request.method=="POST":
			data=request.json
			tokken=data["tokken"]
			inf=Influencer_details.query.filter_by(c_tokken=tokken).first()
			involve=inf.involved_in
			campaign_schema=Campaign_S()
			result=[]
			post_files=[]
			for i in involve:
				if i.accepted:
					cc=Campaign.query.filter_by(campaign_id=i.campaign_id).first()
					if cc.status==1:
						result.append(campaign_schema.dump(i.registered_campaigns).data)
			return jsonify(valid=True,livecampaign=result)
	except:
		return jsonify(valid=False,err="Some Thing Went Wrong!!!")

@app.route("/inf-activity",methods=["GET","POST"])
def inf_activity():
	try:
		if request.method=="POST":
			data=request.json
			tokken=data["tokken"]
			inf=Influencer_details.query.filter_by(c_tokken=tokken).first()
			involve=inf.involved_in
			campaign_schema=Campaign_S()
			result=[]
			post_files=[]
			total_earning=0
			count=0
			for i in involve:
				if i.active_status==3 and i.accepted:
					total_earning+=i.amount_to_be_paid
					count+=1
					result.append({"camp":i.registered_campaigns.name,"earning":i.amount_to_be_paid})
			return jsonify(valid=True,report=result,total_earning=total_earning,count=count)
	except:
		return jsonify(valid=False,err="Some Thing Went Wrong!!!")

@app.route("/check-inf-platform",methods=["GET","POST"])
def check_inf_platform():
	try:
		if request.method=="POST":
			data=request.json
			inf=Influencer_details.query.filter_by(c_tokken=data["tokken"]).first()
			return jsonify(valid=True,fbverified=inf.use_facebook,instaverified=inf.use_instagram,ytverified=inf.use_youtube,twitterverified=inf.use_twitter)
	except:
		return jsonify(valid=False,err="Some Thing Went Wrong!!!")

@app.route("/brand-activity",methods=["GET","POST"])
def brand_activity():
	try:
		if request.method=="POST":
			data=request.json
			tokken=data["tokken"]
			brand=Brand_details.query.filter_by(c_tokken=tokken).first()
			involve=brand.campaigns
			campaign_schema=Campaign_S()
			result=[]
			total_inf_inv=0
			count=0
			for i in involve:
				if i.status==1 or i.status==2:
					total_inf_inv+=i.no_of_influencers1+i.no_of_influencers2
					count+=1
					result.append({"camp":i.name,"earning":i.no_of_influencers1+i.no_of_influencers2,"campaign_id":i.campaign_id})
			return jsonify(valid=True,report=result,total_earning=total_inf_inv,count=count)
	except:
		return jsonify(valid=False,err="Some Thing Went Wrong!!!")

@app.route("/inf-applied-campaign",methods=["GET","POST"])
def inf_applied_campaign():
	try:
		if request.method=="POST":
			data=request.json
			tokken=data["tokken"]
			inf=Influencer_details.query.filter_by(c_tokken=tokken).first()
			involve=inf.involved_in
			campaign_schema=Campaign_S()
			result=[]
			for i in involve:
				if not i.accepted:
					result.append(campaign_schema.dump(i.registered_campaigns).data)
			return jsonify(valid=True,appliedcampaign=result)
	except:
		return jsonify(valid=False,err="Some Thing Went Wrong!!!")

@app.route("/inflivecampaign",methods=["GET","POST"])
def inflivecampaign():
	try:
		if request.method=="POST":
			data=request.json
			tokken=data["tokken"]
			inf=Influencer_details.query.filter_by(c_tokken=tokken).first()
			camp=Campaign.query.all()
			campaign_schema=Campaign_S()
			result=[]
			for i in camp:
				if i.status==1:
				# if inf.location[0] in i.location and inf.interests in i.business_interest:
					if i.platform==0 and inf.use_facebook:
						result.append(campaign_schema.dump(i).data)
					elif i.platform==1 and inf.use_instagram:
						result.append(campaign_schema.dump(i).data)
					elif i.platform==3 and inf.use_twitter:
						result.append(campaign_schema.dump(i).data)
					elif i.platform==2 and inf.use_youtube:
						result.append(campaign_schema.dump(i).data)
					elif i.platform==10:
						result.append(campaign_schema.dump(i).data)
			return jsonify(valid=True,campaigns=result)
	except:
		return jsonify(valid=False,err="Some Thing Went Wrong!!!")




@app.route("/submitspoc",methods=["GET","POST"])
def submitspoc():
	try:
		if request.method=="POST":
			data = request.json
			brand=Brand_details.query.filter_by(c_tokken=data["tokken"]).first()
			spoc=Spoc_details(name=data["full_name"],email=data["email"],contact_no=data["number"],designation=data["desig"])
			db.session.add(spoc)
			brand.spoc.append(spoc)
			db.session.commit()
			return jsonify(valid=True,msg="SPOC Updated")
		else:
			return jsonify(valid=False,err="Method Not Allowed!!!")
	except:
		return jsonify(valid=False,err="Some Thing Went Wrong!!!")


@app.route("/submitinf-platform",methods=["GET","POST"])
def submitinf_platform():
	try:
		if request.method=="POST":
			data = request.json
			inf=Influencer_details.query.filter_by(c_tokken=data["tokken"]).first()
			fb,insta,yt,twitter=data["fb"],data["insta"],data["yt"],data["twitter"]
			msg=""
			if fb:
				pass
				inf.use_facebook=True
				f=Facebook()
			if insta:
				inf.use_instagram=True
				msg+="Instargram"
			if yt:
				if data["ytid"]=="" or data["ytid"]==None:
					return jsonify(valid=False,err="Invalid Youtube Id")
				inf.use_youtube=True
				if store_youtube_account_data(data["tokken"],data["ytid"]):
					msg=" Youtube-Verified "
				else:
					msg=" Youtube-Not Verified "
					return jsonify(valid=False,err="Less Youtube Followers")
			if twitter:
				inf.use_twitter=True
				foll=twapi.getfollowers(data["twitterid"])
				if foll==-1:
					return jsonify(valid=False,err="Invalid Twitter Id")
				if foll>100:
					t=Twitter(profile_url=data["twitterid"],follower_count=foll,verified=True)
					db.session.add(t)
					inf.tw_id.append(t)
					msg=" Twitter-Verified "
				else:
					msg=" Twitter-Not-Verified "
					return jsonify(valid=False,err="Less Twitter Followers")
			int_details=Interest_details(user_type=1,name1=1 if 1 in data["interestselected"] else 0,name2=1 if 2 in data["interestselected"] else 0,name3=1 if 3 in data["interestselected"] else 0,name4=1 if 4 in data["interestselected"] else 0,name5=1 if 5 in data["interestselected"] else 0,name6=1 if 6 in data["interestselected"] else 0,name7=1 if 7 in data["interestselected"] else 0,name8=1 if 8 in data["interestselected"] else 0,name9=1 if 9 in data["interestselected"] else 0,name10=1 if 10 in data["interestselected"] else 0,name11=1 if 11 in data["interestselected"] else 0)
			db.session.add(int_details)
			inf.interests.append(int_details)
			db.session.commit()
			msg=""
			if inf.use_facebook:
				msg+=" Facebook Verified "
			if inf.use_instagram:
				msg+=" Instagram Verified "
			if inf.use_twitter:
				msg+=" Twitter Verified "
			if inf.use_youtube:
				msg+=" Youtube Verified "
			if msg=="":
			    msg="Please Update Your Social Media Platform"
# 			send_push_notif(inf,"Welcome "+str(inf.name.split(" ")[0])+"! You have been successfully registered with GenZ360. Your id card can be downloaded from your profile on to your device.")
			return jsonify(valid=True,msg=msg)
		else:
			return jsonify(valid=False,err="Method Not Allowed!!!")
		# except:
		# 	return jsonify(valid=False,err=str(data))
	except:
		return jsonify(valid=False,err="Something Went Wrong!!!")


@app.route("/submitcomapnydetails",methods=["GET","POST"])
def submitcomapnydetails():
	try:
		if request.method=="POST":
			data = request.json
			brand=Brand_details.query.filter_by(c_tokken=data["tokken"]).first()
			brand.company_type=data["type"]
			brand.company_turnover=data["turnover"]
			brand.company_size=data["size"]
			brand.headquarter=data["hq"]
			brand.website_url=data["url"]
			brand.gst_no=data["gst"]
			db.session.commit()
			return jsonify(valid=True,msg="SPOC Updated")
		else:
			return jsonify(valid=False,err="Method Not Allowed!!!")
		# except:
		# 	return jsonify(valid=False,err=str(data))
	except:
		return jsonify(valid=False,err="Something Went Wrong!!!")



@app.route("/createnewcampaign",methods=["GET","POST"])
def createnewcampaign():
	try:
		if request.method=="POST":
			data=request.json
			ids=[]
			camp_type=data["selectedTypeval"]
			caption=data["caption"]
			app_token=data["uniquetoken"]
			link=data["link"]
			brand=Brand_details.query.filter_by(c_tokken=data["tokken"]).first()
			if str(camp_type)=='5':
				campaign=Campaign(name=data["name"],desc=data["description"],platform=10,creative_req=data["creativereq"],subtype=str(camp_type),linktoshare=link,caption=caption,status=4)
				db.session.add(campaign)
				brand.campaigns.append(campaign)
				db.session.commit()
				ids+=[campaign.campaign_id]
			if data["fb"]:
				campaign=Campaign(name=data["name"],desc=data["description"],platform=0,creative_req=data["creativereq"],subtype=str(camp_type),linktoshare=link,caption=caption,status=4)
				db.session.add(campaign)
				brand.campaigns.append(campaign)
				db.session.commit()
				if int(camp_type) in [7,8]:
					for l in data["location"]:
						loc=Location.query.filter_by(location_id=int(l)).first()
						loc.campaigns.append(campaign)
					db.session.commit()
				ids+=[campaign.campaign_id]
			if data["insta"]:
				campaign=Campaign(name=data["name"],desc=data["description"],platform=1,creative_req=data["creativereq"],subtype=str(camp_type),linktoshare=link,caption=caption,status=4)
				db.session.add(campaign)
				brand.campaigns.append(campaign)
				db.session.commit()
				if int(camp_type) in [7,8]:
					for l in data["location"]:
						loc=Location.query.filter_by(location_id=int(l)).first()
						loc.campaigns.append(campaign)
					db.session.commit()
				ids+=[campaign.campaign_id]
			if data["yt"]:
				campaign=Campaign(name=data["name"],desc=data["description"],platform=2,creative_req=data["creativereq"],subtype=str(camp_type),linktoshare=link,caption=caption,status=4)
				db.session.add(campaign)
				brand.campaigns.append(campaign)
				db.session.commit()
				if int(camp_type) in [7,8]:
					for l in data["location"]:
						loc=Location.query.filter_by(location_id=int(l)).first()
						loc.campaigns.append(campaign)
					db.session.commit()
				ids+=[campaign.campaign_id]
			if data["twitter"]:
				campaign=Campaign(name=data["name"],desc=data["description"],platform=3,creative_req=data["creativereq"],subtype=str(camp_type),linktoshare=link,caption=caption,status=4)
				db.session.add(campaign)
				brand.campaigns.append(campaign)
				db.session.commit()
				if int(camp_type) in [7,8]:
					for l in data["location"]:
						loc=Location.query.filter_by(location_id=int(l)).first()
						loc.campaigns.append(campaign)
					db.session.commit()
				ids+=[campaign.campaign_id]
			if len(ids)==0:
				return jsonify(valid=False,err="No Platform Selected")
			db.session.commit()
			return jsonify(valid=True,msg="Campaign Created",campaign_ids=ids)
	except:
		return jsonify(valid=False,err="Something Went Wrong!!!")

@app.route("/enternewcampdetails",methods=["GET","POST"])
def enternewcampdetails():
	try:
		if request.method=="POST":
			data=request.json
			cp=None
			campaigns=data["camp_ids"]
			if len(data["interestselected"])==0:
				return jsonify(valid=False,err="No Interest Selected")
			for c in campaigns:
				cc=Campaign.query.filter_by(campaign_id=c).first()
				if cc:
				# 	if not data["req"]:
					imgdata=base64.b64decode(data["imageData"])
					filename = 'camp'+str(cc.campaign_id)+'.jpg'
					with open('./static/storeimg/'+filename, 'wb') as f:
						f.write(imgdata)
					cc.image=filename
					int_details=Interest_details(user_type=1,name1=1 if 1 in data["interestselected"] else 0,name2=1 if 2 in data["interestselected"] else 0,name3=1 if 3 in data["interestselected"] else 0,name4=1 if 4 in data["interestselected"] else 0,name5=1 if 5 in data["interestselected"] else 0,name6=1 if 6 in data["interestselected"] else 0,name7=1 if 7 in data["interestselected"] else 0,name8=1 if 8 in data["interestselected"] else 0,name9=1 if 9 in data["interestselected"] else 0,name10=1 if 10 in data["interestselected"] else 0,name11=1 if 11 in data["interestselected"] else 0)
					db.session.add(int_details)
					cc.business_interest.append(int_details)
					db.session.commit()
# 			print(str(data["req"])+"   "+str(data["camp_ids"]))
			return jsonify(valid=True)
	except:
		return jsonify(valid=False,err="Something Went Wrong!!!")


@app.route("/campaign-cost-calc",methods=["GET","POST"])
def campaign_cost_calc():
	try:
		if request.method=="POST":
			data=request.json
			estimp=0
			netcost=0
			netpayout=0
			total_inf1=0
			total_inf2=0
			total_inf3=0
			total_inf4=0
			for i in data["camp_ids"]:
				campaign=Campaign.query.filter_by(campaign_id=i).first()
				service=int(campaign.subtype)
				if service<=6:
					ttype=1
				else:
					ttype=2
					service=service-6
				if int(campaign.platform)==0:
					campaign.no_of_influencers1=int(data['fb1'])
					campaign.no_of_influencers2=int(data['fb2'])
					total_inf1+=int(data['fb1'])
					total_inf1+=int(data['fb2'])
					if int(data['fb1']) not in [0,None]:
						res1=calc_price(ttype,service,int(data['fb1']),102)
						estimp+=res1['estimp']
						netcost+=res1['netcost']
					if int(data['fb2']) not in [0,None]:
						res2=calc_price(ttype,service,int(data['fb2']),502)
						estimp+=res2['estimp']
						netcost+=res2['netcost']
				elif int(campaign.platform)==1:
					campaign.no_of_influencers1=int(data['insta1'])
					campaign.no_of_influencers2=int(data['insta2'])
					total_inf2+=int(data['insta1'])
					total_inf2+=int(data['insta2'])
					if int(data['insta1']) not in [0,None]:
						res1=calc_price(ttype,service,int(data['insta1']),102)
						estimp+=res1['estimp']
						netcost+=res1['netcost']
					if int(data['insta2']) not in [0,None]:
						res2=calc_price(ttype,service,int(data['insta2']),502)
						estimp+=res2['estimp']
						netcost+=res2['netcost']
				elif int(campaign.platform)==2:
					campaign.no_of_influencers1=int(data['yt1'])
					campaign.no_of_influencers2=int(data['yt2'])
					total_inf3+=int(data['yt1'])
					total_inf3+=int(data['yt2'])
					if int(data['yt1']) not in [0,None]:
						res1=calc_price(ttype,service,int(data['yt1']),102)
						estimp+=res1['estimp']
						netcost+=res1['netcost']
					if int(data['yt2']) not in [0,None]:
						res2=calc_price(ttype,service,int(data['yt2']),502)
						estimp+=res2['estimp']
						netcost+=res2['netcost']
				elif int(campaign.platform)==3:
					campaign.no_of_influencers1=int(data['twitter1'])
					campaign.no_of_influencers2=int(data['twitter2'])
					total_inf4+=int(data['twitter1'])
					total_inf4+=int(data['twitter2'])
					if int(data['twitter1']) not in [0,None]:
						res1=calc_price(ttype,service,int(data['twitter1']),102)
						estimp+=res1['estimp']
						netcost+=res1['netcost']
					if int(data['twitter2']) not in [0,None]:
						res2=calc_price(ttype,service,int(data['twitter2']),502)
						estimp+=res2['estimp']
						netcost+=res2['netcost']
				elif int(campaign.platform)==10:
					campaign.no_of_influencers1=int(data['appins1'])
					campaign.no_of_influencers2=int(data['appins2'])
					total_inf4+=int(data['appins1'])
					total_inf4+=int(data['appins2'])
					if int(data['appins1']) not in [0,None]:
						res1=calc_price(ttype,service,int(data['appins1']),102)
						estimp+=res1['estimp']
						netcost+=res1['netcost']
					if int(data['appins2']) not in [0,None]:
						res2=calc_price(ttype,service,int(data['appins2']),502)
						estimp+=res2['estimp']
						netcost+=res2['netcost']
				# netpayout+=(res1['netpayout']+res2['netpayout'])
				pd=Pricing_details(est_impression=estimp,payout=netpayout,cost=netcost)
				db.session.add(pd)
				campaign.pricing.append(pd)
				campaign.status=0
			db.session.commit()
			this_brand=Brand_details.query.filter_by(c_tokken=data["tokken"]).first()
			send_push_notif_brand(this_brand,"Campaign submitted for approval!")
		return jsonify(valid=True,estimp=estimp,netcost=netcost,total_inf=max([total_inf1,total_inf2,total_inf3,total_inf4]))
	except:
		return jsonify(valid=False,err="Something Went Wrong!!!")

@app.route("/create-post",methods=["GET","POST"])
def create_post():
	if request.method=="POST":
		data=request.json
		brand=Brand_details.query.filter_by(c_tokken=data["tokken"]).first()
		if brand:
			cc=Campaign.query.filter_by(brand_id=brand.brand_id,campaign_id=data["campaign_id"]).first()
			if cc:
				post=Posts_done(rules=data['rules'],desc=data['desc'],verified=True)
				db.session.add(post)
				db.session.commit()
				imgdata=base64.b64decode(data["imageData"])
				filename = 'post'+str(cc.campaign_id)+'_'+str(post.pd_id)+'.jpg'
				with open('./static/storeimg/'+filename, 'wb') as f:
					f.write(imgdata)
				post.file_name=filename
				db.session.commit()
				for inv in cc.influencers:
					inv.posts.append(post)
				db.session.commit()
				return jsonify(valid=True)
			return jsonify(valid=False,error="No Campaign Found")
		return jsonify(valid=False,error="No Brand Found")

@app.route("/create-ugc",methods=["GET","POST"])
def create_ugc():
	try:
		if request.method=="POST":
			data=request.json
			inff=Influencer_details.query.filter_by(c_tokken=data['c_tokken'])
			cc=Campaign.query.filter_by(campaign_id=data["campaign_id"]).first()
			if cc:
				post=Posts_done(desc=data['desc'],verified=False)
				db.session.add(post)
				db.session.commit()
				imgdata=base64.b64decode(data["imageData"])
				filename = 'post'+str(cc.campaign_id)+'_'+str(post.pd_id)+'.jpg'
				with open('./static/storeimg/'+filename, 'wb') as f:
					f.write(imgdata)
				post.file_name=file_name
				db.session.commit()
				inv.posts.append(post)
				db.session.commit()
				return jsonify(valid=True)
			return jsonify(valid=False,error="No Campaign Found")
	except:
		return jsonify(valid=False,err="Something Went Wrong!!!")

@app.route("/to-verify-ugc",methods=["GET","POST"])
def to_verify_ugc():
	try:
		if request.method=="POST":
			res=[]
			data=request.json
			cc=Campaign.query.filter_by(campaign_id=data["campaign_id"]).first()
			inff=cc.influencers
			if len(inff)>0:
				for inf in inff:
					posts=inf.posts
					if len(posts)!=0:
						for post in posts:
							if not post.verified:
								res.append({"file_name":post.file_name,"pd_id":post.pd_id,"post_data":post.post_data})
				return jsonify(valid=True,res=res)
			return jsonify(valid=False,err="No Posts Found")
	except:
		return jsonify(valid=False,err="Something Went Wrong!!!")

@app.route("/verify-ugc",methods=["GET","POST"])
def verify_ugc():
	try:
		if request.method=="POST":
			data=request.json
			p=Posts_done.query.filter_by(pd_id=data["pd_id"]).first()
			p.verified=True
			db.session.commit()
			return jsonify(valid=True)
		else:
			return jsonify(valid=False)
	except:
		return jsonify(valid=False,err="Something Went Wrong!!!")

@app.route("/reject-ugc",methods=["GET","POST"])
def Reject_ugc():
	try:
		if request.method=="POST":
			data=request.json
			p=Posts_done.query.filter_by(pd_id=data["pd_id"]).first()
			db.session.delete(p)
			db.session.commit()
			return jsonify(valid=True)
		else:
			return jsonify(valid=False)
	except:
		return jsonify(valid=False,err="Something Went Wrong!!!")


@app.route("/brandprofileimageupdate",methods=["GET","POST"])
def brandprofileimageupdate():
	try:
		if request.method=="POST":
			data=request.json
			inf=Brand_details.query.filter_by(c_tokken=data["tokken"]).first()
			if inf:
				imgdata=base64.b64decode(data["imageData"])
				filename = 'brandprofile'+str(inf.brand_id)+'.jpg'
				with open('./static/storeimg/'+filename, 'wb') as f:
					f.write(imgdata)
				inf.logo=filename
				db.session.commit()
				send_push_notif_brand(inf,"Your profile has been updated successfully.")
				return jsonify(valid=True,uploaded=inf.logo)
			return jsonify(valid=False,uploaded='')
	except:
		return jsonify(valid=False,err="Something Went Wrong!!!")


@app.route("/infprofileimageupdate",methods=["GET","POST"])
def infprofileimageupdate():
	try:
		if request.method=="POST":
			data=request.json
			inf=Influencer_details.query.filter_by(c_tokken=data["tokken"]).first()
			if inf:
				imgdata=base64.b64decode(data["imageData"])
				filename = 'profile'+str(inf.influencer_id)+'.jpg'
				with open('./static/storeimg/'+filename, 'wb') as f:
					f.write(imgdata)
				inf.profile_photo=filename
				db.session.commit()
				send_push_notif(inf,"Congratulations! Your profile has been updated.")
				return jsonify(valid=True,uploaded=inf.profile_photo)
			return jsonify(valid=False,uploaded='')
	except:
		return jsonify(valid=False,err="Something Went Wrong!!!")

@app.route("/insta-get-access-token")
def insta_get_access_token():
	try:
		# access_token=request.args
		return '''  <script type="text/javascript">
					var token = window.location.href.split("access_token=")[1]; 
					window.location = "/app_response_token/" + token;
				</script> '''
		# return access_token
	except:
		return jsonify(valid=False,err="Something Went Wrong!!!")

@app.route('/app_response_token/<token>/', methods=['GET'])
def app_response_token(token):
	try:
		url='https://api.instagram.com/v1/users/self/?access_token='+token
		uResponse = requests.get(url)
		Jresponse = uResponse.text
		d = json.loads(Jresponse)
		insta_numeric_id=(d['data']['id'])
		followers=(d['data']['counts']['followed_by'])
		if followers>100:
			insta=Instagram(access_token=token,verified=True,profile_url=insta_numeric_id,follower_count=followers)
			db.session.add(insta)
			db.session.commit()
			user=Influencer_details.query.filter_by(c_tokken=session["username"]).first()
			user.insta_id.append(insta)
			user.use_instagram=True
			db.session.commit()
			return render_template("success.html")
		else:
			return render_template("failure.html")
	except:
		return jsonify(valid=False,err="Something Went Wrong!!!")


@app.route("/instagram-authentication/<string:tokken>",methods=["GET","POST"])
def instagram_authentication(tokken):
	try:
		session["username"]=tokken
		return redirect("https://api.instagram.com/oauth/authorize/?client_id=881d029d08a641c38422323a44b29c07&redirect_uri=http://www.genz360.com:81/insta-get-access-token&response_type=token")
	except:
		return jsonify(valid=False,err="Something Went Wrong!!!")

@app.route("/get-campaign-details",methods=["GET","POST"])
def get_campaign_details():
	try:
		data=request.json
		campaign=Campaign.query.filter_by(campaign_id=data["campaign_id"]).first()
		no_task=0 if len(campaign.posts)>0 else 1
		campaign_schema=Campaign_S()
		output=campaign_schema.dump(campaign).data
		return jsonify(valid=True,campaign=output,no_task=no_task)
	except:
		return jsonify(valid=False,err="Something Went Wrong!!!")

def click_url_generator(mobile_no,campaign_id):
	s="www.genz360.com:81/infurl/56"+str(mobile_no)+"78-"+str(campaign_id)
	return s

@app.route("/infurl/<string:m>-<string:cid>",methods=["GET","POST"] )
def infurl(m,cid):
	mob=m[2:12]
	inff=Influencer_details.query.filter_by(mobile_no=mob).first()
	infinv=Influencers_involved.query.filter_by(influencer_id=inff.influencer_id,campaign_id=int(cid)).first()
	if infinv.click_count==None:
		infinv.click_count=1
	else:
		infinv.click_count=infinv.click_count+1
	db.session.commit()
	return redirect('https://www.studentingera.com')



@app.route("/apply-for-campaign",methods=["GET","POST"])
def apply_for_campaign():
	try:
		if request.method=="POST":
			data=request.json
			inf=Influencer_details.query.filter_by(c_tokken=data["tokken"]).first()
			campaign=Campaign.query.filter_by(campaign_id=data["campaign_id"]).first()
			infinv=Influencers_involved.query.filter_by(influencer_id=inf.influencer_id,campaign_id=campaign.campaign_id).all()
			if len(infinv)>0:
				return jsonify(valid=False,err=" You Have Already Applied ")
			req_platform=campaign.platform
			followers=0
			if req_platform==0:
				fb=Facebook.query.filter_by(influencer_id=inf.influencer_id).first()
				followers=fb.follower_count
			if req_platform==1:
				insta=Instagram.query.filter_by(influencer_id=inf.influencer_id).first()
				followers=insta.follower_count
			if req_platform==3:
				tw=Twitter.query.filter_by(influencer_id=inf.influencer_id).first()
				followers=tw.follower_count
			if req_platform==2:
				yt=Youtube.query.filter_by(influencer_id=inf.influencer_id).first()
				followers=yt.subscriber_count
			if req_platform==10:
				inf_inv=Influencers_involved.query.filter_by(campaign_id=data["campaign_id"]).all()
				already_inv=len(inf_inv)
				req_inf=campaign.no_of_influencers1
				if already_inv<req_inf:
					involve=Influencers_involved(influencer_id=inf.influencer_id,campaign_id=campaign.campaign_id,range_type=0,accepted=True)
					db.session.add(involve)
					db.session.commit()
					campaign.influencers.append(involve)
					inf.involved_in.append(involve)
					db.session.commit()
					if int(campaign.subtype)==4 or int(campaign.subtype)==6:
						send_push_notif(inf,"Our Application send to the brand !, Wait for the response.")
						return jsonify(valid=True)
					for p in campaign.posts:
						new_post=Posts_done(file_name=p.file_name,rules=p.rules,desc=p.desc,verified=True)
						db.session.add(new_post)
						db.session.commit()
						involve.posts.append(new_post)
						db.session.commit()
					send_push_notif(inf,"Your application has been accepted. Please Perform the Action As Soon As Possible.")
					return jsonify(valid=True)
				elif already_inv<int(1.05*req_inf):
					involve=Influencers_involved(influencer_id=inf.influencer_id,campaign_id=campaign.campaign_id,range_type=0,accepted=False)
					db.session.add(involve)
					db.session.commit()
					campaign.influencers.append(involve)
					inf.involved_in.append(involve)
					db.session.commit()
					if int(campaign.subtype)==4 or int(campaign.subtype)==6:
						send_push_notif(inf,"Your application is pending.")
						return jsonify(valid=True)
					for p in campaign.posts:
						new_post=Posts_done(file_name=p.file_name,rules=p.rules,desc=p.desc)
						db.session.add(new_post)
						db.session.commit()
						involve.posts.append(new_post)
						db.session.commit()
					send_push_notif(inf,"Your application is pending.")
					return jsonify(valid=True)
			if followers>=100 and followers<=500:
				x=0
				req_inf=campaign.no_of_influencers1
			if followers>500:
				x=1
				req_inf=campaign.no_of_influencers2
			inf_inv=Influencers_involved.query.filter_by(campaign_id=data["campaign_id"],range_type=x).all()
			already_inv=len(inf_inv)
# 			un_link=click_url_generator(inf.mobile_no,campaign.campaign_id)
			if already_inv<req_inf:
				involve=Influencers_involved(influencer_id=inf.influencer_id,campaign_id=campaign.campaign_id,range_type=x,accepted=True)
				db.session.add(involve)
				db.session.commit()
				campaign.influencers.append(involve)
				inf.involved_in.append(involve)
				db.session.commit()
				if int(campaign.subtype)==4 or int(campaign.subtype)==6:
					send_push_notif(inf,"Your application has been accepted. Please Perform the Action As Soon As Possible.")
					return jsonify(valid=True)
				for p in campaign.posts:
					new_post=Posts_done(file_name=p.file_name,rules=p.rules,desc=p.desc,verified=True)
					db.session.add(new_post)
					db.session.commit()
					involve.posts.append(new_post)
					db.session.commit()
				send_push_notif(inf,"Your application has been accepted. Please Perform the Action As Soon As Possible.")
				return jsonify(valid=True)
			elif already_inv<int(1.05*req_inf):
				involve=Influencers_involved(influencer_id=inf.influencer_id,campaign_id=campaign.campaign_id,range_type=x,accepted=False)
				db.session.add(involve)
				db.session.commit()
				campaign.influencers.append(involve)
				inf.involved_in.append(involve)
				db.session.commit()
				if int(campaign.subtype)==4 or int(campaign.subtype)==6:
					send_push_notif(inf,"Your application is pending.")
					return jsonify(valid=True)
				for p in campaign.posts:
					new_post=Posts_done(file_name=p.file_name,rules=p.rules,desc=p.desc)
					db.session.add(new_post)
					db.session.commit()
					involve.posts.append(new_post)
					db.session.commit()
				send_push_notif(inf,"Your application is pending.")
				return jsonify(valid=True)
			else:
				send_push_notif(inf,"Regret! Number of applications have reached the limit.")
				return jsonify(valid=False,err="Sorry!!! Campaign Full Please Try In Some Other Campaign")
	except:
		return jsonify(valid=False,err="Something Went Wrong!!!")

@app.route("/check-applied",methods=["GET","POST"])
def check_applied():
	try:
		if request.method=="POST":
			data=request.json
			inf=Influencer_details.query.filter_by(c_tokken=data["tokken"]).first()
			campaign=Campaign.query.filter_by(campaign_id=data["campaign_id"]).first()
			involve=Influencers_involved.query.filter_by(influencer_id=inf.influencer_id,campaign_id=campaign.campaign_id).all()
			if len(involve)>0:
				involve=involve[0]
				return jsonify(valid=True,status="Pending" if not involve.accepted else "Accepted",color="orange" if not involve.accepted else "green",stateval=True)
			return jsonify(valid=True,status="Apply Now",color="red",stateval=False)
	except:
		return jsonify(valid=False,err="Something Went Wrong!!!")


@app.route("/get-campaign",methods=["GET","POST"])
def campaign():
	try:
		data=request.json
		output=[]
		brand=Brand_details.query.filter_by(c_tokken=data["tokken"]).first()
		campaigns=brand.campaigns
		campaign_schema=Campaign_S()
		# return jsonify(valid=True,campaigns=output,tokken=data["tokken"])
	# 	count=0
		for campaign in campaigns:
			if campaign.status==1:
				output.append(campaign_schema.dump(campaign).data)
		return jsonify(valid=True,campaigns=output)
	except:
		return jsonify(valid=False,err="Something Went Wrong!!!")



@app.route("/get-campaign-some",methods=["GET","POST"])
def campaign_some():
	try:
		data=request.json
		output=[]
		brand=Brand_details.query.filter_by(c_tokken=data["tokken"]).first()
		campaigns=brand.campaigns
		campaign_schema=Campaign_S()
		# return jsonify(valid=True,campaigns=output,tokken=data["tokken"])
		count=0
		for campaign in campaigns:
			if campaign.status==1:
				output.append(campaign_schema.dump(campaign).data)
		return jsonify(valid=True,campaigns=output)
	except:
		return jsonify(valid=False,err="Something Went Wrong!!!")

@app.route("/get-pending-campaign-some",methods=["GET","POST"])
def campaign_pending_some():
	try:
		data=request.json
		output=[]
		brand=Brand_details.query.filter_by(c_tokken=data["tokken"]).first()
		campaigns=brand.campaigns
		campaign_schema=Campaign_S()
		# return jsonify(valid=True,campaigns=output,tokken=data["tokken"])
		count=0
		for campaign in campaigns:
			if campaign.status==0:
				output.append(campaign_schema.dump(campaign).data)
		return jsonify(valid=True,campaigns=output)
	except:
		return jsonify(valid=False,err="Something Went Wrong!!!")


@app.route("/brandprofile",methods=["GET","POST"])
def brandprofile():
	try:
		data=request.json
		campaigns=[]
		output=[]
		brand=Brand_details.query.filter_by(c_tokken=data["tokken"]).first()
		campaigns=brand.campaigns
		campaign_schema=Campaign_S()
		if len(campaigns)==0:
			output=["not_available.jpg"]
		else:
			for campaign in campaigns:
				if campaign.status==1:
					output+=[campaign_schema.dump(campaign).data]
		return jsonify(valid=True,brand={"fname":brand.full_name,"brand_name":brand.brand_name,"email":brand.email,"campaign":output,"b_wallet":brand.b_wallet,"logo":brand.logo})
	except:
		return jsonify(valid=False,err="Something Went Wrong!!!")

@app.route("/infprofile",methods=["GET","POST"])
def infprofile():
	try:
		data=request.json
		campaigns=[]
		output=[]
		inf=Influencer_details.query.filter_by(c_tokken=data["tokken"]).first()
		campaigns=Influencers_involved.query.filter_by(influencer_id=inf.influencer_id).all()
		campaign_schema=Campaign_S()
		found=True
		if len(campaigns)==0:
			found=False
		else:
			for campaign in campaigns:
				cc=Campaign.query.filter_by(campaign_id=campaign.campaign_id).first()
				if cc.status==1:
					output+=[campaign_schema.dump(cc).data]
		return jsonify(valid=True,found=found,inf={"uid":inf.influencer_id,"name":inf.name,"contact":inf.mobile_no,"email":inf.email,"campaign":output,'profile_photo':inf.profile_photo})
	except:
		return jsonify(valid=False,err="Something Went Wrong!!!")

@app.route("/infwallet",methods=["GET","POST"])
def infwallet():
	try:
		data=request.json
		trans=[]
		inf=Influencer_details.query.filter_by(c_tokken=data["tokken"]).first()
		for i in inf.payment:
			trans+=[{"purpose":i.purpose,"amount":i.amount,"date_time":i.date_time,"transaction_id":i.transaction_id,"status":i.status}]
		return jsonify(valid=True,transactions=trans,amount=inf.i_wallet)
	except:
		return jsonify(valid=False,err="Something Went Wrong!!!")

@app.route("/brandwallet",methods=["GET","POST"])
def brandwallet():
	try:
		data=request.json
		trans=[]
		brand=Brand_details.query.filter_by(c_tokken=data["tokken"]).first()
		for i in brand.payment:
			trans+=[{"purpose":i.purpose,"amount":i.amount,"date_time":i.date_time,"transaction_id":i.transaction_id,"status":i.status}]
		return jsonify(valid=True,transactions=trans,amount=brand.b_wallet)
	except:
		return jsonify(valid=False,err="Something Went Wrong!!!")

@app.route("/payment/paypal/success")
def Paypalsuccess():
	try:
		pid=request.args["PayerId"]
		payid=request.args["paymentId"]
		payment_det,state=Executepayment(pid,payid)
		if state:
			p=Payments.query.filter_by(transaction_id=payid).first()
			p.status="Completed"
			db.session.commit()
			return render_template("paymentsuccess.html")
		else:
			p=Payments.query.filter_by(transaction_id=payid).first()
			p.status="Failed"
			db.session.commit()
			return render_template("paymentfailed.html")
	except:
		return jsonify(valid=False,err="Something Went Wrong!!!")

@app.route("/payment/paypal/failed")
def Paypalfailed():
	try:
		return render_template("paymentfailed.html")
	except:
		return jsonify(valid=False,err="Something Went Wrong!!!")


@app.route("/submit-creative",methods=["GET","POST"])
def submit_creative():
	try:
		if request.method=="POST":
			data=request.json
			inf=Influencer_details.query.filter_by(c_tokken=data["tokken"]).first()
			infv=Influencers_involved.query.filter_by(campaign_id=data["campaign_id"],influencer_id=inf.influencer_id).first()
			inv=Influencers_involved.query.filter_by(influencer_id=inf.influencer_id,campaign_id=data["campaign_id"]).first()
			campaign=Campaign.query.filter_by(campaign_id=data["campaign_id"]).first()
		
			if data["text"] or data["img"] or data["vid"]:
				if len(inv.posts)>0:
					return jsonify(valid=False,err="You Have Already submitted ")
						
				if data["text"]:
					if (data["textval"]==None or data["textval"]==""):
						return jsonify(valid=False,err="Please submit valid text.")
					else :
					     for p in campaign.posts:
        					 post=Posts_done(file_name=p.file_name,rules=p.rules,desc=p.desc,post_data=data["textval"])
        					 db.session.add(post)
        					 infv.posts.append(post)
        					 db.session.commit()
				# 	else:
				# 		check=Posts_done.query.filter_by(post_data=data["textval"]).all()
				# 		if len(check)>0:
				# 			return jsonify(valid=False,err="This Transaction id already exists")
				# 		post=Posts_done(post_data=data["textval"])
				# 		db.session.add(post)
				# 		infv.posts.append(post)
				# 		db.session.commit()
				elif data["img"]:
					if (data["imageData"]==None or data["imageData"]==""):
						return jsonify(valid=False,err="Please submit valid Image.")
					else:
						imgdata=base64.b64decode(data["imageData"])
						filename="infcreative"+str(infv.inf_inv_id)+'.jpg'
						with open('./static/storeimg/'+filename, 'wb') as f:
							f.write(imgdata)
						post=Posts_done(file_name=filename)
						db.session.add(post)
						infv.posts.append(post)
						db.session.commit()
				elif data["vid"]:
					if (data["vidval"]==None or data["vidval"]==""):
						return jsonify(valid=False,err="Please submit valid Video.")
					else:
					    for p in campaign.posts:
        					 post=Posts_done(file_name=p.file_name,rules=p.rules,desc=p.desc,post_data=data["vidval"])
        					 db.session.add(post)
        					 infv.posts.append(post)
        					 db.session.commit()
        					 
				return jsonify(valid=True)
			else:
				return jsonify(valid=False,err="Please submit a valid Creative.")
	except:
		return jsonify(valid=False,err="Something Went Wrong!!!")




@app.route("/infnotifications",methods=["GET","POST"])
def infnotifications():
	try:
		data=request.json
		trans=[]
		inf=Influencer_details.query.filter_by(c_tokken=data["tokken"]).first()
		n_sch=Notifications_S()
		for i in inf.notify[::-1]:
			trans.append(n_sch.dump(i.for_influencer).data)
		return jsonify(valid=True,notif=trans)
	except:
		return jsonify(valid=False,err="Something Went Wrong!!!")


@app.route("/submitinfdetails",methods=["GET","POST"])
def submitinfdetails():
	try:
		if request.method=="POST":
			data=request.json
			if int(data["age"])<15:
				return jsonify(valid=False,err="You Do Not fall Under Required Age Limit")
			inf=Influencer_details.query.filter_by(c_tokken=data["tokken"]).first()
			inf.name=data["full_name"]
			inf.age=data["age"]
			inf.date_of_birth=data['dob']
			loc=Location.query.filter_by(location_id=data["loc"]).first()
# 			inf.location.append(loc)
			loc.influencers.append(inf)
			inf.email=data["email"]
			inf.gender=data["gender"][0]
			# int_details=Interest_details(user_type=1,name1=1 if 1 in data["interestselected"] else 0,name2=1 if 2 in data["interestselected"] else 0,name3=1 if 3 in data["interestselected"] else 0,name4=1 if 4 in data["interestselected"] else 0,name5=1 if 5 in data["interestselected"] else 0,name6=1 if 6 in data["interestselected"] else 0,name7=1 if 7 in data["interestselected"] else 0,name8=1 if 8 in data["interestselected"] else 0,name9=1 if 9 in data["interestselected"] else 0,name10=1 if 10 in data["interestselected"] else 0,name11=1 if 11 in data["interestselected"] else 0)
			# db.session.add(int_details)
			# inf.interests.append(int_details)
			inf.updated=True
			db.session.commit()
			return jsonify(valid=True,msg="Updated")
		else:
			return jsonify(valid=False,err="Method Not Allowed")
	except:
		return jsonify(valid=False,err="Something Went Wrong!!!")


@app.route("/brandnotification",methods=["GET","POST"])
def brandnotification():
	try:
		data=request.json
		brand=Brand_details.query.filter_by(c_tokken=data["tokken"]).first()
		n_sch=Notifications_S()
		trans=[]
		for i in brand.notify[::-1]:
			trans.append(n_sch.dump(i.for_brand).data)
		# return jsonify(valid=True,notif=trans)
		return jsonify(valid=True,notifications=trans)
	except:
		return jsonify(valid=False,err="Something Went Wrong!!!")

@app.route("/brandlogout",methods=["GET","POST"])
def brandlogout():
	try:
		data=request.json
		brand=Brand_details.query.filter_by(c_tokken=data["tokken"]).first()
		brand.c_tokken=""
		brand.not_token=None
		db.session.commit()
		return jsonify(valid=True,msg="Logged Out")
	except:
		return jsonify(valid=False,err="Something Went Wrong!!!")

@app.route("/inflogout",methods=["GET","POST"])
def inflogout():
	try:
		data=request.json
		inf=Influencer_details.query.filter_by(c_tokken=data["tokken"]).first()
		inf.c_tokken=""
		inf.not_token=None
		db.session.commit()
		return jsonify(valid=True,msg="Logged Out")
	except:
		return jsonify(valid=False,err="Something Went Wrong!!!")


@app.route("/brand-payment/<string:tokken>/<string:amount>",methods=["GET","POST"])
def req_payment(tokken,amount):
	try:
		brand=Brand_details.query.filter_by(c_tokken=tokken).all()
		if len(brand)==0:
			return jsonify(valid=False,msg="You are logged Out")
		brand=brand[0]
		red_url,pay=Createpaypalpayment(item="Campaign",amount=amount,desc="Payment Done for Gez360 campaign")
		payment=Payments(pay_type=0,mode=0,amount=amount,date_time=datetime.now(),purpose="Payment For Campaign",transaction_id=pay["id"],links=red_url,status=pay["state"])
		db.session.add(payment)
		db.session.commit()
		brand.payment.append(payment)
		db.session.commit()
		return redirect(red_url)
	except:
		return jsonify(valid=False,err="Something Went Wrong!!!")

@app.route("/inf-payment-final",methods=["GET","POST"])
def inf_req_payment():
	try:
		data=request.json
		msg="Created"
		tokken=data["tokken"]
		amount=data["amount"]
		number=data["number"]
		inf=Influencer_details.query.filter_by(c_tokken=tokken).first()
		if inf.i_wallet<amount or int(amount)<=0:
			return jsonify(valid=True,msg="Invalid Amount")
		order_id="Paytm_Genz360_"+str(len(Payments.query.all())+1)
		res=ExecutePaytmPayment(str(amount),str(number),str(order_id))
		payment=Payments(pay_type=1,mode=1,amount=amount,date_time=datetime.now(),purpose="Transfer To Wallet",transaction_id=str(order_id),payment_detail_data=str(res),status=res["statusMessage"])
		db.session.add(payment)
		inf.i_wallet=inf.i_wallet-int(amount)
		db.session.commit()
		msg="Pending"
		count=0
		payment_status,valid_s=CheckOrderStatus(order_id)
	# 	while not valid_s:
	# 		if count>4:
	# 			break
	# 		count+=1
	# 		payment_status,valid_s=CheckOrderStatus(order_id)
		if payment_status["status"]==1:
			payment.status=str(payment_status["status"])+payment_status["message"]
			msg="Completed"
			send_push_notif(inf,"Hurray!"+str(amount)+" has been debited from your wallet.")
	# 		break
		db.session.commit()
		inf.payment.append(payment)
		db.session.commit()
		return jsonify(valid=True,msg=msg)
	except:
		return jsonify(valid=False,err="Something Went Wrong!!!")

@app.route("/bestinfluencers",methods=["GET","POST"])
def bestinfluencers():
	try:
		influencers=Influencer_details.query.limit(5).all()
		# influencers=[{"image":"bi.png"},{"image":"bi.png"},{"image":"bi.png"}]
		result=[]
		for i in influencers:
			if len(result)>4:
				break
			result.append({"name":i.name,"profile_photo":i.profile_photo,"age":i.age,"influencer_id":i.influencer_id})
		return jsonify(valid=True,bestinfluencers=result,err="some err")
	except:
		return jsonify(valid=False,err="Something Went Wrong!!!")

@app.route("/influencers-all",methods=["GET","POST"])
def influencers_all():
	try:
		influencers=Influencer_details.query.limit(100).all()
		# out=[{"influencer_id":"influencer.influencer_id","image":"os.jpg","name":"influencer.name","city":"influencer.city","facebook_count":"influencer.facebook","instagram_count":"influencer.instagram","youtube_count":"influencer.youtube","twitter_count":"influencer.twitter"}]
		out=[]
		for influencer in influencers:
			if len(out)>15:
				break
			out+=[{"influencer_id":influencer.influencer_id,"image":influencer.profile_photo,"name":influencer.name,"gender":influencer.gender,"use_facebook":influencer.use_facebook,"use_instagram":influencer.use_instagram,"use_twitter":influencer.use_twitter,"use_youtube":influencer.use_youtube}]
		return jsonify(valid=True,influencers=out,err="some err")
	except:
		return jsonify(valid=False,err="Something Went Wrong!!!")


@app.route("/genzsuccess",methods=["GET","POST"])
def genzsuccess():
	try:
		genzsuccess=[{"image":"os.jpg"},{"image":"os.jpg"}]
		return jsonify(valid=True,oursuccess=genzsuccess,err="some err")
	except:
		return jsonify(valid=False,err="Something Went Wrong!!!")


@app.route("/get-image/<string:name>",methods=["GET","POST"])
def get_image(name):
	try:
		filename=name
		return send_file('./static/storeimg/'+filename, mimetype='image')
	except:
		return send_file('./static/storeimg/'+"defaultprof.jpg", mimetype='image')
@app.route("/get-image1/<string:name>",methods=["GET","POST"])
def get_image1(name):
# 	try:
		filename=name
		with open('./static/storeimg/'+filename, "rb") as image_file:
			encoded_string = base64.b64encode(image_file.read())
			base64_string = encoded_string.decode('utf-8')
			return jsonify(valid=True,inbase=base64_string)
# 	except:
# 		return jsonify(valid=False,err="Something Went Wrong!!!")


@app.route("/cal-camp-data")
def cal_camp_data():
	try:
		data=request.json
		r1,d1,b1=reach_duration_budget(data["fb1"],data["fb2"],data["fb3"],data["fb4"],data["fb5"],data["fb6"])
		r2,d2,b2=reach_duration_budget(data["insta1"],data["insta2"],data["insta3"],data["insta4"],data["insta5"],data["insta6"])
		r3,d3,b3=reach_duration_budget(data["yt1"],data["yt2"],data["yt3"],data["yt4"],data["yt5"],data["yt6"])
		r4,d4,b4=reach_duration_budget(data["twitter1"],data["twitter2"],data["twitter3"],data["twitter4"],data["twitter5"],data["twitter6"])
		return jsonify(valid=True,budget=b1+b2+b3+b4+b5+b6,duration=d1+d2+d3+d4+d5+d6,reach=r1+r2+r3+r4+r5+r6)
	except:
		return jsonify(valid=False,err="Something Went Wrong!!!")

@app.route("/campaign-involvement-details",methods=["GET","POST"])
def campaign_involvement_details():
	try:
		if request.method=="POST":
			data=request.json
			fbr=Influencers_required(range1=data["fb1"],range2=data["fb2"],range3=data["fb3"],range4=data["fb4"],range5=data["fb5"],range6=data["fb6"],total=data["fbn"])
			instar=Influencers_required(range1=data["insta1"],range2=data["insta2"],range3=data["insta3"],range4=data["insta4"],range5=data["insta5"],range6=data["insta6"],total=data["instan"])
			ytr=Influencers_required(range1=data["yt1"],range2=data["yt2"],range3=data["yt3"],range4=data["yt4"],range5=data["yt5"],range6=data["yt6"],total=data["ytn"])
			twitterr=Influencers_required(range1=data["twitter1"],range2=data["twitter2"],range3=data["twitter3"],range4=data["twitter4"],range5=data["twitter5"],range6=data["twitter6"],total=data["twittern"])
			db.session.add(ytr)
			db.session.add(fbr)
			db.session.add(instar)
			db.session.add(twitterr)
			brand=Brand_details.query.filter_by(c_tokken=data["tokken"]).first()
			campaigns=data["camp_ids"]
			for c in campaigns:
				cc=Campaign.query.filter_by(campaign_id=c).first()
				if cc.brand_id==brand.brand_id:
					if cc.platform==0:
						cc.no_of_influencers.append(fbr)
						cc.est_budget,cc.est_duration,cc.est_reach=reach_duration_budget(data["fb1"],data["fb2"],data["fb3"],data["fb4"],data["fb5"],data["fb6"])
					elif cc.platform==1:
						cc.no_of_influencers.append(instar)
						cc.est_budget,cc.est_duration,cc.est_reach=reach_duration_budget(data["insta1"],data["insta2"],data["insta3"],data["insta4"],data["insta5"],data["insta6"])
					elif cc.platform==2:
						cc.no_of_influencers.append(ytr)
						cc.est_budget,cc.est_duration,cc.est_reach=reach_duration_budget(data["yt1"],data["yt2"],data["yt3"],data["yt4"],data["yt5"],data["yt6"])
					elif cc.platform==3:
						cc.no_of_influencers.append(twitterr)
						cc.est_budget,cc.est_duration,cc.est_reach=reach_duration_budget(data["twitter1"],data["twitter2"],data["twitter3"],data["twitter4"],data["twitter5"],data["twitter6"])
					db.session.commit()
				else:
					return jsonify(valid=False,err="Not Authorized")
			return jsonify(valid=True,camp_ids=data["camp_ids"])
		else:
			return jsonify(valid=False,err="Method Not Allowed")
	except:
		return jsonify(valid=False,err="Something Went Wrong!!!")


@app.route("/update-task-link",methods=["GET","POST"])
def update_task_link():
	try:
		if request.method=="POST":
			data=request.json
			tokken=data["tokken"]
			post=Posts_done.query.filter_by(pd_id=data["pd_id"]).first()
			if post.post_unique_id is not None:
			    return jsonify(valid=False,err="Link Already Submited!!!")
			if len(data["link"])==0:
				return jsonify(valid=False,err="No Post Found")
			post.post_unique_id=data["link"]
			post.date_posted=datetime.now()
			if "twitter" in data["link"]:
				post_id=data["link"].split("/")[-1]
				valid,x=twapi.getpost(int(post_id))
				if valid:
					post.comment_count=x.retweet_count
					post.post_url=data["link"]
					post.verified=True
					post.platform=3
					post.done=True
					db.session.commit()
					return jsonify(valid=True,msg="Link Updated Successfully")
				return jsonify(valid=False,msg="Invalid Link")
			if "facebook" in data["link"]:
				post_id=data["link"].split("/")[-1]
				post.post_url=data["link"]
				post.platform=0
				post.done=True
				db.session.commit()
				return jsonify(valid=True,msg="Link Updated Successfully")
			if "instagram" in data["link"]:
				try:
					url=data["link"]
					insta_data=Influencer_details.query.filter_by(c_tokken=tokken).first().insta_id[0]
					insta_numeric_id=insta_data.profile_url
					access_token=insta_data.access_token
					alphabet ={'-':62,'1':53,'0':52,'3':55,'2':54,'5':57,'4':56, '7':59, '6':58,'8':60,'9':61,'A':0,'C':2,'B':1,'E':4,'D':3,'G':6,'F':5,'I':8,'H':7,'K':10,'J':9,'M':12,'L':11,'O':14,'N':13,'Q':16,'P':15,'S':18,'R':17,'U':20,'T':19,'W':22,'V':21,'Y':24,'X':23,'Z':25,'_':63,'a':26,'c':28,'b':27,'e':30,'d':29,'g':32,'f':31,'i':34,'h':33,'k':36,'j':35,'m':38,'l':37,'o':40,'n':39,'q':42,'p':41,'s':44,'r':43,'u':46,'t':45,'w':48,'v':47,'y':50,'x':49,'z':51}
					n=0
					su=url.split('/')
					code=su[-2]
					for i in range(len(code)):
						c=code[i]
						n=n*64+alphabet[c]
					media_id=str(n)+'_'+insta_numeric_id
					url='https://api.instagram.com/v1/media/'+media_id+'?access_token='+access_token
					uResponse = requests.get(url)
					Jresponse = uResponse.text
					d = json.loads(Jresponse)
					likes_count=(d['data']['likes']['count'])
					comments_count=(d['data']['comments']['count'])
					post.like_count=likes_count
					post.comment_count=comments_count
					post.post_url=data["link"]
					post.verified=True
					post.done=True
					post.platform=1
					db.session.commit()
					return jsonify(valid=True,msg="Link Updated Successfully")
				except:
					return jsonify(valid=False,err="Link Updated")
			if "youtube" in data["link"]:
				try:
					link=data["link"]
					c_tokken=tokken
					x=link.split('/')
					video_id=x[-1]
					url='https://www.googleapis.com/youtube/v3/videos?part=statistics&id='+video_id+'&key='+api_key
					uResponse = requests.get(url)
					Jresponse = uResponse.text
					d = json.loads(Jresponse)
					viewCount=(d['items'][0]['statistics']['viewCount'])
					likeCount=(d['items'][0]['statistics']['likeCount'])
					post.like_count=likeCount
					post.comment_count=viewCount
					post.verified=True
					post.done=True
					post.platform=2
					return jsonify(valid=True,msg="Link Updated Successfully")
				except:
					return jsonify(valid=False,err="Invalid Link")
					
			post.post_url=data["link"]
			post.verified=True
			post.done=True
			db.session.commit()
		return jsonify(valid=True,msg="Link Updated Successfully")
	except:
		return jsonify(valid=False,err="Something Went Wrong!!!")




################################################################################################################################################
##################                    ADMIN                ##############################
################################################################################################################################################








def admin_login_required(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		try:
			if session["logged_in"] and session["username"]=="admin":
				return f(*args, **kwargs)
			else:
				return redirect("/admin-login-page")
		except:
			return redirect("/admin-login-page")
	return wrap

def send_active_msg(camp_id):
    c=Campaign.query.filter_by(campaign_id=camp_id).first()
    if c.platform==0:
        inf_all=Influencer_details.query.filter_by(use_facebook=1).all()
    elif c.platform==1:
        inf_all=Influencer_details.query.filter_by(use_instagram=1).all()
    elif c.platform==2:
        inf_all=Influencer_details.query.filter_by(use_twitter=1).all()
    elif c.platform==3:
        inf_all=Influencer_details.query.filter_by(use_youtube=1).all()
    # if c.subtype==7 or c.subtype==8:
    #     for inf in inf_all:
    #         if inf.location[0] in c.location:
    #             send_push_notif(inf,"Congratulations! You are eligible for"+ str(c.name) +"campaign")
    # else:
    for inf in inf_all:
        send_push_notif(inf,"Congratulations! You are eligible for"+ str(c.name) +"campaign")


def send_complete_msg(camp_id):
    c=Campaign.query.filter_by(campaign_id=camp_id).first()
    all_inv=c.influencers
    for inf in all_inv:
        send_push_notif(inf,"Lets have a look at your performance in the"+ str(c.name) +"campaign")

@app.route("/admin")
def admin_Home():
	try:
		if session["logged_in"]:
			return redirect("/admin-dashboard")
		else:
			return redirect("/admin-login-page")
	except:
		return redirect("/admin-login-page")

@app.route("/admin-login-page",methods=["GET","POST"])
def admin_login_page():
    return render_template("login.html")

@app.route("/admin-login",methods=["GET","POST"])
def admin_login():
    #if request.form=="POST":
        username=request.form['username']
        password=request.form['password']
        if username=="admin" and password=="gz2019.inf.brand.&ult1m@te$h@rkw3@r3b3$t":
            session['logged_in']=True
            session['username']="admin"
            return redirect("/admin-dashboard")
        else:
            flash("Wrong Credentials")
            return render_template("login.html")
    # else:
    #     flash("Method Not Allowed")
    #     return render_template("login.html")

@app.route("/admin-active-campaign",methods=["GET","POST"])
@admin_login_required
def admin_active_campaign():
    try:
        cc=Campaign.query.filter_by(status=1).all()
        d=[]
        for i in cc[::-1]:
            b=Brand_details.query.filter_by(brand_id=i.brand_id).first()
            d.append({'c':i, 'brand_name':b.brand_name})
        return render_template("campaign.html",dd=d,status=status,value="Active Campaigns",sts=1)
    except:
        return render_template("error.html")

@app.route("/admin-pending-campaign",methods=["GET","POST"])
@admin_login_required
def admin_pending_campaign():
    try:
        cc=Campaign.query.filter_by(status=0).all()
        d=[]
        for i in cc[::-1]:
            b=Brand_details.query.filter_by(brand_id=i.brand_id).first()
            d.append({'c':i, 'brand_name':b.brand_name})
        return render_template("campaign.html",dd=d,status=status,value="Pending Campaigns",sts=0)
    except:
        return render_template("error.html")

@app.route("/admin-completed-campaign",methods=["GET","POST"])
@admin_login_required
def admin_completed_campaign():
    try:
        cc=Campaign.query.filter_by(status=2).all()
        d=[]
        for i in cc[::-1]:
            b=Brand_details.query.filter_by(brand_id=i.brand_id).first()
            d.append({'c':i, 'brand_name':b.brand_name})
        return render_template("campaign.html",dd=d,status=status,value="Completed Campaigns",sts=2)
    except:
        return render_template("error.html")




@app.route("/admin-logout",methods=["GET","POST"])
@admin_login_required
def admin_logout():
	try:
		mobile=session['username']
		session.pop('username',None)
		session['logged_in']=False
		# flash("Successfully Logged Out.")
		return redirect("/admin-login-page")
	except:
		flash("ALREADY LOGGED OUT")
		return redirect("/admin-login")


@app.route("/admin-dashboard",methods=["GET","POST"])
@admin_login_required
def admin_dashboard():
    return render_template("dashboard.html")


@app.route("/admin-all-campaign",methods=["GET","POST"])
@admin_login_required
def admin_all_campaign():
    try:
        cc=Campaign.query.all()
        d=[]
        for i in cc:
            b=Brand_details.query.filter_by(brand_id=i.brand_id).first()
            d.append({'c':i, 'brand_name':b.brand_name})
        return render_template("campaign.html",dd=d,status=status,sts=0)
    except:
        return render_template("error.html")

@app.route("/admin-brands",methods=["GET","POST"])
@admin_login_required
def admin_brands():
    try:
        cc=Brand_details.query.all()
        return render_template("list_brands.html",ii=cc)
    except:
        return render_template("error.html")


@app.route("/admin-influencers",methods=["GET","POST"])
@admin_login_required
def admin_influencers():
    try:
        cc=Influencer_details.query.all()
        return render_template("list_inf.html",ii=cc)
    except:
        return render_template("error.html")

@app.route("/admin-filter_content/<int:sts>",methods=["GET","POST"])
@admin_login_required
def admin_filter_content(sts):
    try:
        # sts=request.form['status']
        typ=request.form['type']
        ptf=request.form['platform']
        cc=Campaign.query.filter_by(status=sts,subtype=typ,platform=ptf).all()
        d=[]
        for i in cc:
            b=Brand_details.query.filter_by(brand_id=i.brand_id).first()
            d.append({'c':i, 'brand_name':b.brand_name})
        #return render_template("campaign.html",dd=d,status=status,sts=sts)
        return render_template("campaign.html",dd=d,status=status,value=str(status[sts])+" Campaigns",sts=sts)
    except:
        return render_template("error.html")


@app.route("/admin-update-campaign-status/<int:camp_id>",methods=["GET","POST"])
@admin_login_required
def admin_update_campaign_status(camp_id):
    try:
        if request.method=="POST":
            sts=request.form["status"]
            if sts==1:
                t1=Thread(target=send_active_msg, args=(camp_id,))
                t1.start()
            elif sts==2:
                t2=Thread(target=send_complete_msg, args=(camp_id,))
                t2.start()
            c=Campaign.query.filter_by(campaign_id=camp_id).first()
            c.status=sts
            if request.form["type1"]:
                type1=request.form["type1"]
                c.payout_influencers1=type1
            if request.form["type2"]:
                type2=request.form["type2"]
                c.payout_influencers2=type2
            if request.form["data"]:
                data=request.form["data"]
                c.data=str(data)
            if request.form["pay_date"]:
                pay_date=request.form["pay_date"]
                c.payment_date=str(pay_date)
            db.session.commit()
            flash("Submission Successfull..!!!")
            if sts=="0":
                return redirect("/admin-pending-campaign")
            elif sts=="1":
                return redirect("/admin-active-campaign")
            elif sts=="2":
                return redirect("/admin-completed-campaign")
        else:
            flash("Method not Allowed")
            return render_template("error.html")
    except:
        return render_template("error.html")

@app.route("/admin-influencers-involved/<int:camp_id>",methods=["GET","POST"])
@admin_login_required
def admin_influencers_involved(camp_id):
    try:
        t=0
        c=Influencers_involved.query.filter_by(campaign_id=camp_id).all()
        campaign=Campaign.query.filter_by(campaign_id=camp_id).first()
        acc=Influencers_involved.query.filter_by(campaign_id=camp_id,accepted=True).count()
        for i in c:
            if i.posts:
                if i.posts[0].post_unique_id:
                    t+=1
        return render_template("influencer_involved_list.html",ii=c,status=status,c=campaign,acc=acc,task_counter=t)
    except:
        return render_template("error.html")

@app.route("/admin-get-post-data/<int:inf_id>",methods=["GET","POST"])
@admin_login_required
def admin_posts(inf_id):
    try:
        posts=Posts_done.query.filter_by(inf_inv_id=inf_id).all()
        return render_template("posts.html",ii=posts)
    except:
        return render_template("error.html")

@app.route("/admin-inf-post-notdone/<int:post_id>/<int:camp_id>",methods=["GET","POST"])
@admin_login_required
def admin_inf_post_notdone(post_id,camp_id):
    try:
        post=Posts_done.query.filter_by(pd_id=post_id).first()
        post.done=False
        db.session.commit()
        return redirect("/admin-influencers-involved/"+str(camp_id))
    except:
        return render_template("error.html")

@app.route("/admin-inf-post-done/<int:post_id>/<int:camp_id>",methods=["GET","POST"])
@admin_login_required
def admin_inf_post_done(post_id,camp_id):
    try:
        post=Posts_done.query.filter_by(pd_id=post_id).first()
        post.done=True
        db.session.commit()
        return redirect("/admin-influencers-involved/"+str(camp_id))
    except:
        return render_template("error.html")

@app.route("/admin-inf-post-alldone/<int:camp_id>",methods=["GET","POST"])
@admin_login_required
def admin_inf_post_alldone(camp_id):
    try:
        influencer=Influencers_involved.query.filter_by(campaign_id=camp_id).all()
        for i in influencer:
            if (i.posts):
                i.posts[0].done=True
        db.session.commit()
        return redirect("/admin-influencers-involved/"+str(camp_id))
    except:
        return render_template("error.html")
        
        
@app.route("/admin-inf-post-alldone-false/<int:camp_id>",methods=["GET","POST"])
@admin_login_required
def admin_inf_post_alldone_false(camp_id):
    try:
        influencer=Influencers_involved.query.filter_by(campaign_id=camp_id).all()
        for i in influencer:
            if (i.posts):
                i.posts[0].done=False
        db.session.commit()
        return redirect("/admin-influencers-involved/"+str(camp_id))
    except:
        return render_template("error.html")
        


@app.route("/admin-verify-ugc/<int:pd_id>/<int:camp_id>",methods=["GET","POST"])
def admin_verify_ugc(pd_id,camp_id):
	try:
		data=request.json
		p=Posts_done.query.filter_by(pd_id=pd_id).first()
		p.verified=True
		db.session.commit()
		flash("Accepted")
		return redirect("/admin-influencers-involved/"+str(camp_id))
	except:
		return render_template("error.html")

@app.route("/admin-reject-ugc/<int:pd_id>/<int:camp_id>",methods=["GET","POST"])
def admin_Reject_ugc(pd_id,camp_id):
	try:
		data=request.json
		p=Posts_done.query.filter_by(pd_id=pd_id).first()
		db.session.delete(p)
		db.session.commit()
		flash("Rejected")
		return redirect("/admin-influencers-involved/"+str(camp_id))
	except:
		return render_template("error.html")



@app.route("/admin-creative-upload/<int:camp_id>",methods=["GET","POST"])
@admin_login_required
def admin_creative_upload(camp_id):
    try:
        y=Campaign_posts.query.count()
        filename = 'admin_creative_'+str(camp_id)+"_"+str(y+1)+'.jpg'
        imageData=request.files['pfile'].read()
        with open('./static/storeimg/'+filename, 'wb') as f:
            f.write(imageData)
            c=Campaign_posts(file_name=filename,approved=False,campaign_id=camp_id)
            db.session.add(c)
            db.session.commit()
            flash("Request creative uploaded ")
        return redirect("/admin-campaign-det/"+str(camp_id))
    except:
        return render_template("error.html")

@app.route("/admin-inf-det/<int:inf_id>",methods=["GET","POST"])
@admin_login_required
def admin_inf_det(inf_id):
    try:
        inf=Influencer_details.query.filter_by(influencer_id=inf_id).first()
        p=Payments.query.filter_by(influencer_id=inf_id).all()
        return render_template("inf_details.html",i=inf,p=p)
    except:
        return render_template("error.html")


@app.route("/admin-campaign-det/<int:campaign_id>",methods=["GET","POST"])
@admin_login_required
def admin_campaign_det(campaign_id):
    try:
        inf=Campaign.query.filter_by(campaign_id=campaign_id).first()
        return render_template("Camp_details.html",i=inf)
    except:
        return render_template("error.html")

@app.route("/admin-brand-det/<int:brand_id>",methods=["GET","POST"])
@admin_login_required
def admin_brand_det(brand_id):
    try:
        inf=Brand_details.query.filter_by(brand_id=brand_id).first()
        p=Payments.query.filter_by(brand_id=inf.brand_id).all()
        spoc=Spoc_details.query.filter_by(brand_id=inf.brand_id).first()
        return render_template("brand_det.html",i=inf,spoc=spoc,p=p)
    except:
        return render_template("error.html")


@app.route("/admin-payout/<int:camp_id>",methods=["GET","POST"])
@admin_login_required
def admin_payout(camp_id):
    try:
        c=Campaign.query.filter_by(campaign_id=camp_id).first()
        for i in c.influencers:
            if i.posts[0].done:
                fc=0
                paisa=0
                if c.platform==0:
                    fb=Facebook.query.filter_by(influencer_id=i.influencer_id).first()
                    if fb:
                        fc=int(fb.follower_count)
                elif c.platform==1:
                    fb=Instagram.query.filter_by(influencer_id=i.influencer_id).first()
                    if fb:
                        fc=int(fb.follower_count)
                elif c.platform==3:
                    fb=Twitter.query.filter_by(influencer_id=i.influencer_id).first()
                    if fb:
                        fc=int(fb.follower_count)
                elif c.platform==2:
                    fb=Youtube.query.filter_by(influencer_id=i.influencer_id).first()
                    if fb:
                        fc=int(fb.subscriber_count)
                elif c.platform==10:
                    fc=200
                if fc>99 and fc<501:
                    paisa=c.payout_influencers1
                elif fc>500:
                    paisa=c.payout_influencers2
                inf=Influencer_details.query.filter_by(influencer_id=i.influencer_id).first()
                inf.i_wallet=inf.i_wallet+int(paisa)
                x=Influencers_involved.query.filter_by(influencer_id=i.influencer_id,campaign_id=camp_id).first()
                x.amount_to_be_paid=int(paisa)
                x.paid_status=True
                db.session.commit()
        return ("Paid Successfully in wallet of Selected Influencers")
        # return render_template("error.html")
    except:
        return render_template("error.html")


# @app.route("/export-all-influencers")
# def export_all_influencers():
#     t2=Thread(target=export_all_influencers1, args=())
#     t2.start()
#     return redirect("/admin-login-page")


@app.route("/export-all-influencers")
@admin_login_required
def export_all_influencers1():
    ii=Influencer_details.query.all()
    with open('\\static\\csvfiles\\inf_all.csv', 'w') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerow(["influencer_id","mobile_no","name","email","age","registration_date","updated","gender","location","i_wallet","use_facebook","use_instagram","use_twitter","use_youtube"])
        for i in ii:
            l=""
            if i.location:
                l=i.location[0]
            writer.writerow([i.influencer_id,i.mobile_no,i.name,i.email,i.age,i.registration_date,i.updated,i.gender,l,i.i_wallet,i.use_facebook,i.use_instagram,i.use_twitter,i.use_youtube])
    csvFile.close()
    path='\\static\\csvfiles\\inf_all.csv'
    # path="/inf_all.csv"
    return send_file(path, as_attachment=True)
    # return send_file(path, attachment_filename="abc.csv")



# @app.route("/export-all-brands")
# def export_all_brands():
#     t2=Thread(target=export_all_brands1, args=())
#     t2.start()
#     return "Done"


@app.route("/export-all-brands")
@admin_login_required
def export_all_brands1():
    ii=Brand_details.query.all()
    with open('./static/csvfiles/brands_all.csv', 'w') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerow(["brand_id","full_name","brand_name","email","verified","company_type","company_turnover","registration_date","contact_no","company_size","headquarter","website_url","b_wallet","spoc_name","spoc_email","spoc_contact_no","spoc_designation"])
        for i in ii:
            spoc=Spoc_details.query.filter_by(brand_id=i.brand_id).first()
            writer.writerow([i.brand_id,i.full_name,i.brand_name,i.email,i.verified,i.company_type,i.company_turnover,i.registration_date,i.contact_no,i.contact_no,i.headquarter,i.website_url,i.b_wallet,spoc.name if spoc else "",spoc.email if spoc else "",spoc.contact_no if spoc else "",spoc.designation if spoc else ""])
    csvFile.close()
    path='./static/csvfiles/brands_all.csv'
    return send_file(path, as_attachment=True)


# @app.route("/export-inf-inv/<int:campaign_id>")
# def export_inf_inv(campaign_id):
#     t2=Thread(target=export_inf_inv1, args=(campaign_id,))
#     t2.start()
#     return redirect("/admin-login-page")

@app.route("/export-inf-inv/<int:campaign_id>")
@admin_login_required
def export_inf_inv1(campaign_id):
    ii=Influencers_involved.query.filter_by(campaign_id=campaign_id).all()
    with open('\\static\\csvfiles\\inf_inv_'+str(campaign_id)+'.csv', 'w') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerow(["Influencer Id","Influencer name","Mobile number","Status","Post_url","File_url","Reach(Likes)","Payment status"])
        for i in ii:
            writer.writerow([i.influencer.influencer_id if i.influencer else "",i.influencer.name if i.influencer else "",i.influencer.mobile_no if i.influencer else "",i.accepted,i.posts[0].post_unique_id if i.posts else "","http://www.genz360.com:81/get-image/"+str(i.posts[0].file_name) if i.posts else "",i.posts[0].like_count if i.posts else "",i.paid_status])
    csvFile.close()
    path='\\static\\csvfiles\\inf_inv_'+str(campaign_id)+'.csv'
    return send_file(path, as_attachment=True)
    

@app.route("/export-campaigns/<int:sts>")
@admin_login_required
def export_campaigns(sts):
    ii=Campaign.query.filter_by(status=sts).all()
    with open('\\static\\csvfiles\\campaign_'+str(sts)+'.csv', 'w') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerow(["campaign_id","campaign_name","description","brand_id","Brand_name","subtype","creative_req","status","age_req","platform","location","no_of_influencers1","no_of_influencers2","payout_influencers1","payout_influencers2","data"])
        for i in ii:
            bb=Brand_details.query.filter_by(brand_id=i.brand_id).first()
            writer.writerow([i.campaign_id,i.name,i.desc,i.brand_id,bb.name,i.subtype,i.creative_req,i.status,i.age_req,i.platform,i.location,i.no_of_influencers1,i.no_of_influencers2,i.payout_influencers1,i.payout_influencers2,i.data])
    csvFile.close()
    path='\\static\\csvfiles\\campaign_'+str(sts)+'.csv'
    return send_file(path, as_attachment=True)
    
    
@app.route("/export-inf-location")
def export_inf_location():
    ii=Influencer_details.query.all()
    with open('\\static\\csvfiles\\inf_loc.csv', 'w') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerow(["influencer_id","location"])
        for i in ii:
            writer.writerow([i.influencer_id,i.location if i.location else ""])
    csvFile.close()
    path='\\static\\csvfiles\\inf_loc.csv'
    return send_file(path, as_attachment=True)










app.secret_key = 'patanahi kyun in logo ko secret key janni hai'

if __name__ == '__main__':
	app.run(debug=True,host='0.0.0.0',port=81)
