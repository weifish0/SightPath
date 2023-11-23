
var tinderContainer = document.querySelector('.tinder');
const shape = 18; //768
let score_cnt = 0;

getData("love");
initCards(false);
init();

function ajax_save(love_or_nope, id) {
    $.ajax({
        type: "POST",
        url: "/save_persona/",
        dataType: 'json',
        data: {
            "love_or_nope": love_or_nope,
            "id": id,
            "csrfmiddlewaretoken": CSRF_TOKEN
        },
        success: function (newData) {
        }
    })
}

function storeData(id, is_love) {
    const request = indexedDB.open("model_data");
    request.onsuccess = function (e) {
        let db = e.target.result;
        let items;
        // get an object store to operate on it
        if (is_love) {
            let transaction = db.transaction("love", "readwrite");
            items = transaction.objectStore("love");
            if (id != '') ajax_save("love", id)
        }
        else {
            let transaction = db.transaction("nope", "readwrite");
            items = transaction.objectStore("nope");
            if (id != '') ajax_save("nope", id);
        }

        if (id != '') suc = items.put(id, id);
        db.close();
    };
}


function loadCards(do_train = true) {
    $.ajax({
        type: "GET",
        url: "/home_update",
        data: {},
        success: function (newData) {
            console.log("loadCards")
            $('.tinder--cards').find('script').remove();
            $('.tinder--cards').append(newData);
            initCards();
            init();
            if (do_train) train();
        }
    })
}

async function initCards(do_train = true) {
    var firstCard = document.querySelectorAll('.tinder--card')[0];
    if (firstCard == null) {
        loadCards(do_train);
        return;
    }

    // "/embvec/comp/" + firstCard.id.toString()
    var newData = embvec[firstCard.id.toString()];

    const request = indexedDB.open("model_data");
    request.onsuccess = async function (e) {
        let db = e.target.result;
        let transaction = db.transaction("tmp", "readwrite"); // (1)
        let items = transaction.objectStore("tmp");
        // console.log("firstCard.id", firstCard.id)
        let suc = items.add(newData, firstCard.id);
        db.close();


        let score = await predict(firstCard.id);
        let ran = Math.random();

        console.log(firstCard.id, score, score + ran, ran)
        // Math.random();

        if (score + ran < 0.5) {
            score_cnt++;
            if (score_cnt >= 20) {
                delete_data();
            }
            firstCard.remove();
            initCards(false);

            // essential, to prevent the error:
            // classification.js:97 Uncaught (in promise) TypeError: Cannot read properties of undefined (reading 'emb') at train
            allCards = document.querySelectorAll('.tinder--card');
        }
        else {
            score_cnt = 0;

            var newCards = document.querySelectorAll('.tinder--card:not(.removed)');
            newCards.forEach(function (card, index) {
                if (index <= 1) card.style.opacity = 1;
                if (index >= 1) card.style.filter = "brightness(50%)";

                card.style.zIndex = -index;
                // card.style.transform = 'scale(' + (20 - index) / 20 + ') translateY(-' + 30 * index + 'px)';
            });
            newCards[0].style.cssText += "touch-action: pan-y pinch-zoom; pointer-events:auto;";
            newCards[0].style.filter = "none"
            newCards[0].querySelectorAll('*').forEach(function (child) {
                child.style.opacity = 1;
            });
        }
    };

    // firstCard.style.transition = "all 0.3s ease-in-out";
    tinderContainer.classList.add('loaded');
}


function init() {
    allCards = document.querySelectorAll('.tinder--card');
    allCards.forEach(function (e) {
        e.addEventListener('pointerdown', onPointerDown)
        e.addEventListener("touchstart", onTouchStart)
    });
}


/* function createButtonListener(love) {
    return function (event) {
        var cards = document.querySelectorAll('.tinder--card:not(.removed)');
        var moveOutWidth = document.body.clientWidth * 1.5;

        if (!cards.length) return false;

        var card = cards[0];

        card.classList.add('removed');

        if (love) {
            card.style.transform = 'translate(' + moveOutWidth + 'px, -100px) rotate(-30deg)';
        } else {
            card.style.transform = 'translate(-' + moveOutWidth + 'px, -100px) rotate(30deg)';
        }
        initCards();

        event.preventDefault();
    };
} */

//var nopeListener = createButtonListener(false);
//var loveListener = createButtonListener(true);

//nope.addEventListener('click', nopeListener);
//love.addEventListener('click', loveListener);