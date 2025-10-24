const express = require('express');
const router = express.Router();
const axios = require('axios');

const FLASK_API_URL = process.env.FLASK_API_URL || 'http://localhost:5000';

// Helper function to fetch cards from Flask API
async function fetchCards(page = 1, query = {}) {
  try {
    const params = {
      page: page,
      per_page: 12
    };

    // Add search query if provided
    if (query.searchQuery) {
      params.search = query.searchQuery;
    }

    const response = await axios.get(`${FLASK_API_URL}/api/magiprof/cards`, {
      params: params
    });

    return response.data;
  } catch (error) {
    console.error('Error fetching cards from Flask API:', error.message);
    return { cards: [], pagination: { page: 1, total_pages: 0, total: 0 } };
  }
}

router.get('/cards-page2', async function(req, res, next) {
  try {
    const data = await fetchCards(2, req.query);

    // Get featured card image from first card or use default
    let cardImage = '/card_images/default-card.png';
    if (data.cards && data.cards.length > 0 && data.cards[0].image_filepath) {
      cardImage = '/' + data.cards[0].image_filepath;
    }

    res.render('cards-page2', {
      cards: data.cards || [],
      cardImage: cardImage,
      pagination: data.pagination || { page: 1, total_pages: 0, total: 0 },
      query: req.query
    });
  } catch (error) {
    console.error('Error rendering cards-page2:', error);
    res.render('cards-page2', {
      cards: [],
      cardImage: '/card_images/default-card.png',
      pagination: { page: 1, total_pages: 0, total: 0 },
      query: req.query,
      error: 'Unable to load cards'
    });
  }
});

router.get('/cards-page3', async function(req, res, next) {
  try {
    const data = await fetchCards(3, req.query);

    let cardImage = '/card_images/default-card.png';
    if (data.cards && data.cards.length > 0 && data.cards[0].image_filepath) {
      cardImage = '/' + data.cards[0].image_filepath;
    }

    res.render('cards-page3', {
      cards: data.cards || [],
      cardImage: cardImage,
      pagination: data.pagination || { page: 1, total_pages: 0, total: 0 },
      query: req.query
    });
  } catch (error) {
    console.error('Error rendering cards-page3:', error);
    res.render('cards-page3', {
      cards: [],
      cardImage: '/card_images/default-card.png',
      pagination: { page: 1, total_pages: 0, total: 0 },
      query: req.query,
      error: 'Unable to load cards'
    });
  }
});

// API endpoint for AJAX card loading
router.get('/api/cards', async function(req, res, next) {
  try {
    const page = parseInt(req.query.page) || 1;
    const data = await fetchCards(page, req.query);
    res.json(data);
  } catch (error) {
    console.error('Error in /api/cards endpoint:', error);
    res.status(500).json({
      error: 'Failed to fetch cards',
      cards: [],
      pagination: { page: 1, total_pages: 0, total: 0 }
    });
  }
});

module.exports = router;