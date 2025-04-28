(function ($) {
	
	"use strict";

	// Header Type = Fixed
  $(window).scroll(function() {
    var scroll = $(window).scrollTop();
    var box = $('.header-text').height();
    var header = $('header').height();

    if (scroll >= box - header) {
      $("header").addClass("background-header");
    } else {
      $("header").removeClass("background-header");
    }
  });


	$('.loop').owlCarousel({
      center: true,
      items:1,
      loop:true,
      autoplay: true,
      nav: true,
      margin:0,
      responsive:{ 
          1200:{
              items:5
          },
          992:{
              items:3
          },
          760:{
            items:2
        }
      }
  });
  
  $("#modal_trigger").leanModal({
		top: 100,
		overlay: 0.6,
		closeButton: ".modal_close"
});

$(function() {
		// Calling Login Form
		$("#login_form").click(function() {
				$(".social_login").hide();
				$(".user_login").show();
				return false;
		});

		// Calling Register Form
		$("#register_form").click(function() {
				$(".social_login").hide();
				$(".user_register").show();
				$(".header_title").text('Register');
				return false;
		});

		// Going back to Social Forms
		$(".back_btn").click(function() {
				$(".user_login").hide();
				$(".user_register").hide();
				$(".social_login").show();
				$(".header_title").text('Login');
				return false;
		});
});

  // Acc
  $(document).on("click", ".naccs .menu div", function() {
    var numberIndex = $(this).index();

    if (!$(this).is("active")) {
        $(".naccs .menu div").removeClass("active");
        $(".naccs ul li").removeClass("active");

        $(this).addClass("active");
        $(".naccs ul").find("li:eq(" + numberIndex + ")").addClass("active");

        var listItemHeight = $(".naccs ul")
          .find("li:eq(" + numberIndex + ")")
          .innerHeight();
        $(".naccs ul").height(listItemHeight + "px");
      }
  });
	

	// Menu Dropdown Toggle
  if($('.menu-trigger').length){
    $(".menu-trigger").on('click', function() { 
      $(this).toggleClass('active');
      $('.header-area .nav').slideToggle(200);
    });
  }


  // Menu elevator animation
  $('.scroll-to-section a[href*=\\#]:not([href=\\#])').on('click', function() {
    if (location.pathname.replace(/^\//,'') == this.pathname.replace(/^\//,'') && location.hostname == this.hostname) {
      var target = $(this.hash);
      target = target.length ? target : $('[name=' + this.hash.slice(1) +']');
      if (target.length) {
        var width = $(window).width();
        if(width < 991) {
          $('.menu-trigger').removeClass('active');
          $('.header-area .nav').slideUp(200);  
        }       
        $('html,body').animate({
          scrollTop: (target.offset().top) + 1
        }, 700);
        return false;
      }
    }
  });

  $(document).ready(function () {
      $(document).on("scroll", onScroll);
      
      //smoothscroll
      $('.scroll-to-section a[href^="#"]').on('click', function (e) {
          e.preventDefault();
          $(document).off("scroll");
          
          $('.scroll-to-section a').each(function () {
              $(this).removeClass('active');
          })
          $(this).addClass('active');
        
          var target = this.hash,
          menu = target;
          var target = $(this.hash);
          $('html, body').stop().animate({
              scrollTop: (target.offset().top) + 1
          }, 500, 'swing', function () {
              window.location.hash = target;
              $(document).on("scroll", onScroll);
          });
      });

      // Add more staff cards on button click
      $('#staff-more-btn').click(function() {
          var container = $('#staff-container');
          var currentCount = container.children().length;
          for (var i = 1; i <= 3; i++) {
              var newIndex = currentCount + i;
              var newCard = `
              <div class="col-lg-4 mb-4">
                <div class="card mb-3" style="max-width: 100%;">
                  <div class="row g-0">
                    <div class="col-md-4">
                      <img src="assets/images/staff-placeholder.png" class="img-fluid rounded-start" alt="Staff Member" />
                    </div>
                    <div class="col-md-8">
                      <div class="card-body">
                        <h5 class="card-title">Staff Member Name ${newIndex}</h5>
                        <p class="card-text"><small class="text-muted">Position / Role</small></p>
                        <p class="card-text">Brief description or bio of the staff member goes here. Highlight their expertise and contributions.</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>`;
              container.append(newCard);
          }
      });

      // Add more project cards on button click
      $('#project-more-btn').click(function() {
          var container = $('#project-container');
          var currentCount = container.children().length;
          for (var i = 1; i <= 3; i++) {
              var newIndex = currentCount + i;
              var newCard = `
              <div class="col-md-6 col-lg-3 mb-4">
                <div class="card" style="width: 18rem;">
                  <img src="assets/images/project-placeholder.png" class="card-img-top" alt="Project Image" />
                  <div class="card-body">
                    <h5 class="card-title">Project Title ${newIndex}</h5>
                    <p class="card-text">This is a brief description of the project. It highlights key features and objectives.</p>
                    <a href="#" class="btn btn-primary">Learn More</a>
                  </div>
                </div>
              </div>`;
              container.append(newCard);
          }
      });
  });

  function onScroll(event){
      var scrollPos = $(document).scrollTop();
      $('.nav a').each(function () {
          var currLink = $(this);
          var refElement = $(currLink.attr("href"));
          if (refElement.position().top <= scrollPos && refElement.position().top + refElement.height() > scrollPos) {
              $('.nav ul li a').removeClass("active");
              currLink.addClass("active");
          }
          else{
              currLink.removeClass("active");
          }
      });
  }


	// Page loading animation
	 $(window).on('load', function() {

        $('#js-preloader').addClass('loaded');

    });

	

	// Animate statistics numbers from 0 to final value
  function animateNumbers() {
    $('.statistic-item h3').each(function() {
      var $this = $(this);
      var countTo = parseInt($this.text());
      $({ countNum: 0 }).animate({ countNum: countTo }, {
        duration: 2000,
        easing: 'swing',
        step: function() {
          $this.text(Math.floor(this.countNum));
        },
        complete: function() {
          $this.text(this.countNum);
        }
      });
    });
  }

  // Trigger animation when statistics section is visible
  function isScrolledIntoView(elem) {
    var docViewTop = $(window).scrollTop();
    var docViewBottom = docViewTop + $(window).height();

    var elemTop = $(elem).offset().top;
    var elemBottom = elemTop + $(elem).height();

    return ((elemBottom <= docViewBottom) && (elemTop >= docViewTop));
  }

  $(window).on('scroll', function() {
    if (isScrolledIntoView('#statistics')) {
      animateNumbers();
      // Remove scroll event after animation to prevent repeated animation
      $(window).off('scroll');
    }
  });

  // Also trigger animation if statistics section is already visible on page load
  $(document).ready(function() {
    if (isScrolledIntoView('#statistics')) {
      animateNumbers();
    }
  });

})(window.jQuery);
