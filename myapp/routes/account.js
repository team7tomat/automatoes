var express = require('express');
var router = express.Router();
var db = require('../database');

router.get('/', function(req, res, next) {
	if (req.session.loggedin) {
		var username = req.session.username;
		db.query("CALL show_raspis(?)", [username], function (err, data, fields) {
			if(err) throw err;
			console.log(data[0]);
			res.render('account', {title: 'Plant data', plantData: data[0]});
		});
	} else {
		res.redirect('/login');
	}
});

router.get('/add-plant', function(req, res, next) {
	if (req.session.loggedin) {
		res.render('addplant', {title: 'Add new Plant' });
	}
	else {
		res.send('Please login to view this page!');
	}
});


router.post('/add-plant', function(req, res, next) {
	if (req.session.loggedin) {
		console.log("adding plant");
		console.log(JSON.stringify(req.body, null, 4));
		var pins = req.body.bpin + "," + req.body.wpin + "," + req.body.hrpin + "," + req.body.lrpin;

		var ip = req.body.ip;
		ip = ip.replace(/\./g, '_');
		var img_location = "/images/" + ip + ".jpg";

		// db insert
		db.query("CALL new_raspi(?,?,?,?,?,?,?,?,?,?,?,?)",
		[req.body.ip, req.body.planttype, req.session.username, req.body.lux, req.body.blue, req.body.white, req.body.red, req.body.nightbegin, req.body.nightend, pins, req.body.intensity, img_location], function(err, data, fields) {
			if(err) throw(err);
			console.log(data[0]);
			res.redirect('/account');
		});
	}
	else {
		res.send('Please login to view this page!');
	}

});

module.exports = router;
