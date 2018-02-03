import gensim.models.word2vec as w2v
import os


class Hthinker(object):
	def __init__(self):
		self.vecs = []
		vecs_list = os.listdir("cortex/hashtag/_data/trained")
		for v in vecs_list:
			self.vecs.append(w2v.Word2Vec.load(os.path.join("cortex", "hashtag", "_data","trained", v)))

	def think(self, words):
	    predict_words = []
	    for w in words:
	        for v in self.vecs:
	            try:
	                predict_words.extend(v.most_similar_cosmul(w))
	            except:
	                pass
	    predict_words.sort(key=lambda x: x[1])
	    predict_words = [i[0] for i in predict_words if i[1] > 0.7]
	    return predict_words[::-1][:10]