function ajax_save(id_st, love_or_nope) {
    console.log(JSON.stringify(Array.from(id_st)))
    $.ajax({
        type: "POST",
        url: "/save_persona/",
        dataType: 'json',
        xhrFields: { withCredentials: true },
        crossDomain: true,
        data: {
            "love_or_nope": love_or_nope,
            "idstr_li": JSON.stringify(Array.from(id_st)),
            "csrfmiddlewaretoken": CSRF_TOKEN
        },
        success: function (newData) {
            console.log(newData)
        }
    })
    // data = {
    //     "love_or_nope": love_or_nope,
    //     "idstr_li": JSON.stringify(Array.from(id_st)),

    // }

    // fetch("/save_persona/", {
    //     credentials: "include",
    //     method: "POST", headers: { "X-CSRF-Token": CSRF_TOKEN },
    //     body: data,
    // })

    // .then(...).catch(...);
}

function storeData(id_st, love_or_nope) {
    const request = indexedDB.open("tinder_data");

    request.onupgradeneeded = function (e) {
        let db = e.target.result;
        console.log(`running onupgradeneeded, version: ${db.version}`);
        db.createObjectStore('data');
    };
    request.onsuccess = function (e) {
        ajax_save(id_st, love_or_nope)

        let db = e.target.result;
        // get an object store to operate on it
        let transaction = db.transaction("data", "readwrite");
        let items = transaction.objectStore("data");

        const req = items.get(love_or_nope);
        req.onsuccess = function () {
            const st = req.result || new Set();
            id_st.forEach(it => st.add(it))
            id_st.clear()
            const suc = items.put(st, love_or_nope);
        };
        db.close();
    }
}

let isLoading = false;
let lastScrollTop = 0;

// 初始加載
document.addEventListener('DOMContentLoaded', function() {
    const appContainer = document.getElementById('app');
    if (!appContainer) return;

    appContainer.addEventListener('scroll', function() {
        const scrollTop = this.scrollTop;
        const scrollHeight = this.scrollHeight;
        const clientHeight = this.clientHeight;

        // 滾動到底部時自動加載
        if (scrollHeight - scrollTop - clientHeight < 200) {
            loadCards();
        }
    });
});

function loadCards() {
    if (window.isLoading) return;
    window.isLoading = true;

    const currentCount = document.querySelectorAll('.swiper-slide').length;

    $.ajax({
        type: "GET",
        url: "/home_update",
        data: { offset: currentCount },
        success: function (newData) {
            if (newData.trim()) {
                const wrapper = document.querySelector('.swiper-wrapper');
                wrapper.insertAdjacentHTML('beforeend', newData);
            }
            window.isLoading = false;
        },
        error: function() {
            window.isLoading = false;
        }
    });
}

async function delete_data(del_url) {
    $.ajax({
        type: "POST",
        url: del_url,
        dataType: 'json',
        data: {
            "csrfmiddlewaretoken": CSRF_TOKEN
        },
        success: function (newData) {
            console.log(newData)
        }
    })

    let request = indexedDB.deleteDatabase("tinder_data");
    request.onsuccess = function () {
        console.log("deleted tinder_data successfully")
    }
    // getData("love");
}

// 按讚/按爛功能
// 注意：兩個按鈕都用 .card-action-btn class

document.addEventListener('click', function(e) {
    // Like
    if (e.target.closest('.card-like-btn')) {
        const btn = e.target.closest('.card-like-btn');
        const card = btn.closest('.custom-card');
        const compId = card.getAttribute('data-id');
        const compType = card.getAttribute('data-type');
        if (!compId || !compType) return;
        const idStr = `${compType}_${compId}`;
        // toggle 狀態
        if (btn.classList.contains('liked')) {
            btn.classList.remove('liked', 'animate');
        } else {
            btn.classList.remove('disliked');
            btn.classList.add('animate', 'liked');
            setTimeout(() => btn.classList.remove('animate'), 300);
        }
        storeData(new Set([idStr]), 'love');
    }
    // Dislike
    if (e.target.closest('.card-dislike-btn')) {
        const btn = e.target.closest('.card-dislike-btn');
        const card = btn.closest('.custom-card');
        const compId = card.getAttribute('data-id');
        const compType = card.getAttribute('data-type');
        if (!compId || !compType) return;
        const idStr = `${compType}_${compId}`;
        // toggle 狀態
        if (btn.classList.contains('disliked')) {
            btn.classList.remove('disliked', 'animate');
        } else {
            btn.classList.remove('liked');
            btn.classList.add('animate', 'disliked');
            setTimeout(() => btn.classList.remove('animate'), 300);
        }
        storeData(new Set([idStr]), 'nope');
    }
});

// Learn More 彈出 bottom sheet
document.addEventListener('click', function(e) {
    const learnMoreBtn = e.target.closest('.card-learnmore-btn');
    if (learnMoreBtn) {
        e.preventDefault();
        const card = learnMoreBtn.closest('.custom-card');
        const title = card.querySelector('.card-title').innerText;
        const tags = Array.from(card.querySelectorAll('.card-tag')).map(t => t.innerText);
        const date = card.querySelector('.card-date-text')?.innerText || '';
        const link = learnMoreBtn.getAttribute('href');
        const description = card.getAttribute('data-description') || '（請補充活動介紹內容）';

        document.getElementById('sheet-title').innerText = title;
        document.getElementById('sheet-labels').innerHTML =
            `<span class="sheet-label"><i class="fa fa-calendar"></i> ${date}</span>` +
            tags.map(t => `<span class="sheet-label">${t}</span>`).join('');
        document.getElementById('sheet-link').innerHTML =
            `<i class="fa fa-link"></i> <a href="${link}" target="_blank">${link}</a>`;
        document.getElementById('sheet-description').innerText = description;

        document.getElementById('activity-detail-sheet').classList.add('active');
        document.getElementById('activity-detail-mask').classList.add('active');
    }
});

function closeSheet() {
    document.getElementById('activity-detail-sheet').classList.remove('active');
    document.getElementById('activity-detail-mask').classList.remove('active');
}