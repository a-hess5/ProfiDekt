const express = require('express');
const router = express.Router();
const axios = require('axios');

const FLASK_API_URL = process.env.FLASK_API_URL || 'http://localhost:5000';

// Helper function to fetch cards
async function fetchCards(page, query = {}) {
  try {
    const response = await axios.get(`${FLASK_API_URL}/api/cards/search`, {
      params: {
        q: query.searchQuery || '',
        view: query.viewType || 'cards',
        sort: query.sortBy || 'name',
        order: query.order || 'asc',
        page: page,
        per_page: 12
      }
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching cards:', error.message);
    return { cards: [], pagination: { page: 1, total_pages: 0 } };
  }
}

router.get('/cards-page2', async function(req, res, next) {
  const data = await fetchCards(2, req.query);
  const cardImage = data.cards.length > 0 
    ? `images/${data.cards[0].name}.png`
    : "images/Academy Ruins (Hill Memorial).png";
    
  res.render('cards-page2', { 
    cards: data.cards,
    cardImage: cardImage,
    pagination: data.pagination,
    filters: data.filters || {},
    query: req.query
  });
});

router.get('/cards-page3', async function(req, res, next) {
  const data = await fetchCards(3, req.query);
  const cardImage = data.cards.length > 0 
    ? `images/${data.cards[0].name}.png`
    : "images/Niv-Mizzet, Parun (Doc-Gargac, Parun).png";
    
  res.render('cards-page3', { 
    cards: data.cards,
    cardImage: cardImage,
    pagination: data.pagination,
    filters: data.filters || {},
    query: req.query
  });
});

// API endpoint for AJAX card loading
router.get('/api/cards', async function(req, res, next) {
  const page = parseInt(req.query.page) || 1;
  const data = await fetchCards(page, req.query);
  res.json(data);
});

module.exports = router;