(function ($) {
  "use strict";

  // ========== Header Scroll Effect ==========
  function handleHeaderScroll() {
      var scroll = $(window).scrollTop();
      var box = $('.header-text').height();
      var header = $('header').height();

      $("header").toggleClass("background-header", scroll >= box - header);
  }

  // ========== Owl Carousel ==========
  function initOwlCarousel() {
      $('.loop').owlCarousel({
          center: true,
          items: 1,
          loop: true,
          autoplay: true,
          nav: true,
          margin: 0,
          responsive: {
              1200: { items: 5 },
              992: { items: 3 },
              760: { items: 2 }
          }
      });
  }

  // ========== Modal Functions ==========
  function initModals() {
      $("#modal_trigger").leanModal({
          top: 100,
          overlay: 0.6,
          closeButton: ".modal_close"
      });

      // Login/Register Form Toggles
      $("#login_form").click(function(e) {
          e.preventDefault();
          $(".social_login").hide();
          $(".user_login").show();
      });

      $("#register_form").click(function(e) {
          e.preventDefault();
          $(".social_login").hide();
          $(".user_register").show();
          $(".header_title").text('Register');
      });

      $(".back_btn").click(function(e) {
          e.preventDefault();
          $(".user_login, .user_register").hide();
          $(".social_login").show();
          $(".header_title").text('Login');
      });
  }

  // ========== Accordion Function ==========
  function initAccordion() {
      $(document).on("click", ".naccs .menu div", function() {
          var numberIndex = $(this).index();

          if (!$(this).hasClass("active")) {
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
  }

  // ========== Mobile Menu Toggle ==========
  function initMobileMenu() {
      if ($('.menu-trigger').length) {
          $(".menu-trigger").on('click', function() {
              $(this).toggleClass('active');
              $('.header-area .nav').stop().slideToggle(200);
          });
      }
  }

      // ========== Smooth Scrolling ==========
      function initSmoothScroll() {
          // Handle section scrolling
          $('.scroll-to-section a[href*="#"]:not([href="#"])').on('click', function(e) {
              if (location.pathname.replace(/^\//, '') === this.pathname.replace(/^\//, '') && 
                  location.hostname === this.hostname) {
                  
                  // Only proceed if this.hash starts with #
                  if (this.hash && this.hash.startsWith("#")) {
                      e.preventDefault();
                      var target = $(this.hash);
                      target = target.length ? target : $('[name=' + this.hash.slice(1) + ']');
                      
                      if (target.length) {
                          // Close mobile menu if open
                          if ($(window).width() < 991) {
                              $('.menu-trigger').removeClass('active');
                              $('.header-area .nav').stop().slideUp(200);
                          }

                          $('html, body').stop().animate({
                              scrollTop: target.offset().top + 1
                          }, 700);
                      }
                  }
              }
          });

          // Initialize scrollspy
          $(document).on("scroll", onScroll);
          
          // Enhanced smoothscroll with active class management
          $('.scroll-to-section a[href^="#"]').on('click', function(e) {
              // Only proceed if this.hash starts with #
              if (this.hash && this.hash.startsWith("#")) {
                  e.preventDefault();
                  $(document).off("scroll");
                  
                  $('.scroll-to-section a').removeClass('active');
                  $(this).addClass('active');
                  
                  var target = $(this.hash);
                  $('html, body').stop().animate({
                      scrollTop: target.offset().top + 1
                  }, 500, 'swing', function() {
                      window.location.hash = this.hash;
                      $(document).on("scroll", onScroll);
                  });
              }
          });
      }

  // ========== Scrollspy Function ==========
  function onScroll() {
      var scrollPos = $(document).scrollTop();
      
      $('.nav a[href^="#"]').each(function() {
          var currLink = $(this);
          var href = currLink.attr("href");
          
          // Only process hash links
          if (href && href.charAt(0) === '#') {
              try {
                  var refElement = $(href);
                  if (refElement.length) {
                      var elementTop = refElement.offset().top;
                      var elementBottom = elementTop + refElement.height();
                      
                      if (elementTop <= scrollPos && elementBottom > scrollPos) {
                          $('.nav a').removeClass("active");
                          currLink.addClass("active");
                      } else {
                          currLink.removeClass("active");
                      }
                  }
              } catch(e) {
                  console.error("Error processing navigation link:", e);
              }
          }
      });
  }

  // ========== Dynamic Content Loading ==========
  function initDynamicContent() {
      // Staff cards
      $('#staff-more-btn').click(function() {
          loadMoreItems('#staff-container', 'staff', 3);
      });

      // Project cards
      $('#project-more-btn').click(function() {
          loadMoreItems('#project-container', 'project', 3);
      });
  }

  function loadMoreItems(containerId, type, count) {
      var container = $(containerId);
      var currentCount = container.children().length;
      
      for (var i = 1; i <= count; i++) {
          var newIndex = currentCount + i;
          var newCard = generateCard(type, newIndex);
          container.append(newCard);
      }
  }

  function generateCard(type, index) {
      if (type === 'staff') {
          return `
              <div class="col-lg-4 mb-4">
                  <div class="card mb-3" style="max-width: 100%;">
                      <div class="row g-0">
                          <div class="col-md-4">
                              <img src="assets/images/staff-placeholder.png" class="img-fluid rounded-start" alt="Staff Member" />
                          </div>
                          <div class="col-md-8">
                              <div class="card-body">
                                  <h5 class="card-title">Staff Member Name ${index}</h5>
                                  <p class="card-text"><small class="text-muted">Position / Role</small></p>
                                  <p class="card-text">Brief description or bio of the staff member.</p>
                              </div>
                          </div>
                      </div>
                  </div>
              </div>`;
      } else { // project
          return `
              <div class="col-md-6 col-lg-3 mb-4">
                  <div class="card" style="width: 18rem;">
                      <img src="assets/images/project-placeholder.png" class="card-img-top" alt="Project Image" />
                      <div class="card-body">
                          <h5 class="card-title">Project Title ${index}</h5>
                          <p class="card-text">This is a brief description of the project.</p>
                          <a href="#" class="btn btn-primary">Learn More</a>
                      </div>
                  </div>
              </div>`;
      }
  }

  // ========== Number Animation ==========
  function initNumberAnimation() {
      // Check if element is in viewport
      function isInViewport(elem) {
          var rect = elem.getBoundingClientRect();
          return (
              rect.top <= (window.innerHeight || document.documentElement.clientHeight) &&
              rect.bottom >= 0
          );
      }

      // Animate numbers when visible
      function animateNumbers() {
          $('.statistic-item h3').each(function() {
              var $this = $(this);
              var countTo = parseInt($this.text().replace(/,/g, '')) || 0;
              
              $({ countNum: 0 }).animate({ countNum: countTo }, {
                  duration: 2000,
                  easing: 'swing',
                  step: function() {
                      $this.text(Math.floor(this.countNum).toLocaleString());
                  },
                  complete: function() {
                      $this.text(this.countNum.toLocaleString());
                  }
              });
          });
      }

      // Check on scroll and load
      function checkAnimation() {
          if ($('#statistics').length && isInViewport(document.getElementById('statistics'))) {
              animateNumbers();
              $(window).off('scroll', checkAnimation);
          }
      }

      $(window).on('scroll', checkAnimation);
      checkAnimation(); // Check on page load
  }

  // ========== Page Load Animation ==========
  function initPageLoad() {
      $(window).on('load', function() {
          $('#js-preloader').addClass('loaded');
      });
  }

  // ========== Initialize All Functions ==========
  $(document).ready(function() {
      handleHeaderScroll();
      $(window).scroll(handleHeaderScroll);
      
      initOwlCarousel();
      initModals();
      initAccordion();
      initMobileMenu();
      initSmoothScroll();
      initDynamicContent();
      initNumberAnimation();
      initPageLoad();
  });

})(window.jQuery);