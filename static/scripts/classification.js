function getData(string, id = "no") {
    const request = indexedDB.open("model_data");
    return new Promise(function (resolve, reject) {
        request.onupgradeneeded = function (e) {
            db = e.target.result;
            console.log('running onupgradeneeded');
            const store_love = db.createObjectStore('love');
            const store_nope = db.createObjectStore('nope');
            const store_tmp = db.createObjectStore('tmp');
        };
        request.onsuccess = function (e) {
            let db = e.target.result;
            let transaction = db.transaction(string, "readwrite"); // (1)
            let items = transaction.objectStore(string);

            let records;
            if (id == "no") records = items.getAll();
            else records = items.get(id);

            records.onsuccess = function () {
                let love = records.result;
                resolve(love);
            };
            db.close();
        }
    });
}

const epoch_num = 1;

async function train() {
    let love = await getData("love");
    let nope = await getData("nope");
    let tmp_emb;
    let emb = [];

    //console.log(nope.length);
    for (let i = 0; i < love.length; i++) {
        tmp_emb = await getData("tmp", love[i]);
        emb.push(JSON.parse(tmp_emb["emb"]))
    }
    for (let i = 0; i < nope.length; i++) {
        tmp_emb = await getData("tmp", nope[i]);
        emb.push(JSON.parse(tmp_emb["emb"]))
    }

    let model;
    try {
        model = await tf.loadLayersModel('indexeddb://model');
        model.compile({
            optimizer: 'adam',
            loss: 'binaryCrossentropy'
        });
    } catch (error) {
        console.log("indexeddb model not loaded")

        model = tf.sequential({
            layers: [tf.layers.dense({
                units: 1,
                inputShape: [shape]
            })]
        });
        model.compile({
            optimizer: 'adam',
            loss: 'binaryCrossentropy'
        });
    }


    for (let i = 0; i < epoch_num; i++) {
        let pos = tf.fill([love.length, 1], 1);
        let neg = tf.fill([nope.length, 1], -1);

        const h = await model.fit(
            tf.tensor(emb),
            tf.concat([pos, neg], axis=0), {
            batchSize: 4,
            epochs: 3
        });
        console.log("love Loss after Epoch " + i + " : " + h.history.loss[0]);
    }

    const saveResults = await model.save('indexeddb://model');
}
