from collections import Counter
import os
from textblob import TextBlob as tb
import math
import nltk 
nltk.download("punkt")
nltk.download("stopwords")
from nltk.corpus import stopwords
from nltk import word_tokenize
import re
from collections import Counter

class WordExtractor(object):
	def __init(self):
		pass

	def tf(self, word, blob):
		return blob.words.count(word) / len(blob.words)

	def n_containing(self, word, bloblist):
		return sum(1 for blob in bloblist if word in blob.words)

	def idf(self, word, bloblist):
		return math.log(len(bloblist) / (1 + self.n_containing(word, bloblist)))

	def tfidf(self, word, blob, bloblist):
		return self.tf(word, blob) * self.idf(word, bloblist)

	def clean_sentence(self,raw, unique=True):
		noise_words = []
		stop_words = list(set(stopwords.words('english')))
		URL_REGEX = r"""(?i)\b((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?<>""'']))"""
		raw = re.sub(URL_REGEX, '', raw, flags=re.MULTILINE)
		for n in noise_words:
		    clean = raw.replace(n, " ")
		clean = re.sub("[^a-zA-Z]"," ", raw)
		clean = clean.lower()
		words = clean.split()
		stop_words = list(set(stopwords.words('english')))
		words = [w for w in words if w not in stop_words]
		return " ".join(words)

	def get_keyword_count(self, text):
		document = tb(self.clean_sentence(text))
		pos_dict = {}
		for i in document.tags:
			if i[1] in ['JJ', 'NN', 'JJR', 'NNS', 'NNP', 'NNPS'] and len(i[0]) > 3:
				pos_dict[i[0]] = i[1]
		bloblist  = [document]
		freq = document.word_counts
		for i, blob in enumerate([document]):
			scores = {word: self.tfidf(word, blob, bloblist) for word in blob.words}
			sorted_words = sorted(scores.items(), key=lambda x: x[1], reverse=True)
			results = []
			for word, score in sorted_words:
				if word in pos_dict.keys():
					results.append((word, pos_dict[word]))
			results.sort(key=lambda x: x[1])
			data = [i[0] for i in results]

		freq_data = {}
		for i in data:
			freq_data[i] = freq[i]
		return freq_data


	def get_words(self, text):
		document = tb(self.clean_sentence(text))
		pos_dict = {}
		for i in document.tags:
			if i[1] in ['JJ', 'NN', 'JJR', 'NNS', 'NNP', 'NNPS'] and len(i[0]) > 3:
				pos_dict[i[0]] = i[1]

		bloblist  = [document]
		for i, blob in enumerate([document]):
			scores = {word: self.tfidf(word, blob, bloblist) for word in blob.words}
			sorted_words = sorted(scores.items(), key=lambda x: x[1], reverse=True)
			results = []
			for word, score in sorted_words:
				if word in pos_dict.keys():
					results.append((word, pos_dict[word]))
			results.sort(key=lambda x: x[1])
			return [i[0] for i in results]


