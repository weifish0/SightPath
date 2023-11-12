let ver = 0;
let run_upgraded = 1;

function getData(string, id = "no") {
    // console.log("version" + ver.toString())
    const request = indexedDB.open("model_data", ver + run_upgraded);
    return new Promise(function (resolve, reject) {
        request.onupgradeneeded = function (e) {
            run_upgraded = 0;

            db = e.target.result;
            console.log('running onupgradeneeded');
            const store_love = db.createObjectStore('love');
            const store_nope = db.createObjectStore('nope');
            const store_tmp = db.createObjectStore('tmp');
        };
        request.onsuccess = function (e) {
            let db = e.target.result;
            ver = db.version; // ver = ver + run_upgraded

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


function handleSave(artifacts) {
    // https://github.com/tensorflow/tfjs/issues/495
    // https://stackoverflow.com/questions/6965107/converting-between-strings-and-arraybuffers
    // https://github.com/feross/buffer
    // https://github.com/browserify/browserify

    artifacts.weightData = buffer.Buffer.from(artifacts.weightData)
        .toString("base64");
    // console.log(artifacts)

    $.ajax({
        type: "POST",
        url: "/save_model/",
        data: {
            "artifacts": JSON.stringify(artifacts),
            "csrfmiddlewaretoken": CSRF_TOKEN
        },
        success: async function (newData) {
        }
    });
    // console.log(artifacts.modelTopology);
    // console.log(artifacts.weightSpecs);
    // console.log(artifacts.weightData);
    return;
}

async function loadModel(){
    if (artifacts != "None") {
        artifacts = JSON.parse(artifacts.replace(/&quot;/g, '"'))
        weight = new Uint8Array(buffer.Buffer.from(artifacts.weightData, "base64")).buffer;
        artifacts.weightData = weight;

        model = await tf.loadLayersModel(tf.io.fromMemory(artifacts));
        model.save('indexeddb://model');
        artifacts = "None";

        console.log("model loaded from server")
    }
    else model = await tf.loadLayersModel('indexeddb://model');

    return model;
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
        model = await loadModel();
        model.compile({
            optimizer: 'adam',
            loss: 'binaryCrossentropy'
        });
    } catch (error) {
        console.log(error)
        console.log("indexeddb model not loaded")

        model = tf.sequential({
            layers: [
                tf.layers.dense({ units: 64, inputShape: [shape] }),
                tf.layers.dense({ units: 128 }),
                tf.layers.dense({ units: 64 }),
                // tf.layers.dropout(0.2),
                tf.layers.dense({ units: 1, activation: "sigmoid" })
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
            tf.concat([pos, neg], axis = 0), {
            batchSize: 4,
            epochs: 3
        });
        console.log("Loss after Epoch " + i + " : " + h.history.loss[0]);
    }

    model.save('indexeddb://model');
    // console.log(buffer.Buffer.from(model.getWeights()).toString("base64"))
    // let result = await model.save(tf.io.withSaveHandler(async modelArtifacts => modelArtifacts));
    model.save(tf.io.withSaveHandler(handleSave));
    // console.log(JSON.stringify(model.getWeights()));
}

async function predict(id, emb = []) {
    try {
        let tmp_emb;
        if (emb.length == 0) tmp_emb = await getData("tmp", id);
        else tmp_emb = emb;

        var model = await loadModel();
        tensor = tf.tensor(JSON.parse(tmp_emb["emb"]), [1, shape]);

        // console.log(model.predict(tensor).dataSync());
        return model.predict(tensor).dataSync()[0];
    } catch (error) {
        // console.log(error)
        return error;
    }
}

async function delete_data() {
    tf.io.removeModel('indexeddb://model');
    var request = indexedDB.deleteDatabase("model_data");
    request.onsuccess = function (e) {
        console.log("deleted  model_data successfully")
    }

    getData("love");
}