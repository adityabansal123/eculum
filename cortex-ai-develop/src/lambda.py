import firefly

from cortex.tcategorizer.predict import Classifier
from cortex.hashtag.hthink import Hthinker
from cortex.hashtag.word_extract import WordExtractor

imodel_dir = 'cortex/tcategorizer/trained_results_1502219150/'
imodel_seq = 70

iclf = Classifier(imodel_dir, seq_len = imodel_seq)
hthink = Hthinker()
we = WordExtractor()

def predict_interest(payload):
	result = {}
	for s in payload:
		result[s] = iclf.predict(s).replace('_', ' ')
	return result

def predict_hashtag(payload):
	words = we.get_words(payload)
	hashtags = hthink.think(words)
	data = {}
	data['words'] = words
	data['hashtags'] = hashtags
	return data


def keyword_freq(payload):
	data = we.get_keyword_count(payload)
	return data

