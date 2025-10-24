const express = require('express');
const router = express.Router();
const axios = require('axios');

// Configure Flask API URL
const FLASK_API_URL = process.env.FLASK_API_URL || 'http://localhost:5000';

// Handle window size tracking
router.post('/window-size', function(req, res) {
  res.json({ success: true });
});

/* GET index page with card data and filters */
router.get('/', async function(req, res, next) {
  try {
    // Get all query parameters
    const searchQuery = req.query.q || '';
    const page = parseInt(req.query.page) || 1;
    const viewType = req.query.view || 'cards';
    const display = req.query.display || 'images';
    const sortBy = req.query.sort || 'name';
    const order = req.query.order || 'asc';

    // Build params for Flask API
    const params = {
      page: page,
      per_page: 11
    };

    if (searchQuery) {
      params.search = searchQuery;
    }

    // Call Flask API
    const response = await axios.get(`${FLASK_API_URL}/api/magiprof/cards`, {
      params: params
    });

    let cards = response.data.cards || [];
    const pagination = response.data.pagination || { page: 1, total_pages: 0, total: 0 };

    // Apply sorting on frontend
    if (cards.length > 0) {
      cards.sort((a, b) => {
        let aVal, bVal;

        if (sortBy === 'year' || sortBy === 'release_date') {
          aVal = parseInt(a.card_year) || 0;
          bVal = parseInt(b.card_year) || 0;
          return order === 'desc' ? bVal - aVal : aVal - bVal;
        } else if (sortBy === 'card_number') {
          aVal = a.card_number || 0;
          bVal = b.card_number || 0;
          return order === 'desc' ? bVal - aVal : aVal - bVal;
        } else {
          // Default: sort by name
          aVal = (a.card_name || '').toLowerCase();
          bVal = (b.card_name || '').toLowerCase();
          return order === 'desc' ? bVal.localeCompare(aVal) : aVal.localeCompare(bVal);
        }
      });
    }

    // Get card image
    let cardImage = '/card_images/default-card.png';
    if (cards.length > 0 && cards[0].image_filepath) {
      cardImage = '/' + cards[0].image_filepath;
    }

    // Stats
    const stats = {
      total_cards: pagination.total || 0,
      unique_cards: pagination.total || 0
    };

    res.render('index', {
      cards: cards,
      cardImage: cardImage,
      pagination: pagination,
      filters: {},
      stats: stats,
      query: {
        searchQuery: searchQuery,
        viewType: viewType,
        display: display,
        sortBy: sortBy,
        order: order
      }
    });

  } catch (error) {
    console.error('Error fetching cards from Flask API:', error.message);
    res.render('index', {
      cards: [],
      cardImage: '/card_images/default-card.png',
      pagination: { page: 1, total_pages: 0, total: 0 },
      filters: {},
      stats: { total_cards: 0, unique_cards: 0 },
      query: {
        searchQuery: '',
        viewType: 'cards',
        sortBy: 'name',
        order: 'asc',
        display: 'images'
      },
      error: 'Unable to load cards. Is the Flask API running?'
    });
  }
});

module.exports = router;