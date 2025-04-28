/**
 * Custom JavaScript for UI interactions
 * Dependencies: jQuery 3.3.1, Owl Carousel, leanModal
 */
(function ($, window, document) {
  'use strict';

  // Ensure jQuery is available
  if (!$ || typeof $.fn === 'undefined') {
    console.error('jQuery is not loaded. Please ensure jQuery is included before custom.js.');
    return;
  }

  // Header: Add background when scrolled past header text
  $(window).on('scroll', function () {
    const scroll = $(window).scrollTop();
    const boxHeight = $('.header-text').height() || 0;
    const headerHeight = $('header').height() || 0;

    if (scroll >= boxHeight - headerHeight) {
      $('header').addClass('background-header');
    } else {
      $('header').removeClass('background-header');
    }
  });

  // Owl Carousel: Initialize carousel with responsive settings
  if (typeof $.fn.owlCarousel === 'function') {
    $('.loop').owlCarousel({
      center: true,
      items: 1,
      loop: true,
      autoplay: true,
      nav: true,
      margin: 0,
      responsive: {
        760: { items: 2 },
        992: { items: 3 },
        1200: { items: 5 }
      }
    });
  } else {
    console.warn('Owl Carousel plugin is not loaded.');
  }

  // Lean Modal: Initialize modal with custom settings
  if (typeof $.fn.leanModal === 'function') {
    $('#modal_trigger').leanModal({
      top: 100,
      overlay: 0.6,
      closeButton: '.modal_close'
    });
  } else {
    console.warn('leanModal plugin is not loaded.');
  }

  // Login/Register Form Toggling
  $('#login_form').on('click', function (e) {
    e.preventDefault();
    $('.social_login').hide();
    $('.user_login').show();
  });

  $('#register_form').on('click', function (e) {
    e.preventDefault();
    $('.social_login').hide();
    $('.user_register').show();
    $('.header_title').text('Register');
  });

  $('.back_btn').on('click', function (e) {
    e.preventDefault();
    $('.user_login').hide();
    $('.user_register').hide();
    $('.social_login').show();
    $('.header_title').text('Login');
  });

  // Accordion: Toggle active menu items and adjust list height
  $(document).on('click', '.naccs .menu div', function () {
    const numberIndex = $(this).index();

    if (!$(this).hasClass('active')) {
      $('.naccs .menu div').removeClass('active');
      $('.naccs ul li').removeClass('active');

      $(this).addClass('active');
      $('.naccs ul').find(`li:eq(${numberIndex})`).addClass('active');

      const listItemHeight = $('.naccs ul').find(`li:eq(${numberIndex})`).innerHeight();
      $('.naccs ul').height(`${listItemHeight}px`);
    }
  });

  // Menu: Toggle dropdown on mobile
  if ($('.menu-trigger').length) {
    $('.menu-trigger').on('click', function () {
      $(this).toggleClass('active');
      $('.header-area .nav').slideToggle(200);
    });
  }

  // Smooth Scrolling: Scroll to section on link click
  $('.scroll-to-section a[href*="#"]:not([href="#"])').on('click', function (e) {
    if (
      location.pathname.replace(/^\//, '') === this.pathname.replace(/^\//, '') &&
      location.hostname === this.hostname
    ) {
      const target = $(this.hash);
      const validTarget = target.length ? target : $(`[name=${this.hash.slice(1)}]`);

      if (validTarget.length) {
        e.preventDefault();
        const width = $(window).width();
        if (width < 991) {
          $('.menu-trigger').removeClass('active');
          $('.header-area .nav').slideUp(200);
        }
        $('html, body').animate(
          { scrollTop: validTarget.offset().top + 1 },
          700
        );
        return false;
      }
    }
  });

  // Document Ready: Initialize scroll handling and dynamic content
  $(document).ready(function () {
    // Scroll: Highlight active nav link
    function onScroll() {
      const scrollPos = $(document).scrollTop();
      $('.nav a').each(function () {
        const currLink = $(this);
        const refElement = $(currLink.attr('href'));
        if (
          refElement.position().top <= scrollPos &&
          refElement.position().top + refElement.height() > scrollPos
        ) {
          $('.nav ul li a').removeClass('active');
          currLink.addClass('active');
        } else {
          currLink.removeClass('active');
        }
      });
    }

    $(document).on('scroll', onScroll);

    // Smooth Scroll: Enhanced scrolling for nav links
    $('.scroll-to-section a[href^="#"]').on('click', function (e) {
      e.preventDefault();
      $(document).off('scroll');

      $('.scroll-to-section a').removeClass('active');
      $(this).addClass('active');

      const target = $(this.hash);
      $('html, body').stop().animate(
        { scrollTop: target.offset().top + 1 },
        500,
        'swing',
        function () {
          window.location.hash = target.selector;
          $(document).on('scroll', onScroll);
        }
      );
    });

    // Staff Cards: Add more on button click
    $('#staff-more-btn').on('click', function () {
      const container = $('#staff-container');
      const currentCount = container.children().length;

      for (let i = 1; i <= 3; i++) {
        const newIndex = currentCount + i;
        const newCard = `
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

    // Project Cards: Add more on button click
    $('#project-more-btn').on('click', function () {
      const container = $('#project-container');
      const currentCount = container.children().length;

      for (let i = 1; i <= 3; i++) {
        const newIndex = currentCount + i;
        const newCard = `
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

  // Page Loading Animation
  $(window).on('load', function () {
    $('#js-preloader').addClass('loaded');
  });

  // Statistics Animation: Animate numbers when visible
  function animateNumbers() {
    $('.statistic-item h3').each(function () {
      const $this = $(this);
      const countTo = parseInt($this.text(), 10);
      $({ countNum: 0 }).animate(
        { countNum: countTo },
        {
          duration: 2000,
          easing: 'swing',
          step() {
            $this.text(Math.floor(this.countNum));
          },
          complete() {
            $this.text(this.countNum);
          }
        }
      );
    });
  }

  // Check if element is in viewport
  function isScrolledIntoView(elem) {
    const $elem = $(elem);
    if (!$elem.length) return false;

    try {
      const docViewTop = $(window).scrollTop();
      const docViewBottom = docViewTop + $(window).height();
      const elemTop = $elem.offset().top;
      const elemBottom = elemTop + $elem.height();

      return elemBottom <= docViewBottom && elemTop >= docViewTop;
    } catch (e) {
      console.error('Error checking scroll position:', e);
      return false;
    }
  }

  // Trigger statistics animation on scroll
  $(window).on('scroll', function () {
    if (isScrolledIntoView('#statistics')) {
      animateNumbers();
      $(window).off('scroll', this.handler); // Remove handler to prevent repeat
    }
  });

  // Trigger statistics animation if already visible on load
  $(document).ready(function () {
    if (isScrolledIntoView('#statistics')) {
      animateNumbers();
    }
  });
})(window.jQuery, window, document);