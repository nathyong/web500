/* This should handle the drawing of UI components such as cards as well as
 * bind actions card clicks etc.
 */
function Game(socket) {
    var game = {
        state: 'instantiated',
    };
    var deck;
    var $container = document.getElementById('container');
    var validMoves = [];

    function init(players) {
        deck = Deck(players.length === 6);

        deck.cards.forEach(function (card, i) {
            card.$el.addEventListener('mousedown', onTouch);
            card.$el.addEventListener('touchstart', onTouch);

            card.$el.addEventListener('mouseover', function() {
                if (validMoves.indexOf(card.i) !== -1) {
                    card.$el.style.cursor = 'pointer';
                } else {
                    card.$el.style.cursor = '';
                }
            });

            function onTouch () {
                if (validMoves.indexOf(card.i) !== -1) {
                    socket.sendRequest({
                        act: 'game_play',
                        data: card.i,
                    });
                    console.log('you played the right card!');
                    validMoves = [];
                } else {
                    console.log('you can\'t play that card yet!');
                }
            }
        });

        deck.mount($container);
        deck.intro();
        reset();
    }

    addListeners();

    function addListeners() {
        socket.addListener('game_start', function(message) {
            if (game.state === 'instantiated') {
                init(message.data);
            }
        });
        socket.addListener('game_reveal', function(message) {
            if (game.state === 'initialised') {
                reveal(message.data);
            }
        });
        socket.addListener('game_turn', function(message) {
            if (game.state === 'play') {
                validMoves = message.data;
            }
        });
        socket.addListener('game_reset', function(message) {
            if (game.state === 'ended') {
                reset();
            }
        });
    }

    function reset() {
        deck.flip('back');
        deck.shuffle();
        deck.shuffle();
        deck.deal();
        game.state = 'initialised';
    }

    function showKitty(newhand) {
        deck.addKitty(newhand);
        deck.showHand();
        game.state = 'kitty'; //waiting for kitty return
    }

    function reveal(hand) {
        deck.transform(hand);
        deck.showHand(true);
        deck.showHand();
        game.state = 'bidding';
    }

    return game;
}
