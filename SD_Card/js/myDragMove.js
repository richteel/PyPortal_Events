// REF: https://stackoverflow.com/questions/9334084/moveable-draggable-div

class myDragMove {
    static move(divid, xpos, ypos) {
        divid.style.left = xpos + 'px';
        divid.style.top = ypos + 'px';
    }

    static startMoving(divid, container, evt) {
        evt = evt || window.event;
        var posX = evt.clientX,
            posY = evt.clientY,
            divTop = divid.style.top,
            divLeft = divid.style.left,
            eWi = parseInt(divid.style.width),
            eHe = parseInt(divid.style.height),
            cWi = parseInt(document.getElementById(container).style.width),
            cHe = parseInt(document.getElementById(container).style.height);
        document.getElementById(container).style.cursor = 'move';
        divTop = divTop.replace('px', '');
        divLeft = divLeft.replace('px', '');
        var diffX = posX - divLeft,
            diffY = posY - divTop;
        document.onmousemove = function (evt) {
            evt = evt || window.event;
            var posX = evt.clientX,
                posY = evt.clientY,
                aX = posX - diffX,
                aY = posY - diffY;
            if (aX < 0) aX = 0;
            if (aY < 0) aY = 0;
            if (aX + eWi > cWi) aX = cWi - eWi;
            if (aY + eHe > cHe) aY = cHe - eHe;
            myDragMove.move(divid, aX, aY);
        }
    }

    static stopMoving(container) {
        var a = document.createElement('script');
        document.getElementById(container).style.cursor = 'default';
        document.onmousemove = function () { }
    }
}