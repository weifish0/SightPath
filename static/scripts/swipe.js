// https://codepen.io/rudtjd2548/pen/qBodXzO

scaling = false
function onTouchStart(e) {
    if (e.touches.length >= 2) scaling = true;
    else scaling = false
}

function onPointerDown(e) {
    // e.classList.add('moving');
    startX = e.screenX //clientX
    startY = e.screenY

    e.target.addEventListener('pointermove', onPointerMove)
    e.target.addEventListener('pointerup', onPointerUp)
    e.target.addEventListener('pointerleave', onPointerUp)
    e.target.addEventListener('pointercancel', onPointerUp)
}

const range = 100;
function onPointerMove(e) {
    moveX = e.screenX - startX
    moveY = e.screenY - startY
    // console.log("move")

    if (!scaling) {
        tinderContainer.classList.toggle('tinder_love', moveX > 0);
        tinderContainer.classList.toggle('tinder_nope', moveX < 0);
        //rotate: (moveX / innerWidth) * 50
        if (moveY > range) setTransform(moveX, range, 0)
        else if (moveY < -range) setTransform(moveX, -range, 0)
        else setTransform(moveX, moveY, 0)
    }
}

function onPointerUp(e) {
    e.target.removeEventListener('pointermove', onPointerMove)
    e.target.removeEventListener('pointerup', onPointerUp)
    e.target.removeEventListener('pointerleave', onPointerUp)
    e.target.removeEventListener('pointercancel', onPointerUp)

    if (scaling || Math.abs(moveX) < range) cancel()
    else {
        e.target.removeEventListener('pointerdown', onPointerDown)
        complete()
    }
}

function setTransform(x, y, deg, duration) {
    allCards[0].style.transform = `translate3d(${x}px, ${y}px, 0) rotate(${deg}deg)`
    if (duration) allCards[0].style.transition = `transform ${duration}ms`
}

function complete() {
    moving = false;
    if (tinderContainer.classList.contains('tinder_love')) {        
        moving = true
        tinderContainer.classList.remove('tinder_love');
        storeData(allCards[0].id, true)
    } else if (tinderContainer.classList.contains('tinder_nope')) {
        moving = true;
        tinderContainer.classList.remove('tinder_nope');
        storeData(allCards[0].id, false)
    }

    if (moving) {
        const flyX = Math.sign(moveX) * innerWidth * 1.3
        const flyY = (moveY / moveX) * flyX
        setTransform(flyX, flyY, 0, innerWidth / 5) //rotate: (flyX / innerWidth) * 50
    }
    else return

    // el.classList.remove('moving');
    const keep = 0;
    allCards[0].classList.toggle('removed', !keep);
    setTimeout(function () {
        allCards[0].remove();
        initCards();

        allCards = document.querySelectorAll('.tinder--card');
        // if (allCards.length <= 1) loadCards(true);
    }, innerWidth / 5)
}

function cancel() {
    setTransform(0, 0, 0, 100)
    setTimeout(() => allCards[0].style.transition = '', 100)

    tinderContainer.classList.remove('tinder_love');
    tinderContainer.classList.remove('tinder_nope');
}