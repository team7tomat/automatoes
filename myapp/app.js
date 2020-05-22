var createError = require('http-errors');
var express = require('express');
var path = require('path');
var session = require('express-session');
var cookieParser = require('cookie-parser');
var logger = require('morgan');

var indexRouter = require('./routes/index');
var accountRouter = require('./routes/account');
var aboutRouter = require('./routes/about');
var loginRouter = require('./routes/login');
var logoutRouter = require('./routes/logout');
var resetpwRouter = require('./routes/resetpw');
var confirmresetRouter = require('./routes/confirmreset');
var plantsRouter = require('./routes/plants');
var editRouter = require('./routes/edit');
var deleteRouter = require('./routes/delete');

var app = express();

// view engine setup
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'ejs');

app.use(logger('dev'));
app.use(express.json());
app.use(express.urlencoded({ extended: false }));
app.use(cookieParser());
app.use(session({
	secret: 'secret',
	resave: true,
	saveUninitialized: true
}));
app.use(express.static(path.join(__dirname, 'public')));

// view engine pages
app.use('/', indexRouter);
app.use('/account', accountRouter);
app.use('/about', aboutRouter);
app.use('/login', loginRouter);
app.use('/logout', logoutRouter);
app.use('/resetpw', resetpwRouter);
app.use('/confirmreset', confirmresetRouter);
app.use('/plants', plantsRouter);
app.use('/edit', editRouter);
app.use('/delete', deleteRouter);

// catch 404 and forward to error handler
app.use(function(req, res, next) {
  next(createError(404));
});

// error handler
app.use(function(err, req, res, next) {
  // set locals, only providing error in development
  res.locals.message = err.message;
  res.locals.error = req.app.get('env') === 'development' ? err : {};

  // render the error page
  res.status(err.status || 500);
  res.render('error');
});

module.exports = app;
