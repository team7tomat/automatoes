var mysql = require('mysql');
var connection = mysql.createConnection({
	host     : 'localhost',
	user     : 'root',
	password : 'pass',
	database : 'tomato'
});

connection.connect(function(err) {
	if(err) throw err;
	console.log('Database is connected successfully!');
});

module.exports = connection;
