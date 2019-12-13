import twitter
api = twitter.Api(consumer_key="6HEDKDhA7fmWgV6Uqt1agJHS2",consumer_secret="ukrVmHTQ0KfyOmjnmJqqgulbxHQXKWptRiYjqoqwEGCAjI3xqb",access_token_key="772665695767113728-gdHRIq0rxvfYONDLk2K33Ljrthm0ekr",access_token_secret="pQ8PUM7pevWTkHo1E2KtVb9oiEv8v5qB7D09r9BZKWd7X",sleep_on_rate_limit=True,application_only_auth=True)

def getfollowers(userid):
	try:
		return len(api.GetFollowers(screen_name=userid,include_user_entities=True))
	except:
		return -1

def getpost(postid):
	try:
		x=api.GetStatus(postid)
		return True
	except:
		return False
# l=api.GetListMembersPaged()
# print(l)