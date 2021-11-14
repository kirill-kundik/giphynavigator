function scrollFooter(scrollY, heightFooter) {
    console.log(scrollY);
    console.log(heightFooter);

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

function getGifHtml(gifObject) {
    return $(
        "<div class=\"col-sm-4 col-md-3 py-2 gif-holder\">" +
        "<div class=\"gif card\" style=\"height: " + gifObject.embed_height + "px\">" +
        "<img src=\"" + gifObject.embed_url + "\">" +
        "</div>" +
        "</div>"
    )
}

function loadTrendingGifs() {
    $.ajax({
        type: 'GET',
        url: '/api/gifs/trending',
        dataType: 'json',
        success: function (data) {
            let gifsContainer = $('#gifs')
            $.each(data, function (index, element) {
                gifsContainer.append(getGifHtml(element)).each(function () {
                    gifsContainer.masonry('reloadItems');
                });
            });
            gifsContainer.masonry()
            $('#scroll-animate, #scroll-animate-main').css({
                'height': getHeightDocument() + 'px'
            });
        }
    });
}

function getHeightDocument() {
    return ($('.content').height()) + ($('footer').height() * 2 + 75)
}

$(window).on('load', function () {
    // let windowHeight = $(window).height()
    let footerHeight = $('footer').height()

    $('#scroll-animate, #scroll-animate-main').css({
        'height': getHeightDocument() + 'px'
    });

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

    console.log("loading trending gifs...")
    loadTrendingGifs()
});
