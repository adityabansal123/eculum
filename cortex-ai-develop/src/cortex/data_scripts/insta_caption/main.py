import json 
import requests
from textblob import TextBlob
from instafetch import Instafetch
import os
import time

dir_path = os.path.join("..", "_data", "insta_captions")

file_name = "insta_{}.txt".format(int(time.time()))

print("Saving File.. ", file_name)

if not os.path.isdir(dir_path):
    os.mkdir(dir_path)
    print("Directory Created")

def is_english(t):
    t = t.replace("#", "")
    chk = TextBlob(t)
    if chk.detect_language() == 'en':
        return True
    return False

def fetch_hashtags(tag):
    I  = Instafetch()
    print("Fetching data...")
    I.explore(tag, pages=25)
    all_posts = I.posts
    captions = []
    print("Data fetch complete: [{}]".format(tag))
    for i in all_posts['data']:
        try:
            c = i['caption']
            if is_english(c):
                captions.append(c+"\n")
        except:
            pass
    for cp in captions:
        try:
            with open(os.path.join(dir_path, file_name), "a") as f:
                f.write(cp)
        except Exception as e:
            print("Error", e)
            pass
    print("Saved Caption for #",tag)
 
if __name__ == "__main__":
    t0 = time.time()
    hashtags =  ['urban', 'sweet', 'women', 'sportsbrav', 'art', 'love', 
        'family', 'guy', 'funny', 'me', 'freeway', 
		'court', 'training', 'crowd', 'street', 'season', 'city', 'fitness', 
		'sketchbook', 'goodtime', 'water', 'player', 'score', 'exercise', 
        'cool', 'bff', 'illustration', 
		'justdoit', 'summer', 'life', 'instamood', 'instaartist', 
		'tagblender', 'blue', 'yogaforlovers', 'loveit', 'bestfriend', 'fitnessmodel', 
		'TagsForLikes', 'fashion', 'creative', 'picture', 'sexy', 'road', 
		'architecture', 'heart', 'igyoga', 'beautiful', 'gym', 'cardio', 
		'orange', 'workout', 'artoftheday', 'green', 'town', 'artsy',
		 'gallery', 'sports', 'pool', 'watersport', 'draw', 'instarun', 'style', 
		'cars', 'hot', 'siblings', 'pencil', 'yogapose', 'artist', 'fun', 'masterpiece', 
		'cute', 'instagood', 'train', 'vehicles', 'ride', 'face', 'figure',
		 'christmas', 'drawing', 'health', 'instaart', 'best', 'sketch', 'hair', 'girl', 'graphic', 
		'clearsky', 'graphics', 'fantastic', 'sporty', 'vibes', 'pen', 'tattoos', 'vacation',
		 'winner', 'nature', 'instayoga', 'red', 'pouring', 'paper', 'somuchfun', 
		'photooftheday', 'swim', 'active', 'healthy']

    for h in hashtags:
        pass
        try:
            fetch_hashtags(h)
        except Exception as e:
            print(e)
            pass
    print("Task Completed in: {} minutes".format((time.time()-t0) // 60 ))
