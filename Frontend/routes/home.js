const express = require('express');
const router = express.Router();

/* GET home page */
router.get('/', function(req, res, next) {
  res.render('home');
});

/* GET search page - handles search form submission */
router.get('/search', function(req, res, next) {
  const searchQuery = req.query.query || '';
  
  // Redirect to index with search query
  res.redirect(`/index?q=${encodeURIComponent(searchQuery)}`);
});

module.exports = router;