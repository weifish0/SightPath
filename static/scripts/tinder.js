//var nope = document.getElementById('nope');
//var love = document.getElementById('love');

var tinderContainer = document.querySelector('.tinder');
const shape = 18; //768
let score_cnt = 0;

initCards();
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
        //console.log("f")
        let db = e.target.result;
        let items;
        // get an object store to operate on it
        if (is_love) {
            let transaction = db.transaction("love", "readwrite"); // (1)
            items = transaction.objectStore("love"); // (2)
            if (id != '') ajax_save("love", id)
        }
        else {
            let transaction = db.transaction("nope", "readwrite"); // (1)
            items = transaction.objectStore("nope");
            if (id != '') ajax_save("nope", id)
        }

        if (id != '') suc = items.put(id, id);
        //items.add(8);

        db.close();
    };
    /*   if (!db.objectStoreNames.contains('books')) { // if there's no "books" store
          db.createObjectStore('books', {keyPath: 'id'}); // create it
      } */
}


function loadCards() {
    $.ajax({
        type: "GET",
        url: "/home_update",
        data: {},
        success: async function (newData) {
            console.log("null")
            $('.tinder--cards').html(newData);
            initCards();
            init();
        }
    });
}

function initCards() {
    var firstCard = document.querySelectorAll('.tinder--card:first-child')[0];

    if (firstCard == null) {
        loadCards();
        return;
    }

    $.ajax({
        type: "GET",
        url: "/embvec/comp/" + firstCard.id.toString(),
        dataType: 'json',
        data: {},
        success: function (newData) {
            const request = indexedDB.open("model_data");
            request.onsuccess = async function (e) {
                let db = e.target.result;
                let transaction = db.transaction("tmp", "readwrite"); // (1)
                let items = transaction.objectStore("tmp");

                let suc = items.add(newData, firstCard.id);
                db.close();

                /////////////////
                let score = await predict(firstCard.id);
                console.log(firstCard.id, score)
                if (score < 0.3) {
                    score_cnt++;
                    if (score_cnt >= 30) delete_data()

                    firstCard.remove();
                    initCards();
                }
                else {
                    score_cnt = 0;
                }
            };
        }
    });


    // firstCard.style.transition = "all 0.3s ease-in-out";

    var newCards = document.querySelectorAll('.tinder--card:not(.removed)');
    newCards.forEach(function (card, index) {
        //card.style.transition = "all 0.3s ease-in-out";
        card.style.zIndex = -index; // allCards.length - index
        // card.style.transform = 'scale(' + (20 - index) / 20 + ') translateY(-' + 30 * index + 'px)';
        if (index < 2) card.style.opacity = Math.pow(3, -index);
        else card.style.opacity = 0;
    });

    tinderContainer.classList.add('loaded');
}

function init() {
    var allCards = document.querySelectorAll('.tinder--card');

    /* getData("love").then(function(result){
        console.log("test-love:");
        console.log(result);
    }); */
    train();


    allCards.forEach(function (el) {
        var hammertime = new Hammer(el);

        hammertime.on('pan', function (event) {
            el.classList.add('moving');
        });

        hammertime.on('pan', function (event) {
            if (event.deltaX === 0) return;
            if (event.center.x === 0 && event.center.y === 0) return;
            // if (event.target.classList.contains("noHammer")) return; //austin 20230928
            if (event.target.style.zIndex != 0) return; //austin 20230929

            tinderContainer.classList.toggle('tinder_love', event.deltaX > 0);
            tinderContainer.classList.toggle('tinder_nope', event.deltaX < 0);


            var xMulti = event.deltaX * 0.03;
            var yMulti = event.deltaY / 80;
            var rotate = xMulti * yMulti;

            allCards[0].style.transform = 'translate(' + event.deltaX + 'px, ' + event.deltaY + 'px) rotate(' + rotate + 'deg)';
        });

        hammertime.on('panend pancancel', function (event) {
            // if (event.target.classList.contains("noHammer")) return; //austin 20230928
            if (event.target.style.zIndex != 0) return; //austin 20230929
            el.classList.remove('moving');
            tinderContainer.classList.remove('tinder_love');
            tinderContainer.classList.remove('tinder_nope');

            var keep = Math.abs(event.deltaX) < 80 || Math.abs(event.velocityX) < 0.2
            if (keep) {
                allCards[0].style.transform = '';
                return;
            }

            if (tinderContainer.classList.contains('tinder_love')) {
                storeData(allCards[0].id, true)
            }
            else storeData(allCards[0].id, false)

            var moveOutWidth = document.body.clientWidth;
            allCards[0].classList.toggle('removed', !keep);
            allCards[0].remove(); //austin 20230928


            var endX = Math.max(Math.abs(event.velocityX) * moveOutWidth, moveOutWidth);
            var toX = event.deltaX > 0 ? endX : -endX;
            var endY = Math.abs(event.velocityY) * moveOutWidth;
            var toY = event.deltaY > 0 ? endY : -endY;
            var xMulti = event.deltaX * 0.03;
            var yMulti = event.deltaY / 80;
            var rotate = xMulti * yMulti;

            allCards[0].style.transform = 'translate(' + toX + 'px, ' + (toY + event.deltaY) + 'px) rotate(' + rotate + 'deg)';
            initCards();

            allCards = document.querySelectorAll('.tinder--card');
            if (allCards.length < 4) loadCards();
        });
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
