from cleo import Command
from conn_db import db
import re 

class Premium(Command):
	"""
	Greets someone

	premium
		{--a|add : To add premium user}
		{--e|remove : To remove premium user}
	"""
	def handle(self):
		if self.option('add') or self.option('remove'):
			self.question("Enter twitter user name (Seperated by space):")
			self.users = list(map(str, input().split(' ')))
		if self.option('add'):
			self.update_premium(1)
		if self.option('remove'):
			self.update_premium(0)
	def update_premium(self, value):
		coll = db['user']
		for u in self.users:
			st = coll.update({'twitter.screen_name': re.compile(u, re.IGNORECASE)}, {'$set': {'premium': value}})
			if st['nModified']:
				self.info(str(u) + ": Updated")
			else:
				self.error(str(u) + ": Failed")

