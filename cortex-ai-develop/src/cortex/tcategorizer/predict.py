import os
import sys
import json
import shutil
import pickle
import logging
from cortex.tcategorizer import data_helper
import numpy as np
import pandas as pd
import tensorflow as tf
from cortex.tcategorizer.text_cnn_rnn import TextCNNRNN
import time

logging.getLogger().setLevel(logging.INFO)

model_dir = "trained_results_1502219150"


class Classifier(object):
	def __init__(self, trained_dir, seq_len=67):
		self.trained_dir = trained_dir
		if not self.trained_dir.endswith('/'):
			self.trained_dir += '/'
		self.params, self.words_index, self.labels, self.embedding_mat = self.load_trained_params(self.trained_dir)

		self.sess = tf.Session()
		self.cnn_rnn = TextCNNRNN(
			embedding_mat = self.embedding_mat,
			non_static = self.params['non_static'],
			hidden_unit = self.params['hidden_unit'],
			sequence_length = seq_len,
			max_pool_size = self.params['max_pool_size'],
			filter_sizes = map(int, self.params['filter_sizes'].split(",")),
			num_filters = self.params['num_filters'],
			num_classes = len(self.labels),
			embedding_size = self.params['embedding_dim'],
			l2_reg_lambda = self.params['l2_reg_lambda'])

		checkpoint_file = self.trained_dir + 'best_model.ckpt'
		saver = tf.train.Saver(tf.global_variables())
		saver = tf.train.import_meta_graph("{}.meta".format(checkpoint_file[:-5]))
		saver.restore(self.sess, checkpoint_file)
		logging.critical('{} has been loaded'.format(checkpoint_file))

		
	def real_len(self, batches):
		return [np.ceil(np.argmin(batch + [0]) * 1.0 / self.params['max_pool_size']) for batch in batches]

	def predict_step(self, x_batch):
		feed_dict = {
			self.cnn_rnn.input_x: x_batch,
			self.cnn_rnn.dropout_keep_prob: 1.0,
			self.cnn_rnn.batch_size: len(x_batch),
			self.cnn_rnn.pad: np.zeros([len(x_batch), 1, self.params['embedding_dim'], 1]),
			self.cnn_rnn.real_len: self.real_len(x_batch),
		}
		predictions = self.sess.run([self.cnn_rnn.predictions], feed_dict)
		return predictions

	def load_trained_params(self, trained_dir):
		params = json.loads(open(self.trained_dir + 'trained_parameters.json').read())
		words_index = json.loads(open(self.trained_dir + 'words_index.json').read())
		labels = json.loads(open(self.trained_dir + 'labels.json').read())

		with open(self.trained_dir + 'embeddings.pickle', 'rb') as input_file:
			fetched_embedding = pickle.load(input_file)
		embedding_mat = np.array(fetched_embedding, dtype = np.float32)
		return params, words_index, labels, embedding_mat


	def map_word_to_index(self, examples, words_index):
		x_ = []
		for example in examples:
			temp = []
			for word in example:
				if word in self.words_index:
					temp.append(self.words_index[word])
				else:
					temp.append(0)
			x_.append(temp)
		return x_

	def predict(self, text):
		x_ = [data_helper.clean_str(text).split(' ')]
		x_ = data_helper.pad_sentences(x_, forced_sequence_length=self.params['sequence_length'])
		x_ = self.map_word_to_index(x_, self.words_index)
		x_test = np.asarray(x_)

		batches = data_helper.batch_iter(list(x_), self.params['batch_size'], 1, shuffle=False)
		predictions = ""
		for x_batch in batches:
			batch_predictions = self.predict_step(x_batch)[0][0]
			predictions = batch_predictions
		return self.labels[predictions]


if __name__ == '__main__':
	clf = Classifier(model_dir)

	data = ['This is tech', 'India does not need bullet train']
	t0 = time.time()
	for d in data:
		clf.predict(d)

	print("{} sentences classified in {} sec".format(len(data), time.time() - t0))
