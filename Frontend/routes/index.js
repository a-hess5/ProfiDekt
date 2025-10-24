const express = require('express');
const router = express.Router();
const axios = require('axios');

// Configure Flask API URL
const FLASK_API_URL = process.env.FLASK_API_URL || 'http://localhost:5000';

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
      per_page: 12
    };

    if (searchQuery) {
      params.search = searchQuery;
    }

    console.log(`\n[DEBUG /index] ========================================`);
    console.log(`[DEBUG /index] Calling Flask API at: ${FLASK_API_URL}/api/magiprof/cards`);
    console.log(`[DEBUG /index] Request Params:`, JSON.stringify(params));

    // Call Flask API with timeout
    const response = await axios.get(`${FLASK_API_URL}/api/magiprof/cards`, {
      params: params,
      timeout: 5000 // 5 second timeout
    });

    console.log(`[DEBUG /index] Flask API Response Status: ${response.status}`);
    console.log(`[DEBUG /index] Cards received: ${response.data.cards ? response.data.cards.length : 0}`);

    let cards = response.data.cards || [];
    const pagination = response.data.pagination || { page: 1, total_pages: 0, total: 0 };

    console.log(`[DEBUG /index] Cards Array Length: ${cards.length}`);
    console.log(`[DEBUG /index] Pagination:`, JSON.stringify(pagination));

    // Fix image paths - Flask returns relative paths, ensure they start with /
    if (cards.length > 0) {
      cards = cards.map(card => {
        let filepath = card.image_filepath;

        // Ensure path starts with / for absolute URL
        if (filepath) {
          if (!filepath.startsWith('/')) {
            filepath = '/' + filepath;
          }
        } else {
          filepath = '/card_images/default-card.png';
        }

        return {
          ...card,
          image_filepath: filepath
        };
      });

      console.log(`[DEBUG /index] Sample fixed path: ${cards[0].image_filepath}`);
    }

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

    // Get card image for featured section
    let cardImage = '/card_images/default-card.png';
    if (cards.length > 0 && cards[0].image_filepath) {
      cardImage = cards[0].image_filepath;
    }

    // Stats
    const stats = {
      total_cards: pagination.total || 0,
      unique_cards: pagination.total || 0
    };

    console.log(`[DEBUG /index] About to render with ${cards.length} cards`);
    console.log(`[DEBUG /index] ========================================\n`);

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
    console.error('\n[ERROR /index] ========================================');
    console.error('[ERROR /index] Error Type:', error.code || error.name);
    console.error('[ERROR /index] Error Message:', error.message);

    if (error.response) {
      console.error('[ERROR /index] Flask API Response Status:', error.response.status);
      console.error('[ERROR /index] Flask API Response Data:', JSON.stringify(error.response.data, null, 2));
    } else if (error.request) {
      console.error('[ERROR /index] No response received from Flask API');
      console.error('[ERROR /index] Request URL:', error.config?.url);
    } else {
      console.error('[ERROR /index] Error during request setup:', error.message);
    }
    console.error('[ERROR /index] FLASK_API_URL:', FLASK_API_URL);
    console.error('[ERROR /index] ========================================\n');

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
      error: `Unable to load cards. Flask API Error: ${error.message}. Is Flask running at ${FLASK_API_URL}?`
    });
  }
});

module.exports = router;