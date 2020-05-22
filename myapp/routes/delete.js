var express = require('express');
var router = express.Router();
var db = require('../database');

//Delete a plant
router.get('/:plantid', function(req, res, next) {
	if (req.session.loggedin) {
		var plantid = req.params.plantid;
		var sql = 'DELETE FROM plantdata WHERE plantid = ?';
		db.query(sql, [plantid], function (err, data, fields) {
			if(err) throw err;
			res.render('delete', {title: 'Delete plant'});
		});
	} else {
		res.send('Please login to view this page!');
	}
});

module.exports = router;
