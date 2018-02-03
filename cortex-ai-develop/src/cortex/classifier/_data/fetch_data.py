''' Script to fetch data from sub-reddits '''

# categories: 
	# * education and research
	# * technology, sciences and engineering
	# * business, startups
	# * politics
	# * music, acting, arts, history, philosophy,literature & writing(entertainment)
	# * sports
	# * services, social works, environment
	# * management, marketing, economics, finance

import requests
import os
import time
import multiprocessing
import pandas as pd
import datetime
import codecs

headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
           'Accept-Encoding': 'gzip, deflate, sdch',
           'Accept-Language': 'en-US,en;q=0.8',
           'Upgrade-Insecure-Requests': '1',
           'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:41.0) Gecko/20100101 Firefox/41.0'}

subreddit = {
	#topic: [subreddit...]
	'business_startups': ['business', 'Entrepreneur', 'Entrepreneurship', 'startup', 
							'venturecapital', 'Business_Ideas', 'Startup_Ideas'], 
	'management_marketing_economics_finance': ['economy', 'InvestmentBanking123', 
												'projectmanagement', 'AskMarketing',
												'marketing', 'digital_marketing', 'investing',
												'finance', 'Economics'], 
	'sports': ['sports', 'Cricket', 'football', 
				'soccer', 'hockey', 'FormulaE', 
				'olympics', 'sports_undelete'], 
	'technology_sciences_engneering': ['technology', 'gadgets', 'Technology_', 'tech',
										'EverythingScience', 'MachineLearning', 'singularity'], 
	'education_and_research': ['college', 'education','computerscience', 
								'GradSchool', 'EngineeringStudents'], 
	'arts_music_acting_literature': ['entertainment', 'bollywood', 'hollywoodtime', 
									'Overwatch', 'WaltDisneyWorld', 'literature', 
									'Art', 'southasianart', 'ancientrome', 'AskHistorians'], 
	'politics': ['politics', 'Indian_Politics', 'News_Politics',
				'PoliticalDiscussion', 'POLITIC', 'IndiaSpeaks', 
				'Indianpolitics', 'The_Europe', 'RussiaLago'], 
	'services_environment_socialworks': ['socialwork', 'NGOs', 'NGO', 'environment', 'nonprofit']
}


def build_data(data, topic):
	pre = []
	if os.path.isfile('raw/{}'.format(topic)):
		pre = open('raw/'+topic+".txt", 'r').read().split('\n')
	with open('raw/'+topic+'.txt', 'a') as f:
		for i in data['data']['children']:
			i = i['data']['title']
			if i not in pre:
				f.write(i+"\n")
		print("Saved: ", topic)

def get_data(subreddit, topic):
	if not os.path.isdir("raw"):
		os.mkdir("raw")
	url = 'https://www.reddit.com/r/{}/.json?limit=100'.format(subreddit)
	r = requests.get(url, headers=headers)
	if r.status_code == 200:
		r = r.json()
		build_data(r, topic)
		i = 0
		while r['data']['after'] and i < 100:
			url = 'https://www.reddit.com/r/{}/.json?limit=100&after={}'. \
					format(subreddit, r['data']['after'])
			r = requests.get(url, headers=headers)
			r = r.json()
			build_data(r, topic)
			i+=1

def sub_data(s):
	for s in subreddit[t]:
		print('Fetching Data: {} ({})'.format(s, t))
		get_data(s, t)


t0 = time.time()
#threads = []
for t in subreddit:
	sub_data(t)
	# p = multiprocessing.Process(target=sub_data, args=(t,))
	# threads.append(p)

# [t.start() for t in threads]
# [t.join() for t in threads]
print('Data fetching finished in: ', time.time()-t0)

print('Finalising data..')

all_data = []
files = os.listdir('raw')
path = 'raw'
for i in files:
	with open(os.path.join(path,i), "r", encoding='utf-8') as f:
		try:
			for t in f.read().split('\n'):
				all_data.append([t, i[:-4]])
			print(i[:-4])
		except:
			print("E")
			pass

df = pd.DataFrame(all_data, columns=['text', 'category'])
df.drop_duplicates('text', inplace=True)
df.reset_index(drop=True, inplace=True)
df.to_csv('raw/labeled_text_{}.csv.gz'. \
			format(datetime.datetime.strftime(datetime.datetime.now(), "%Y_%m_%d")), \
			compression='gzip', encoding="utf-8")
