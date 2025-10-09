var express = require('express');
var router = express.Router();

router.get('/cards-page2', function(req, res, next) {
  res.render('cards-page2', { card: "images/Academy Ruins (Hill Memorial).png" });
});

router.get('/cards-page3', function(req, res, next) {
  res.render('cards-page3', { card: "images/Aragorn, the Uniter (Dr. Estell, the UI_UXer).png" });
});


module.exports = router;
