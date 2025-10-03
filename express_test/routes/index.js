// Update your index.js route file to connect with Flask API
const express = require('express');
const router = express.Router();
const axios = require('axios');

// Configure Flask API URL
const FLASK_API_URL = process.env.FLASK_API_URL || 'http://localhost:5000';

/* GET home page with card data */
router.get('/', async function(req, res, next) {
  try {
    // Get query parameters from URL
    const searchQuery = req.query.q || '';
    const viewType = req.query.view || 'cards';
    const sortBy = req.query.sort || 'name';
    const order = req.query.order || 'asc';
    const page = parseInt(req.query.page) || 1;
    
    // Call Flask API
    const response = await axios.get(`${FLASK_API_URL}/api/cards/search`, {
      params: {
        q: searchQuery,
        view: viewType,
        sort: sortBy,
        order: order,
        page: page,
        per_page: 11  // 11 cards as shown in your template
      }
    });

    const { cards, pagination, filters } = response.data;

    // Get stats for result banner
    const statsResponse = await axios.get(`${FLASK_API_URL}/api/cards/stats`);
    const stats = statsResponse.data;
    
    // Prepare card images - use first card if available
    const cardImage = cards.length > 0 
      ? `images/${cards[0].name}.png` 
      : "images/Niv-Mizzet, Parun (Doc-Gargac, Parun).png";
    
    res.render('index', { 
      cards: cards,
      cardImage: cardImage,
      pagination: pagination,
      filters: filters,
      stats: stats,
      query: {
        searchQuery: searchQuery,
        viewType: viewType,
        sortBy: sortBy,
        order: order
      }
    });
    
  } catch (error) {
    console.error('Error fetching cards:', error.message);
    // Fallback to default card if API fails
    res.render('index', { 
      cards: [],
      cardImage: "images/Niv-Mizzet, Parun (Doc-Gargac, Parun).png",
      pagination: { page: 1, total_pages: 0, total: 0 },
      filters: {},
      stats: { total_cards: 0, unique_cards: 0 },
      query: { searchQuery: '', viewType: 'cards', sortBy: 'name', order: 'asc' },
      error: 'Unable to load cards'
    });
  }
});

module.exports = router;