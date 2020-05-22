var express = require('express');
var router = express.Router();
var db = require('../database');

router.get('/:plantid', function(req, res, next) {
  var plantid = req.params.plantid;
	if (req.session.loggedin) {
		var sql = 'SELECT * FROM plantdata WHERE plantid = ?';
		db.query(sql, [plantid], function (err, data, fields) {
			if(err) throw err;
			res.render('plants', {title: 'Plant data', plantData: data});
		});
	} else {
		res.send('Please login to view this page!');
	}
});

module.exports = router;
