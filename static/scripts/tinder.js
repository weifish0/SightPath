//var nope = document.getElementById('nope');
//var love = document.getElementById('love');

var tinderContainer = document.querySelector('.tinder');
const shape = 18; //768
let score_cnt = 0;

initCards();
init();

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
        }
        else {
            let transaction = db.transaction("nope", "readwrite"); // (1)
            items = transaction.objectStore("nope");
        }

        if(id != '') suc = items.put(id, id);
        //items.add(8);

        db.close();
    };
    /*   if (!db.objectStoreNames.contains('books')) { // if there's no "books" store
          db.createObjectStore('books', {keyPath: 'id'}); // create it
      } */
}

async function predict(id) {
    let tmp_emb = await getData("tmp", id);
    try {
        const model = await tf.loadLayersModel('indexeddb://model');
        tensor = tf.tensor(JSON.parse(tmp_emb["emb"]), [1, shape]);

        // console.log(model.predict(tensor).dataSync());
        return model.predict(tensor).dataSync()[0];
    } catch (error) {
        return "err";
    }
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
        url: "/competition_vec/" + firstCard.id.toString(),
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
                if (score < 0.5) {
                    score_cnt++;
                    if (score_cnt >= 30) {
                        var rm = await tf.io.removeModel('indexeddb://model');
                        var request = indexedDB.deleteDatabase("model_data");
                        request.onsuccess = function (e) {
                            console.log("deleted  model_data successfully")
                        }

                        await getData("love");
                    }
                    
                    firstCard.remove();
                    initCards();
                }
                else {
                    score_cnt = 0;
                }
            };
        }
    });


    firstCard.style.transition = "all 0.3s ease-in-out";

    var newCards = document.querySelectorAll('.tinder--card:not(.removed)');
    newCards.forEach(function (card, index) {
        //card.style.transition = "all 0.3s ease-in-out";
        card.style.zIndex = -index; // allCards.length - index
        card.style.transform = 'scale(' + (20 - index) / 20 + ') translateY(-' + 30 * index + 'px)';
        if (index < 5) card.style.opacity = Math.pow(3, -index);
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

        hammertime.on('panend', function (event) {
            // if (event.target.classList.contains("noHammer")) return; //austin 20230928
            if (event.target.style.zIndex != 0) return; //austin 20230929

            el.classList.remove('moving');

            if (tinderContainer.classList.contains('tinder_love')) {
                tinderContainer.classList.remove('tinder_love');
                storeData(event.target.id, true)
            }
            else {
                tinderContainer.classList.remove('tinder_nope');
                storeData(event.target.id, false)
            }

            var moveOutWidth = document.body.clientWidth;
            var keep = 0;
            // var keep = Math.abs(event.deltaX) < 80 || Math.abs(event.velocityX) < 0.5

            allCards[0].classList.toggle('removed', !keep);
            allCards[0].remove(); //austin 20230928

            /* if (keep) {
                event.target.style.transform = '';
            } else { */
            var endX = Math.max(Math.abs(event.velocityX) * moveOutWidth, moveOutWidth);
            var toX = event.deltaX > 0 ? endX : -endX;
            var endY = Math.abs(event.velocityY) * moveOutWidth;
            var toY = event.deltaY > 0 ? endY : -endY;
            var xMulti = event.deltaX * 0.03;
            var yMulti = event.deltaY / 80;
            var rotate = xMulti * yMulti;

            allCards[0].style.transform = 'translate(' + toX + 'px, ' + (toY + event.deltaY) + 'px) rotate(' + rotate + 'deg)';
            initCards();

            //}
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
