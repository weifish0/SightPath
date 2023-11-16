var arr = new Array(18)
var scores = new Array(18)

const shape = 18; //768
var calls = new Array(shape)

predict_ourtag();

tags = ["資訊", "工程", "數理化", "醫藥衛生", "生命科學", "生物資源",
    "地球與環境", "建築與設計", "藝術", "社會與心理", "大眾傳播", "外語",
    "文史哲", "教育", "法政", "管理", "財經", "遊憩與運動"]

// $.when.apply(null, calls).then(async function () {
async function predict_ourtag() {
    for (pk = 1; pk <= shape; pk++) {
        arr[pk - 1] = tagemb[pk.toString()];
        scores[pk - 1] = await predict(-1, arr[pk - 1]);
        if (scores[pk - 1] instanceof Error) {
            throw new Error("個人模型尚未建立");
        }
    }

    var frame = document.querySelector('.Frame12');
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
                document.querySelector('.persona_img').src =
                    "/static" + newData["url"] + "?t=1"
            }
        }
    })


    sc_sort = Array.from(Array(18).keys()).sort((a, b) => scores[b] - scores[a])
    console.log(sc_sort);

    $.ajax({
        type: "POST",
        url: "/top3/",
        dataType: 'json',
        data: {
            "sc_sort": JSON.stringify(sc_sort.map(val => val + 1)),
            "csrfmiddlewaretoken": CSRF_TOKEN
        },
        success: function (newData) {
        }
    })


    frame.replaceChildren(
        dom_elem(tags[sc_sort[0]]),
        dom_elem(tags[sc_sort[1]]),
        dom_elem(tags[sc_sort[2]])
    )
    console.log("success append 0,1,2")
}


function dom_elem(str) {
    elem = document.createElement('div');
    elem.className = "Frame10";

    elem_inner = document.createElement('div');
    elem_inner.innerHTML = str;

    elem.appendChild(elem_inner);
    return elem;
}