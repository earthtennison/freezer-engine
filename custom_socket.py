"""
custom socket python program for text and image
ref: https://github.com/robocup-eic/robocup2022-cv-yolov5/blob/main/custom_socket.py
"""

import socket
import struct
import numpy as np
import json
import logging

class CustomSocket :

	def __init__(self,host,port,socket_name) :
		self.host = host
		self.port = port
		self.SPLITTER = b","
		self.sock = socket.socket()
		self.isServer = False
		self.socket_name = socket_name

	def startServer(self) :
		try :
			# solve address already in use error
			# https://python-list.python.narkive.com/Y15bAxfI/socket-unbind-or-socket-unlisten-socket-error-48-address-already-in-use
			self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			self.sock.bind((self.host,self.port))
			self.sock.listen(5)
			self.isServer = True
			logging.info("[{}] Started at port {}".format(self.socket_name, str(self.port)))
		except Exception as e :
			logging.error("Error : {}".format(e))
			return False
		return True

	def clientConnect(self) :
		try :
			logging.info("[Socket client] Connecting to {}:{}]".format(self.host, self.port))
			self.sock.connect((self.host,self.port))
			logging.info("[Socket client] Connected to {}:{}]".format(self.host, self.port))
		except Exception as e :
			logging.error("Error : {}".format(e))
			return False
		return True

	def sendMsg(self,sock,msg) :
		temp = msg
		try :
			temp = msg.encode('utf-8')
			logging.info("[{}] Data sent through socket".format(self.socket_name))
		except Exception as e :
			# This message is an image
			logging.info("[{}] Image sent through socket".format(self.socket_name))
		msg = struct.pack('>I', len(temp)) + temp
		sock.sendall(msg)

	def recvall(self,sock,n) :
		data = bytearray()

		while len(data) < n :
			packet = sock.recv(n - len(data))
			if not packet :
				return None
			data.extend(packet)
		return data

	def recvMsg(self,sock) :

		rawMsgLen = self.recvall(sock, 4)
		if not rawMsgLen :
			return None
		msgLen = struct.unpack('>I', rawMsgLen)[0]

		return self.recvall(sock, msgLen)

	def req(self,msg) :
		if type(msg) == str:
			self.sendMsg(self.sock,msg)
			result = self.recvMsg(self.sock).decode('utf-8')
			return json.loads(result)
		else:
			self.sendMsg(self.sock,msg.tobytes())
			result = self.recvMsg(self.sock)
			result = result.decode('utf-8')
			return json.loads(result)

	def register(self, image, name):
		command = b'register'+self.SPLITTER
		image = image[:,:,::-1].tobytes()
		name = self.SPLITTER + str(name).encode("utf-8")
		self.sendMsg(self.sock, command + image + name)
		return json.loads(self.recvMsg(self.sock).decode('utf-8'))
		
	def detect(self, image):
		command = b'detect'+self.SPLITTER
		image = image[:,:,::-1].tobytes()
		self.sendMsg(self.sock, command + image )
		return json.loads(self.recvMsg(self.sock).decode('utf-8'))

def main() :

	server = CustomSocket(socket.gethostname(),10000)
	server.startServer()

	while True:
		try:
			conn, addr = server.sock.accept()
			logging.info("Client connected from".format(addr))
			while True:
				
				data = server.recvMsg(conn)
				# img = np.frombuffer(data ,dtype=np.uint8).reshape(480,640,3)
				# print(img)
				print(data)
				server.sendMsg(conn, json.dumps({'a':'1','b':'2','c':'3'}))

		except Exception as e :
			print(e)
			print("Connection Closed")
			break

if __name__ == '__main__' :
	main()	