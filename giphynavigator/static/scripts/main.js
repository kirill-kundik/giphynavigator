const loadingLimit = 25;
let pageOffset = 0;

let session;
let sessionIsReady = false;

function scrollFooter(scrollY, heightFooter) {
    if (scrollY >= heightFooter) {
        $('footer').css({
            'bottom': '0px'
        });
    } else {
        $('footer').css({
            'bottom': '-' + heightFooter + 'px'
        });
    }
}

function getHeightDocument() {
    return ($('.content').height()) + ($('footer').height() * 2 + 75)
}

function reloadDocumentHeight() {
    $('#scroll-animate, #scroll-animate-main').css({
        'height': getHeightDocument() + 'px'
    });
}

function checkGifInFavorites(gifId) {
    return session.favorites.includes(gifId)
}

function addToFavorites(gifId) {
    $.ajax({
        type: 'POST',
        url: '/api/sessions/' + session.id + '/favorites?item_id=' + gifId,
        dataType: 'json',
        success: function (data) {
            session.favorites.push(gifId)
        }
    });
}

function removeFromFavorites(gifId) {
    $.ajax({
        type: 'DELETE',
        url: '/api/sessions/' + session.id + '/favorites?item_id=' + gifId,
        dataType: 'json',
        success: function (data) {
            const index = session.favorites.indexOf(gifId);
            if (index > -1) {
                session.favorites.splice(index, 1);
            }
        }
    });
}

function getGifHtml(gifObject) {
    let addedToFavorites = checkGifInFavorites(gifObject.id);
    return $("<div class=\"col-sm-3 col-md-2 py-2 gif-holder\">" +
        "<div class=\"gif card\" style='height: " + gifObject.embed_height + "px; background: url(\"" + gifObject.embed_url + "\") no-repeat center; background-size: contain;'>" +
        "<div class=\"description\">" +
        "<div class=\"icons-holder hovered\">" +
        "<i class=\"fas fa-heart favorites\" data-gif-id=\"" + gifObject.id + "\" style=\"color: " + (addedToFavorites ? 'red' : 'white') + ";\"></i>" +
        "<i class=\"fas fa-share\" onclick=\"window.open('" + gifObject.url + "');\"></i>" +
        "</div>" +
        "<p class=\"title hovered\">" + gifObject.title + "</p>" +
        "</div></div></div>");
}

function addGifsToContainer(gifs, empty = false) {
    let gifsContainer = $('#gifs')

    if (empty) gifsContainer.empty();

    $.each(gifs, function (index, element) {
        gifsContainer.append(getGifHtml(element)).each(function () {
            gifsContainer.masonry('reloadItems');
        });
        $('.favorites').click(function (e) {
            e.stopImmediatePropagation();
            const gifId = $(this).attr('data-gif-id');
            console.log("clicked " + gifId)
            if (checkGifInFavorites(gifId)) {
                removeFromFavorites(gifId)
                $(this).css({'color': 'white'});
            } else {
                addToFavorites(gifId)
                $(this).css({'color': 'red'});
            }
            return false;
        })
    });
    gifsContainer.masonry()
    reloadDocumentHeight()
}

function registerSession() {
    $.ajax({
        type: 'POST',
        url: '/api/sessions',
        dataType: 'json',
        success: function (data) {
            session = Object.assign({}, data)
            localStorage.setItem("SessionID", session.id)
        }
    });
}

function checkSession(sessionId) {
    $.ajax({
        type: 'GET',
        url: '/api/sessions/' + sessionId,
        dataType: 'json',
        success: function (data) {
            session = Object.assign({}, data)
            localStorage.setItem("SessionID", session.id)
        },
        error: function () {
            registerSession()
        }
    });
}

function initializeSession() {
    let sessionId = localStorage.getItem("SessionID");

    if (sessionId === null || sessionId === undefined) {
        registerSession()
    } else {
        checkSession(sessionId)
    }
}

function loadTrendingGifs() {
    $.ajax({
        type: 'GET',
        url: '/api/gifs/trending?limit=' + loadingLimit + '&offset=' + pageOffset,
        dataType: 'json',
        success: function (data) {
            addGifsToContainer(data)
        }
    });
}

function loadGifs() {
    console.log("loading gifs... limit=" + loadingLimit + ", offset=" + pageOffset)
    loadTrendingGifs();
}

$(window).on('load', function () {
    initializeSession()
    if (session === undefined) {
        let checkExist = setInterval(function () {
            if (session !== undefined) {
                sessionIsReady = true;
                console.log("Session initialized!");
                clearInterval(checkExist);
            }
        }, 100); // check every 100ms
    }
    // let windowHeight = $(window).height()
    let footerHeight = $('footer').height()

    // $('.wrapper-parallax').css({
    //     'margin-top': windowHeight + 'px'
    // });

    scrollFooter(window.scrollY, footerHeight);

    window.onscroll = function () {
        let scroll = window.scrollY;

        $('#scroll-animate-main').css({
            'top': '-' + scroll + 'px'
        });

        $('header').css({
            'background-position-y': 50 - (scroll * 100 / getHeightDocument()) + '%'
        });

        scrollFooter(scroll, footerHeight);
    }

    loadGifs()

    let loadMore = $('#loadMore')
    loadMore.click(function (e) {
        e.stopImmediatePropagation();
        pageOffset += loadingLimit;
        loadGifs();
        return false;
    })
    loadMore.show(1000, function () {
        reloadDocumentHeight()
    })
});
