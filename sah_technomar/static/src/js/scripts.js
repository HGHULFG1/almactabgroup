$(function () {
  "use strict"

  /* Back to top button*/
  $(window).scroll(function() {
    if ($(this).scrollTop() > 100) {
      $('.back-to-top').fadeIn('slow');
    } else {
      $('.back-to-top').fadeOut('slow');
    }
  });
  $('.back-to-top').click(function(){
    $('html, body').animate({scrollTop : 0},1500, 'easeInOutExpo');
    return false;
  });

    $(".popup_close_icon").click(function(){
        Cookies.set('HomePopup', 'DESTROIED', { expires: 1 });
        $(".popup_discount_contain").fadeOut();
        return false;
    });
    //show_pre_popup();

       /* Initiate the wowjs animation library*/
       new WOW().init();

});

$(function() {
    'use strict';
    $('.langs_dropdown').on('click', function() {
        $(this).find('ul').toggle();
    });
    $('body').on('click', '.o_header_affix .langs_dropdown, .o_header_affix .langs_dropdown ul', function() {
        $(this).find('ul').toggle();
    });
    $(document).on('click', function() {
        $('.nav_menu_language').hide();
    });
    $(document).on('click', '.o_header_affix .langs_dropdown .nav_menu_language', function() {
        $(this).hide();
    });
    $('.langs_dropdown').on('click', function(e) {
        e.stopPropagation();
    });
    $('body').on('click', '.o_header_affix .langs_dropdown', function(e) {
        e.stopPropagation();
    });

})

function directTel(){
    window.open('tel:0012-345-6789');
}
function directEmail(){
    window.open('mailto:support@domain.com');
}

function openCategory(e,product_category) {
    $('.tab-head-item, .tabs_product_Category').removeClass("active");
    $(e).addClass("active");

    $('.cat-tab, .tab-content-item').hide();
    $('#'+product_category).fadeIn();

    $('.cat-tab, .tab-content-item').removeClass("active");
    $('#'+product_category).addClass("active");
    return false;
}