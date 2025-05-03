document.addEventListener('DOMContentLoaded', function () {
	const slides = document.querySelectorAll('.staff-slider .staff-slide');
	const dots = document.querySelectorAll('.staff-dots .dot');
	let currentIndex = 0;
	let slideInterval;
  
	function showSlide(index) {
	  slides.forEach((slide, i) => {
		slide.classList.remove('active');
		slide.style.transform = i < index ? 'translateX(-100%)' : 'translateX(100%)';
		slide.style.opacity = '0';
		if (i === index) {
		  slide.classList.add('active');
		  slide.style.transform = 'translateX(0)';
		  slide.style.opacity = '1';
		}
	  });
	  dots.forEach((dot, i) => {
		dot.classList.toggle('active', i === index);
	  });
	  currentIndex = index;
	}
  
	function nextSlide() {
	  showSlide((currentIndex + 1) % slides.length);
	}
  
	dots.forEach((dot, index) => {
	  dot.addEventListener('click', () => {
		if (slideInterval) {
		  clearInterval(slideInterval);
		}
		showSlide(index);
		slideInterval = setInterval(nextSlide, 3000);
	  });
	});
  
	// Initialize
	if (slides.length > 0) {
	  showSlide(0);
	  slideInterval = setInterval(nextSlide, 3000);
	}
  });