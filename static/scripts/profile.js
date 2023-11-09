var arr = new Array(18)
var sc_promise = new Array(18)
var scores = new Array(18)

const shape = 18; //768
var calls = new Array(shape)

for (i = 0; i < shape; i++) {
    calls[i] = $.ajax({
        type: "GET",
        url: "/embvec/ourtag/" + (i + 1).toString(),
        dataType: 'json',
        data: {},
        success: function (newData) {
            pk = parseInt(newData["pk"]);

            arr[pk - 1] = newData["emb"];
            sc_promise[pk - 1] = predict(-1, newData);
        }
    })
}

tags = ["資訊", "工程", "數理化", "醫藥衛生", "生命科學", "生物資源",
    "地球與環境", "建築與設計", "藝術", "社會與心理", "大眾傳播", "外語",
    "文史哲", "教育", "法政", "管理", "財經", "遊憩與運動"]

$.when.apply(null, calls).then(async function () {
    var frame = document.querySelector('.Frame12');
    for (i = 0; i < shape; i++) {
        scores[i] = await sc_promise[i]
        if (scores[i] instanceof Error) {
            // frame.innerHTML = "<h3>個人模型尚未建立</h3>"
            return;
        }
    }


    $.ajax({
        type: "POST",
        url: "/persona/",
        dataType: 'json',
        data: {
            "scores": JSON.stringify(scores),
            "csrfmiddlewaretoken": CSRF_TOKEN
        },
        success: function (newData) {
            console.log(newData["url"])
            if (newData["url"] != "") {
                document.querySelector('.persona').src =
                    "/static" + newData["url"] + "?t=1"
            }
        }
    })


    var id;
    var elem;
    // frame.innerHTML = ""

    sc_sort = Array.from(Array(18).keys()).sort((a, b) => scores[b]-scores[a])
    console.log(sc_sort);

    $.ajax({
        type: "POST",
        url: "/top3/",
        dataType: 'json',
        data: {
            "sc_sort": JSON.stringify(sc_sort.map(val => val+1)),
            "csrfmiddlewaretoken": CSRF_TOKEN
        },
        success: function (newData) {
        }
    })

    // for (i = 0; i < 3; i++) {
    //     id = sc_sort[i];
    //     // console.log(sc_org);
    //     elem = document.createElement('div');
    //     elem.className = "Frame10";
    //     elem.innerHTML = "<div>" + tags[id] + "</div>"
    //     frame.appendChild(elem);

    //     console.log("success append " + i.toString())
    // }
});


// async function love_list() {
//     let love = await getData("love");
//     console.log(love)
// }

// love_list()