var express = require('express');
var router = express.Router();
var passwordValidator = require('password-validator');
var db = require('../database');

router.get('/:email', async function(req, res, next) {
	res.render('confirmreset');
	db.query('SELECT token FROM resettokens WHERE email = ?', [req.query.email], function(error, results, fields) {
  });

});

router.post('/', async function(req, res, next) {
  //compare passwords
  if (req.body.newpw !== req.body.confirmpw) {
    return res.json({status: 'error', message: 'Passwords do not match. Please try again.'});
  }

  var schema  = new passwordValidator(); // Password rules
  schema
  .is().min(8)
  .is().max(64)
  .has().uppercase()
  .has().lowercase()
  .has().digits()
  .has().not().spaces()
  .is().not().oneOf(['Tomat123','Password123', 'Qwerty1'])

  if(schema.validate(req.body.newpw) == true) {
    await db.query('UPDATE users SET clearpass = ? WHERE email = ?', [req.body.newpw, req.body.email], function(error, results, fields) {
    });
  } else {
    return res.json({status: 'NOT OK', message: 'Gör om gör rätt.'})
  }
	return res.redirect('/login');
});

module.exports = router;
