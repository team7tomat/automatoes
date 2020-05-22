var express = require('express');
var router = express.Router();

router.post('/', function(req,res) {
  if (req.session.loggedin == true) {
    // delete session object
    req.session.destroy(function(err) {
      if(err) {
        return next(err);
      } else {
        return res.redirect('/');
      }
    });
  }
});

module.exports = router;
