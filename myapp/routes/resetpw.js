var express = require('express');
var router = express.Router();
var db = require('../database');
var crypto = require('crypto');
const nodemailer = require('nodemailer');

process.env.DOMAIN = 'localhost:3000' // Local environment, change to public when publishing

/* GET forgot password page. */
router.get('/', function(req, res, next) {
  res.render('resetpw', { title: 'Reset pw' });
});

// Login for the mailsender
const transport = nodemailer.createTransport({
    host: 'smtp.sendgrid.net',
    port: 465,
    secure: true,
    auth: {
       user: 'apikey',
       pass: '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'
    }
});

router.post('/', async function(req, res, next) {
  //ensure that you have a user with this email
  var email = req.body.email;
  db.query('SELECT email FROM resettokens WHERE email = ?', [email], function(error, results, fields) {
    if (results.length > 0) {
      req.session.email = email;
      var fpSalt = crypto.randomBytes(64).toString('base64');
      var expireDate = new Date();
      expireDate.setHours(expireDate.getHours() + 1);
      db.query('UPDATE resettokens SET token = ?, expiration = ?, used = 0 WHERE email = ?', [fpSalt,expireDate,email], function(error, results, fields){});
      res.end()

      //create email
      const message = {
          from: process.env.SENDER_ADDRESS,
          to: req.body.email,
          replyTo: process.env.REPLYTO_ADDRESS,
          subject: process.env.FORGOT_PASS_SUBJECT_LINE,
          text: 'To reset your password, please click the link below.\n\n'+process.env.DOMAIN+'/confirmreset/'+req.body.email+'?token='+encodeURIComponent(fpSalt)
      };

      //send email
      transport.sendMail(message, function (err, info) {
         if(err) { console.log(err)}
         else { console.log(info); }
      });
    } else {
      return res.json({status: 'An email with details has been sent to the email adress'});
    }
  });
});
module.exports = router;
