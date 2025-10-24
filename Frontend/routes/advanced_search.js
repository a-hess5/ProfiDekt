const express = require('express');
const router = express.Router();
const axios = require('axios');

const FLASK_API_URL = process.env.FLASK_API_URL || 'http://localhost:5000';

/* GET Advanced Search Page */
router.get('/', function(req, res, next) {
  res.render('advanced_search', {
    query: req.query,
    cards: [],
    pagination: { page: 1, total_pages: 0, total: 0 }
  });
});

/* POST Advanced Search - handle form submission */
router.post('/search', async function(req, res, next) {
  try {
    const filters = {
      card_name: req.body.card_name || '',
      rules_text: req.body.rules_text || '',
      card_color: req.body.card_color || '',
      type_line: req.body.type_line || '',
      mana_value: req.body.mana_value || '',
      power: req.body.power || '',
      toughness: req.body.toughness || '',
      flavor_text: req.body.flavor_text || '',
      department: req.body.department || '',
      page: parseInt(req.body.page) || 1,
      per_page: 12
    };

    // Call Flask API with filters
    const response = await axios.get(`${FLASK_API_URL}/api/magiprof/cards/search`, {
      params: filters
    });

    const { cards, pagination } = response.data;

    // Get featured card image
    let cardImage = '/card_images/default-card.png';
    if (cards.length > 0 && cards[0].image_filepath) {
      cardImage = '/' + cards[0].image_filepath;
    }

    res.render('advanced_search', {
      cards: cards || [],
      cardImage: cardImage,
      pagination: pagination || { page: 1, total_pages: 0, total: 0 },
      query: req.body,
      resultsShown: true
    });
  } catch (error) {
    console.error('Advanced search error:', error.message);
    res.render('advanced_search', {
      cards: [],
      cardImage: '/card_images/default-card.png',
      pagination: { page: 1, total_pages: 0, total: 0 },
      query: req.body,
      error: 'Error performing search. Please try again.'
    });
  }
});

module.exports = router;