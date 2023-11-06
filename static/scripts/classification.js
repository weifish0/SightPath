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
            layers: [
                tf.layers.dense({units: 64, inputShape: [shape]}),
                tf.layers.dense({units: 128}),
                tf.layers.dense({units: 64}),
                // tf.layers.dropout(0.2),
                tf.layers.dense({units: 1, activation:"sigmoid"})
            ]
        });
        model.compile({
            optimizer: 'adam',
            loss: 'binaryCrossentropy'
        });
    }


    for (let i = 0; i < epoch_num; i++) {
        let pos = tf.fill([love.length, 1], 1);
        let neg = tf.fill([nope.length, 1], 0);

        const h = await model.fit(
            tf.tensor(emb),
            tf.concat([pos, neg], axis=0), {
            batchSize: 4,
            epochs: 3
        });
        console.log("Loss after Epoch " + i + " : " + h.history.loss[0]);
    }

    const saveResults = await model.save('indexeddb://model');
}

async function predict(id, emb=[]) {
    try {
        let tmp_emb;
        if (emb.length == 0) tmp_emb = await getData("tmp", id);
        else tmp_emb = emb;

        const model = await tf.loadLayersModel('indexeddb://model');
        tensor = tf.tensor(JSON.parse(tmp_emb["emb"]), [1, shape]);

        // console.log(model.predict(tensor).dataSync());
        return model.predict(tensor).dataSync()[0];
    } catch (error) {
        // console.log(error)
        return error;
    }
}

async function delete_data() {
    var rm = await tf.io.removeModel('indexeddb://model');
    var request = indexedDB.deleteDatabase("model_data");
    request.onsuccess = function (e) {
        console.log("deleted  model_data successfully")
    }

    await getData("love");
}