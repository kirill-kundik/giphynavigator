const loadingLimit = 25;
let pageOffset = 0;
let canIncreaseOffset = true;

const urlParams = new URLSearchParams(window.location.search);
const q = urlParams.get('q');

let session;

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

function displayHistory() {
    let historyContainer = $('#history');

    historyContainer.empty();
    historyContainer.append($("<h2 class=\"history-title\">Search History</h2>"))

    $.each(session.history, function (index, element) {
        historyContainer.append(
            $("<p class=\"history-item\">" + element + "</p>")
        )
    })

    if(session.history.length === 0) {
        historyContainer.append(
            $("<p style='text-align: center; margin-bottom: 5px'><small>Empty 😢</small></p>")
        )
    }

    $('.history-item').click(function (e) {
        e.stopImmediatePropagation();
        window.location.href = "/search?q=" + $(this).text();
        return false;
    })
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
    return $("<div class=\"col-sm-3 col-md-2 py-2 gif-holder\" id=\"gif_" + gifObject.id + "\">" +
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
    if (gifs.length === 0) canIncreaseOffset = false;

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
                if (window.location.pathname === "/favorites/") {
                    $("#gif_" + gifId).remove();
                    gifsContainer.masonry();
                }
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

function addToHistory(query) {
    let checkExist = setInterval(function () {
        if (session !== undefined) {
            clearInterval(checkExist);
            $.ajax({
                type: 'POST',
                url: '/api/sessions/' + session.id + '/history?query=' + query,
                dataType: 'json',
                success: function () {
                    if (session.history.includes(query)) {
                        const index = session.history.indexOf(query);
                        if (index > -1) {
                            session.history.splice(index, 1);
                        }
                    }
                    session.history.unshift(query)
                    session.history = session.history.slice(0, 10);

                    displayHistory();
                }
            });
        }
    }, 100); // check every 100ms
}

function loadSearchGifs() {
    $.ajax({
        type: 'GET',
        url: '/api/search?query=' + q + '&limit=' + loadingLimit + '&offset=' + pageOffset,
        dataType: 'json',
        success: function (data) {
            if (data.hasOwnProperty('gifs'))
                addGifsToContainer(data.gifs)
            else
                alert("Cannot load GIFs")
        }
    });
}

function loadFavoritesGifs() {
    let checkExist = setInterval(function () {
        if (session !== undefined) {
            clearInterval(checkExist);
            $.ajax({
                type: 'GET',
                url: '/api/sessions/' + session.id + '/favorites?limit=' + loadingLimit + '&offset=' + pageOffset,
                dataType: 'json',
                success: function (data) {
                    if (data.hasOwnProperty('gifs'))
                        addGifsToContainer(data.gifs)
                    else
                        alert("Cannot load GIFs")
                }
            });
        }
    }, 100); // check every 100ms
}

function loadTrendingGifs() {
    $.ajax({
        type: 'GET',
        url: '/api/gifs/trending?limit=' + loadingLimit + '&offset=' + pageOffset,
        dataType: 'json',
        success: function (data) {
            if (data.hasOwnProperty('gifs'))
                addGifsToContainer(data.gifs)
            else
                alert("Cannot load GIFs")
        }
    });
}

function loadGifs() {
    console.log("loading gifs... limit=" + loadingLimit + ", offset=" + pageOffset + ", page=" + window.location.pathname)

    switch (window.location.pathname) {
        case "/favorites/":
            loadFavoritesGifs();
            break;
        case "/search/":
            loadSearchGifs();
            break;
        case "/":
        default:
            loadTrendingGifs();
    }
}

$(window).on('load', function () {
    initializeSession()
    let checkExist = setInterval(function () {
        if (session !== undefined) {
            console.log("Session initialized!");
            clearInterval(checkExist);
            displayHistory();
        }
    }, 100); // check every 100ms
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
        if (!canIncreaseOffset) return false;
        pageOffset += loadingLimit;
        loadGifs();
        return false;
    })
    loadMore.show(1000, function () {
        reloadDocumentHeight()
    })

    let searchInput = $('#search')
    let searchInputField = $('#searchField')

    $(document).on('keypress', function (e) {
        if (e.keyCode === 13) {
            const query = searchInput.val()
            if (query === '') {
                searchInputField.attr('data-tooltip', 'Search cannot be empty')
                searchInput.focus()
                window.scrollTo(0, 0)
                return false;
            }
            window.location.href = "/search?q=" + query;
            return false;
        }
    });

    searchInput.on('input', function () {
        searchInputField.attr('data-tooltip', 'Hit Enter ⏎')
    })

    if (q !== null) {
        addToHistory(q)
        searchInput.val(q);
        $('#resultTitle').text("Results for: '" + q + "'")
    }

    let history = $('#history');
    $('#historyBtn').click(function (e) {
        e.stopImmediatePropagation();
        if (history.hasClass("active")) {
            history.removeClass("active");
            history.hide("middle")
            $(this).css({ "color": "white" })
        } else {
            history.addClass("active");
            history.show("middle")
            $(this).css({ "color": "limegreen" })
        }
        return false;
    })
    $('#footerHistoryBtn').click(function (e) {
        e.stopImmediatePropagation();
        window.scrollTo(0, 0);
        history.addClass("active");
        history.show("middle")
    });
});
