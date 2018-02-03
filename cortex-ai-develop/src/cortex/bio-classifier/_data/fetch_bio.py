mport tweepy
import os
import time

consumer_key = os.environ['TW_CKEY']
consumer_secret = os.environ['TW_CSECRET']

access_token = os.environ['TW_ATOKEN']
access_secret = os.environ['TW_ASECRET']

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)

api = tweepy.API(auth)

reference_users = ["paraazz", 
					"vmesel",
					"bansaladitya209",
					"mitsuhiko",
					"Kailash26558592",
					"arorakanav11",
					"chiax",
					"jk_rowling",
					"rishibagree",
					"rishabhmhjn",
					"GavinFree",
					"HerrBains",
					"JulianAssange",
					"davidfrawleyved",
					"DaveLeeBBC",
					"marcorubio",
					"CaseyNewton",
					"narendramodi",
					"fgautier26",
					"sundarpichai",
					"Pogue",
					"SushmaSwaraj",
					"waltmossberg"
					]

time_instance = time.time()

def save_data(data):
    with open("unlabled/bio_{}.txt".format(time_instance), "a") as f:
    	f.write(data+"\n")
    	f.close()

i = 0
total_bio = 0
t0 = time.time()
while i < len(reference_users):
	ids = []
	print("Getting friends of: ", reference_users[i])

	try:
		for page in tweepy.Cursor(api.friends_ids, \
								screen_name=reference_users[i]).pages():
			print("-")
			ids.extend(page)
		print("Total friends:", len(ids))
		for e in ids:
			user = api.get_user(e)
			print("Saving Bio:", user.screen_name)
			if len(user.description) > 3:
				total_bio+=1
				save_data(user.description)
		
		i+=1
	except Exception as e:
		print("Error: ", e)
		print("\n\nRetrying in 15 minutes")
		time.sleep(915)
		pass

print("Total bio collected:", total_bio)
print("Time Taken:", time.time()-t0)