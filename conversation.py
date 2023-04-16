"""
Conversation manager program as a socket server for receiving text and image messages from app.py
"""

from csv_database import csv_database

# for datetime type
from datetime import datetime

# custom socket
from custom_socket import CustomSocket
import json

class Conversation():
	def __init__(self, db_path):

		# current message user input
		self.current_msg = ""

		# conver_type are add_item, update_item, list_item
		self.conver_type = ""

		self.conver_index = 0

		self.item = {'name':None, 'expiry_date':None, 'store_place':None, 'quantity':None, 'category':None}

		self.db = csv_database(db_path)




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
		# print("Bot:",self.current_msg)

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
			return {'type': "text", 'message': msg, 'aux_data':''}
				
		elif self.conver_type == 'check':
			msg = 'Expiring item! :'
			item_cnt = 0
			for idx, row in self.db.df.iterrows():
				date_diff =  datetime.strptime(row['expiry_date'], '%d.%m.%Y') - datetime.now().replace(hour=0, minute=0, second=0)
				if  0 <= date_diff.days + 1 < 2: # 0-2 days
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
					print("Incorrect date format dd.mm.yyyy or dd.mm")
					return {'type': "text", 'message': "Tell me the date again in format dd.mm.yyyy or dd.mm", 'aux_data':''}
				self.item['expiry_date'] = date_str # todo set to default data format
				self.conver_index += 1
				return {'type': "text", 'message': "How many piece of {}?".format(self.item['name']), 'aux_data':''}
			elif self.conver_index == 3:
				try:
					self.item['quantity'] = int(self.current_msg)
				except ValueError:
					print("Incorrect quantity format")
					return {'type': "text", 'message': "Tell me the quantity again", 'aux_data':''}
				self.conver_index += 1
				return {'type': "text", 'message': "Where will you store the item? fridge home, fridge back home, fridge condo, cabinet", 'aux_data':''}
			elif self.conver_index == 4:
				self.item['store_place'] = self.current_msg

				# push item to database
				self.db.push(self.item)

				self.conver_index = 0
				self.conver_type = ''

				return {'type': "text", 'message': "Roger that!", 'aux_data':''}
			# todo add picture
				
		elif self.conver_type == 'update_item':
			if self.conver_index == 0:
				self.conver_index += 1
				return {'type': "text", 'message': "What's the name of item you want to update?", 'aux_data':''}
			elif self.conver_index == 1:
				self.item['name'] = self.current_msg.lower()
				# check if item is in database
				if self.item['name'] not in self.db.df['name'].to_list():
					print("Bot: Item is not in the list")

					self.conver_index = 0
					self.conver_type = ''

					return {'type': "text", 'message': 'Item is not in the list', 'aux_data':''}
				self.conver_index += 1
				return ('text', "What's the new quantity?", '')
			elif self.conver_index == 2:
				self.item['quantity'] = int(self.current_msg)
				if self.item['quantity'] == 0:
					# delete item
					self.db.df = self.db.df.loc[self.db.df['name'] != self.item['name']]
					self.db.save_csv()

					self.conver_index = 0
					self.conver_type = ''

					return {'type': "text", 'message': "I deleted {}".format(self.item['name']), 'aux_data':''}
				else:
					# update item
					self.db.df.loc[self.db.df['name'] == self.item['name'],'quantity'] = self.item['quantity']
					self.db.save_csv()

					self.conver_index = 0
					self.conver_type = ''

					return {'type': "text", 'message': "{} updated".format(self.item['name']), 'aux_data':''}


		elif self.conver_type == 'list_item':
			msg = "Here's all items:\n"
			for idx, row in self.db.df.iterrows():
				msg += '- ' + row['name'] + '\n'
			
			self.conver_index = 0
			self.conver_type = ""
			
			return {'type': "text", 'message': msg, 'aux_data':''}


def main() :

	con = Conversation("./database/data1.csv")

	server = CustomSocket('0.0.0.0',10000) #host =socket.gethostname()
	print("[Starting server]")
	server.startServer()
	

	while True:
		try:
			conn, addr = server.sock.accept()
			print("Client connected from",addr)

			while True:
				data = server.recvMsg(conn)

				print(data.decode('utf-8'))
				con.push_msg(data.decode('utf-8'))
				res = con.response()
				print(res)
				# send as dictionary
				server.sendMsg(conn, json.dumps(res))
		
		except Exception as e :
			print(e)
			print("Connection Closed")
			break


def manual_input_main():
	con = Conversation("./database/data1.csv")

	while True:
		# Get user input
		user_input = input("You: ")
		con.push_msg(user_input)
		print(con.response())


if __name__ == '__main__':
	main()

