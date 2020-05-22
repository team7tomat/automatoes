var express = require('express');
var router = express.Router();
var db = require('../database');

router.get('/:plantid', function(req, res, next) {
  var plantid = req.params.plantid;
  if (req.session.loggedin) {
    var sql = 'SELECT * FROM plantdata WHERE plantid = ?';
    db.query(sql, [plantid], function (err, data, fields) {
      if(err) throw err;
      res.render('edit', {title: 'Plant data', plantData: data});
    });
  } else {
    res.send('Please login to view this page!');
  }
});

router.post('/:plantid', function(req, res, next) {
  var plantid = req.body.plantid;
  var planttype = req.body.planttype === '' ? null : req.body.planttype // Sends null to the database if left blank
  var irrigation = req.body.irrigation === '' ? null : req.body.irrigation
  var photoperiod = req.body.photoperiod === '' ? null : req.body.photoperiod
  var luxgoal = req.body.luxgoal === '' ? null : req.body.luxgoal
  var blue = req.body.blue === '' ? null : req.body.blue
  var white = req.body.white === '' ? null : req.body.white
  var hred = req.body.hred === '' ? null : req.body.hred
  var nightbegin = req.body.nightbegin === '' ? null : req.body.nightbegin
  var nightend = req.body.nightend === '' ? null : req.body.nightend
  var pins = req.body.pins === '' ? null : req.body.pins
  var intensity = req.body.intensity === '' ? null : req.body.intensity
  var development = req.body.development === '' ? null : req.body.development

  if (req.session.loggedin) {
    var sql = 'UPDATE plantdata SET planttype = ?, irrigation = ?, photoperiod = ?, luxgoal = ?, blue = ?, white = ?, hred = ?, nightbegin = ?, nightend = ?, pins = ?, intensity = ?, development = ? WHERE plantid = ?';
    db.query(sql, [planttype, irrigation, photoperiod, luxgoal, blue, white, hred, nightbegin, nightend, pins, intensity, development, plantid], function (err, data, fields) {
      if(err) throw err;
      console.log(data)
      res.redirect('/account')
    });
  }
});

module.exports = router;
