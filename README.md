# Automatoes

# Information

The server is a central part of the project, it connects the different parts, hosts the webpage, holds the database and predicts images taken from the raspberry.

The server computer can be almost any computer, in this project a laptop running windows 10 was used. If we were to remake this project a server with a unix based os would save some time getting all automations to work properly.

## Webserver
The server is also a web server, hosting the website for the project. 
NodeJS 12.x was used to host and create the website.
Installation is easy, download and install nodejs from *[NodeJS](https://www.nodejs.org)*.
How to setup the required libraries and packages is covered in the GUI documentation.

## Database
In order to save and retrieve data of the plants/environment/raspberry pies, a database is needed.
We are using mysql 8.x. Installation is easy, download and install mysql from *[mysql](https://www.mysql.com/downloads/)*. There are two files (setup.sql and ddl.sql, found in the git repo) that needs to be ran from either cmd/terminal ‘mysql -u -p database_name < setup.sql’ or from a mysql workbench that can be installed as well. The workbench provides a graphical interface to the creation, editing and deleting of databases and their tables.

## Object detection
The server takes care of detecting tomatoes in  images taken by the raspberry pi.
