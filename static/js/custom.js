jQuery(document).ready(function($){

"use strict";

var nav_offset_top = $('header').height() + 345;


AOS.init();

// Navigation Scroll

function navbarOnScroll(){
    if ( $('.header-content').length){ 
        $(window).scroll(function() {
            var scroll = $(window).scrollTop();   
            if (scroll >= nav_offset_top ) {
                $(".header-content").addClass("navbar-scroll");
            } else {
                $(".header-content").removeClass("navbar-scroll");
            }
        });
    };
};
navbarOnScroll();

// SinglePage Scroll

 function SinglePage() {

    $(document).on('click', '#navbarCollapse a[href^="#"]', function (event) {
    event.preventDefault();
    var href = $.attr(this, 'href');
    $('html, body').animate({
        scrollTop: $($.attr(this, 'href')).offset().top
    }, 500, function() {
        // window.location.hash = href;
    });
    });

};

SinglePage();

// ScrollIt

function scroll() {
 $.scrollIt({
    upKey: 38,
    downKey: 40,
    activeClass: 'active',
    easing: 'swing',
    scrollTime: 600,
    onPageChange: null
 });
}

scroll();

  // About SkillBar

  function skillbar() {
 $(".skill-bar").each(function() {
    $(this).waypoint(function() {
        var progressBar = $(".progress-bar");
        progressBar.each(function(indx){
            $(this).css("width", $(this).attr("aria-valuenow") + "%")
        })
    }, {
        triggerOnce: true,
        offset: 'bottom-in-view'
    });
});
}

skillbar();

});



