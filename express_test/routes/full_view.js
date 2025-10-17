var express = require('express');
var router = express.Router();

/* Get Home Page */
router.get('/', function(req, res, next){
    res.render('full_view', {
        cardName: "Doc-Gargac, Parun",
        altName: "Niv-Mizzet, Parun",
        manaCost: '{UUURRR}',
        cardType: "Legendary Creature - Dragon Wizard",
        oracleText: ["This spell can't be countered.", "Flying", "Whenever you draw a card, Doc-Gargac, Parun deals 1 damage to any target.", "Whenever a player casts an instant or sorcery spell, you draw a card.", "Test text {R}, {U}, Hit em again {RU}"],
        flavorText: "As a capstone professor, he is always working on a new project",
        power: 5,
        toughness: 5,
        rarity: "Rare",
        printing: "Nonfoil"
    });
});

module.exports = router;