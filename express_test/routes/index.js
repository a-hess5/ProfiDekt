var express = require('express');
var router = express.Router();

/* GET home page. */
router.get('/', function(req, res, next) {
  res.render('index', { card: "images/Niv-Mizzet, Parun (Doc-Gargac, Parun).png" });
});

module.exports = router;
