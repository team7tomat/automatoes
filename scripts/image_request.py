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
	Needs to have a .h5 file in the folder tomato/models named 'detection_model-ex-052--loss-0033.691.h5'
	Needs to have a .json file in the folder tomato/json named 'detection_config.json'

	How to use: python image_request.py
"""

minimum_percentage = 40

detector = predict_image.load_model()

# get the ip addresses of all the raspberry pis
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
	# filename becomes the ip address but separated with '_' instead of '.'
	filename = "C:\\Users\\WG\\Desktop\\hemsidan2.0\\myapp\\public\\images\\" + hostname.replace('.', '_') + '.jpg'

	client_socket = socket(AF_INET, SOCK_STREAM)
	client_socket.settimeout(2)

	print(f"pi: trying to connect to {hostname}")
	try:
		client_socket.connect((hostname, hostport))
	except:
		print(f"pi: connection to {hostname} timed out")
		continue

	# sending a request to the raspberry pi to take an image
	client_socket.send("image".encode())
	data = bytes("", "utf-8")

	while True:
		new_data = client_socket.recv(4096)
		data += new_data

		if not new_data:
			# all data received, store on disk
			with open(filename, "wb") as file:
				file.write(data)
				print("created file")
			break

	print("Analyzing image")
	tomatoes = predict_image.predict_image(filename=filename, minimum_percentage=minimum_percentage, extract_detected_objects=False, detector=detector)

	output = ""
	output += f'{len(tomatoes["ripe"])} ripe tomatoes\n' if "ripe" in tomatoes else ""
	output += f'{len(tomatoes["non_ripe"])} non-ripe tomatoes' if "non_ripe" in tomatoes else ""

	tomatoes = { "ripe" : len(tomatoes["ripe"]), "non_ripe" : len(tomatoes["non_ripe"]) }

	client_socket.close()
	sleep(1)
	client_socket = socket(AF_INET, SOCK_STREAM)
	client_socket.settimeout(1)
	client_socket.connect((hostname, hostport))
	# sending tomato data back to the raspberry pi
	client_socket.send(f"tomatoes{json.dumps(tomatoes)}".encode())
	print(json.dumps(tomatoes))

	client_socket.close()

	client_socket = socket(AF_INET, SOCK_STREAM)
	client_socket.settimeout(1)
	client_socket.connect((hostname, hostport))

	# sending a request to the raspberry pi to send the sunlight data
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

	client_socket.close()

	try:
		connection = mysql.connector.connect(host='127.0.0.1', database='tomato', user='user', password='pass', auth_plugin='mysql_native_password')
		if connection.is_connected():
			cursor = connection.cursor()
			print("db: connected")
			file = open('text.txt')
			str = file.read()
			lines = str.split('\n')
			# store sunlight data in the database
			for line in lines[:-1]:
				light, date = line.split(',')[0], line.split(',')[1]
				cursor.execute("call log_light({},'{}');".format(light, date))


			# store statistics about the plant in the database
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
