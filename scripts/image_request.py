#!/usr/bin python
# coding=utf-8
# Use 'python' (3.8.2)
from socket import *
import re
import sys
import predict_image
import json
from time import sleep
from mysql import *
import mysql.connector
from mysql.connector import Error

"""
Row 54, filename: needs to be set to the image folder of the website

	How to use: python image_request.py
"""

minimum_percentage = 33
extract_detected_objects = False

detector = predict_image.load_model()

try:
	connection = mysql.connector.connect(host='127.0.0.1', database='tomato', user='user', password='pass', auth_plugin='mysql_native_password')
	if connection.is_connected():
		cursor = connection.cursor(buffered=True)
		print("db: connected")

		result = cursor.execute("call get_all_ip;", multi=True)
		hostnames = []
		for row in result:
			try:
				rows = row.fetchall()
				hostnames = [ host[0] for host in rows if len(host[0]) ]
				break
			except:
				break

		print(hostnames)

	else:
		print("db: not connected")
except Error as e:
	print(":(", e)
finally:
	if(connection.is_connected()):
		cursor.close()
		connection.close()
		print("db: connection closed")

hostport = 1337
for hostname in hostnames:
	filename = "C:\\Users\\WG\\Desktop\\hemsidan2.0\\myapp\\public\\images\\" + hostname.replace('.', '_') + '.jpg'

	client_socket = socket(AF_INET, SOCK_STREAM)
	client_socket.settimeout(2)

	print(f"pi: trying to connect to {hostname}")
	try:
		client_socket.connect((hostname, hostport))
	except:
		continue

	client_socket.send("image".encode())
	data = bytes("", "utf-8")

	while True:
		new_data = client_socket.recv(4096)
		data += new_data

		if not new_data:
			with open(filename, "wb") as file:
				file.write(data)
				print("created file")
			break

	print("Analyzing image")
	tomatoes = predict_image.predict_image(filename, minimum_percentage, extract_detected_objects, detector)

	output = ""
	output += f'{len(tomatoes["ripe"])} ripe tomatoes\n' if "ripe" in tomatoes else ""
	output += f'{len(tomatoes["non_ripe"])} non-ripe tomatoes' if "non_ripe" in tomatoes else ""

	tomatoes = { "ripe" : len(tomatoes["ripe"]), "non_ripe" : len(tomatoes["non_ripe"]) }

	client_socket.close()
	sleep(1)
	client_socket = socket(AF_INET, SOCK_STREAM)
	client_socket.settimeout(1)
	client_socket.connect((hostname, hostport))
	client_socket.send(f"tomatoes{json.dumps(tomatoes)}".encode())
	print(json.dumps(tomatoes))

	client_socket.close()

	client_socket = socket(AF_INET, SOCK_STREAM)
	client_socket.settimeout(1)
	client_socket.connect((hostname, hostport))

	client_socket.send("sunlight".encode())
	print("pi: getting sun data")
	data = bytes("", "utf-8")

	while True:
		try:
			new_data = client_socket.recv(4096)
		except timeout as t:
			with open('text.txt', "wb") as file:
				file.write(data)
				print("created file")
			break

		finally:
			if not new_data:
				print("pi: sun data collected")
				with open('text.txt', "wb") as file:
					file.write(data)
					print("created file")
				break
			data += new_data
			#print("collecting")

	client_socket.close()

	try:
		connection = mysql.connector.connect(host='127.0.0.1', database='tomato', user='user', password='pass', auth_plugin='mysql_native_password')
		if connection.is_connected():
			cursor = connection.cursor()
			print("db: connected")
			file = open('text.txt')
			str = file.read()
			lines = str.split('\n')
			for line in lines[:-1]:
				#print(line, line.split(','))
				light, date = line.split(',')[0], line.split(',')[1]
				#cursor.execute("call log_light(%d, %s);", (light, date))
				cursor.execute("call log_light({},'{}');".format(light, date))

			cursor.execute("call tomato_firsts({},{},'{}');".format(tomatoes["ripe"], tomatoes["non_ripe"],hostname, ))
			connection.commit()

		else:
			print("db: not connected")
	except Error as e:
		print(":(", e)
	finally:
		if(connection.is_connected()):
			cursor.close()
			connection.close()
			print("db: connection closed")
