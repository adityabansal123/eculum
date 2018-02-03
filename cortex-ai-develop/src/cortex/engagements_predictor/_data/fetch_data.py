import requests
import json
import os

accounts = []
with open(os.path.join("raw", "accounts_list.txt")) as f:
	accounts = f.read().strip().split('\n')

print("Number of accounts:", len(accounts))

for n in accounts:
	scrap_data = []
	try:
		data = requests.get("https://instagram.com/{}?__a=1".format(n))
		if data.status_code == 200:
			data  = data.json()
			r_data = {}
			if not data['user']['is_private']:
				for post in data['user']['media']['nodes']:
					media_type = "image"
					caption = ""
					if post['is_video']:
						media_type = "video"
					if post.get('caption'):
						caption = post['caption']
					r_data = {
				        'username': n,
						'followed_by': data['user']['followed_by']['count'],
						'follows': data['user']['follows']['count'],
						'full_name': data['user']['full_name'],
						'is_verified':data['user']['is_verified'],
						'profile_pic': data['user']['profile_pic_url'],
	                    'image': post['display_src'],
	                    'likes': post['likes']['count'],
	                    'comment': post['comments']['count'],
	                    'caption': caption,
	                    "date": post['date'],
	                    'media_type': media_type
					}
					scrap_data.append(r_data)
				print("Data collected for {}".format(n))
				with open(os.path.join("raw", "ig_posts_data.json"), "a") as ig:
					json.dump(scrap_data, ig)
					ig.close()
			else:
				print("User is private")
		else: 
			print("User not found")
	except Exception as e:
		print("Some error occured", e)

