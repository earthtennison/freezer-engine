"""
Conversation manager program as a socket server for receiving text and image messages from app.py
"""

from csv_database import csv_database

# for datetime type
from datetime import datetime

# custom socket
from custom_socket import CustomSocket
import json

from random import randint

import os

import numpy as np

import socket

import logging

logging.basicConfig(filename='app.log', encoding='utf-8', level=logging.DEBUG)

class Conversation():
	def __init__(self, db_path):

		# current message user input
		self.current_msg = ""

		# conver_type are add_item, update_item, list_item
		self.conver_type = ""

		self.conver_index = 0

		self.item = {'item_id':'','name':'', 'expiry_date':None, 'store_place':'', 'quantity':0, 'category':'', 'exist':True, 'image_id':'', 'add_date': None}

		self.db = csv_database(db_path)

		self.image_db_path = './image_db'




	def get_conver_type(self, msg: str):

		if msg.lower() in ['add item', 'เพิ่มของ', 'เพิ่ม', 'add']:
			self.conver_type  = 'add_item'
		elif msg.lower() in ['update item']:
			self.conver_type = 'update_item'
		elif msg.lower() in ['list item']:
			self.conver_type = 'list_item'
		else:
			# send dafault message
			self.conver_type = 'default'

	def push_msg(self, current_msg):
		self.current_msg = current_msg

		# check cancel message
		if self.current_msg.lower() in ['cancel', 'stop']:
			self.conver_index = 0
			self.conver_type = 'default'

		# check message type; checking all expiring items
		elif self.current_msg.lower() == 'check':
			self.conver_index = 0
			self.conver_type = 'check'

		# check if is initial message of the conversation
		if self.conver_index == 0 and self.conver_type == '':
			self.get_conver_type(self.current_msg)



	def response(self):

		# rule base for response
		if self.conver_type == 'default':
			self.conver_index = 0
			self.conver_type = ''
			msg = "Hello, I am Freezer. Please tell me what to do:\n" + \
				"1. add item\n" + \
				"2. update item\n" + \
				"3. list item"
			return {'type': "quick_reply", 'message': msg, 'aux_data':['add item', 'update item', 'list item']}
				
		elif self.conver_type == 'check':
			msg = 'Expiring item! :'
			item_cnt = 0
			for idx, row in self.db.df.iterrows():
				if row['exist'] == True:
					date_diff =  datetime.strptime(row['expiry_date'], '%d.%m.%Y') - datetime.now().replace(hour=0, minute=0, second=0)
					if  0 <= date_diff.days + 1 < 7: # 0-7 days
						msg += '\n- ' + row['name'] + ' is expired in ' + str(date_diff.days + 1) + ' days'
						item_cnt += 1
					elif date_diff.days + 1 < 0: # <0 days
						msg += '\n- '+ row['name'] +' is expired ' + str(-1*(date_diff.days + 1)) + ' days ago'
						item_cnt += 1

			self.conver_index = 0
			self.conver_type = ''

			if item_cnt > 0:
				return {'type': "text", 'message': msg, 'aux_data':''}
			else:
				return {'type': "text", 'message': 'No item expiring today.', 'aux_data':''}

		elif self.conver_type == 'add_item':
			# switch case
			if self.conver_index == 0:
				self.conver_index += 1
				return {'type': "text", 'message': "What's the name of item?", 'aux_data':''}
			elif self.conver_index == 1:
				self.item['name'] = self.current_msg.lower()
				self.item['item_id'] = self.db.gen_id()
				self.conver_index += 1
				return {'type': "text", 'message': "What's the date of expiration?", 'aux_data':''}
			elif self.conver_index == 2:
				date_str = self.current_msg
				try:
					if date_str.count('.') == 2:
						date_obj = datetime.strptime(date_str, '%d.%m.%Y')
					else:
						date_obj = datetime.strptime(date_str, '%d.%m')
						date_str += '.2023'
				except ValueError:
					logging.info("Incorrect date format dd.mm.yyyy or dd.mm")
					return {'type': "text", 'message': "Tell me the date again in format dd.mm.yyyy or dd.mm", 'aux_data':''}
				self.item['expiry_date'] = date_str
				self.item['add_date'] = datetime.now().strftime('%d.%m.%Y')
				self.conver_index += 1
				return {'type': "text", 'message': "How many piece of {}?".format(self.item['name']), 'aux_data':''}
			elif self.conver_index == 3:
				try:
					self.item['quantity'] = int(self.current_msg)
					if self.item['quantity'] <= 0:
						return {'type': "text",'message': "Tell me the quantity again", 'aux_data':''}
				except ValueError:
					logging.info("Incorrect quantity format")
					return {'type': "text", 'message': "Tell me the quantity again", 'aux_data':''}
				self.conver_index += 1
				return {'type': "quick_reply", 'message': "Where will you store the item?", 'aux_data':['fridge home', 'fridge condo', 'fridge back home', 'cabinet home', 'cabinet condo']}
			
			elif self.conver_index == 4:
				self.item['store_place'] = self.current_msg
				self.conver_index += 1
				return {'type': "image", 'message': "Please give me a photo of that item", 'aux_data':''}
			
			elif self.conver_index == 5:

				# if user sent image
				if self.current_msg == 'save image':
					self.item['image_id'] = self.item['name'] + '_' + str(randint(100, 999))
					image_path = os.path.join(self.image_db_path, self.item['image_id'] + '.jpg')
					
					# push item to database
					self.db.push(self.item)

					self.conver_index = 0
					self.conver_type = ''

					return {'type': "image",'message': "Roger that!", 'aux_data':image_path}

				# if user sent text
				else:
					# push item to database
					self.db.push(self.item)

					self.conver_index = 0
					self.conver_type = ''

					return {'type': "text", 'message': "Roger that!", 'aux_data':''}
				
		elif self.conver_type == 'update_item':
			if self.conver_index == 0:
				self.conver_index += 1
				return {'type': "text", 'message': "What's the name of item you want to update?", 'aux_data':''}
			elif self.conver_index == 1:

				# check if is answer from quick reply
				# 'at' is keyword for quick reply from select item location
				if 'at' in self.current_msg.lower():
					
					self.item['item_id'] = self.current_msg.lower().split('_')[-1]


				# 'buy on' is keyword for quick reply from select buy date
				elif 'buy_on' in self.current_msg.lower():

					self.item['item_id'] = self.current_msg.lower().split('_')[-1]
				# else update item name
				else:

					self.item['name'] = self.current_msg.lower()
					# check if item is in database
					if len(self.db.get_id(name=self.item['name'], exist=True)) == 0:
						logging.info("Bot: Item is not in the list")

						self.conver_index = 0
						self.conver_type = ''

						return {'type': "text", 'message': 'Item is not in the list', 'aux_data':''}
					else:
						# check if items are in many locations
						place_list = self.db.df.loc[(self.db.df['name'] == self.item['name']) & (self.db.df['exist']==True),['store_place', 'add_date','item_id']].values.tolist()

						if len(set([p[0] for p in place_list])) > 1:
							return {'type':'quick_reply', 'message':'Please select item location', 'aux_data':[ '{}_at_{}_{}'.format(self.item['name'], p[0], p[2]) for p in place_list]}
					
						else:
							# there is one item or items are in one place
							if len(place_list) == 1:
								self.item['item_id'] = place_list[0][2]
							else:
								return {'type':'quick_reply', 'message':'Please select item buy date', 'aux_data':['{}_at_{}_buy_on_{}_{}'.format(self.item['name'], p[0], p[1], p[2]) for p in place_list]}
				
				self.conver_index += 1
				return {'type': "text", 'message': "What's the new quantity?", 'aux_data':''}
			elif self.conver_index == 2:
				self.item['quantity'] = int(self.current_msg)
				if self.item['quantity'] == 0:
					# delete item
					self.db.df.loc[self.db.df['item_id'] == self.item['item_id'], 'quantity'] = self.item['quantity']
					self.db.df.loc[self.db.df['item_id'] == self.item['item_id'], 'exist'] = False
					self.db.save_csv()

					self.conver_index = 0
					self.conver_type = ''

					return {'type': "text", 'message': "I deleted {}".format(self.item['name']), 'aux_data':''}
				else:
					# update item
					
					self.db.df.loc[self.db.df['item_id'] == self.item['item_id'], 'quantity'] = self.item['quantity']
					
					
					self.db.save_csv()

					self.conver_index = 0
					self.conver_type = ''

					return {'type': "text", 'message': "{} updated".format(self.item['name']), 'aux_data':''}


		elif self.conver_type == 'list_item':
			msg = "Here's all items:\n"
			for place in self.db.df.store_place.unique():
				# check if there is item in that place
				if len(self.db.df.loc[(self.db.df['store_place'] == place) & self.db.df['exist']]) > 0:
					msg += "\n" + place + "\n"
				else:
					continue
				for idx, row in self.db.df.loc[self.db.df['store_place'] == place].iterrows():
					if row['exist'] == True:
						date_diff =  datetime.strptime(row['expiry_date'], '%d.%m.%Y') - datetime.now().replace(hour=0, minute=0, second=0)
						msg += '- {} {} p. {} days left\n'.format(row['name'], row['quantity'], str(date_diff.days + 1))
			
			self.conver_index = 0
			self.conver_type = ""
			
			return {'type': "text", 'message': msg, 'aux_data':''}


def main() :

	con = Conversation("./database/data2.csv")

	server = CustomSocket('127.0.0.1', 10000, 'Socket server') #host =socket.gethostname()
	logging.info("[Socket server] Starting...")
	server.startServer()
	

	while True:
		try:
			conn, addr = server.sock.accept()
			logging.info("[Socket server] Client connected from {}".format(addr))

			while True:
				data = server.recvMsg(conn)

				logging.info('[Socket server] Received data: {}'.format(data.decode('utf-8')))
				con.push_msg(data.decode('utf-8'))
				res = con.response()
				logging.info('[Socket server] Responds: {}'.format(res))
				# send as dictionary
				server.sendMsg(conn, json.dumps(res))
		
		except Exception as e :
			logging.error('[Socket server] Error: {}'.format(e))

			# restart the server
			logging.info('[Socket server] Restarting...')
			server = CustomSocket('127.0.0.1',10000, 'Socket server') #host =socket.gethostname()
			server.startServer()

			continue


def manual_input_main():
	con = Conversation("./database/data2.csv")

	while True:
		# Get user input
		user_input = input("You: ")
		con.push_msg(user_input)
		print(con.response())


if __name__ == '__main__':
	main()
	# manual_input_main()

