document.addEventListener('DOMContentLoaded', function() {
    // Navbar scroll effect
    const navbar = document.querySelector('.navbar');
    
    window.addEventListener('scroll', function() {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });
    
    // Mobile menu toggle
    const menuToggle = document.querySelector('.menu-toggle');
    const navLinks = document.querySelector('.nav-links');
    
    menuToggle.addEventListener('click', function() {
        navLinks.classList.toggle('active');
    });
    
    // Scroll animations
    const animatedElements = document.querySelectorAll('.animate-on-scroll');
    
    function checkScroll() {
        const triggerBottom = window.innerHeight * 0.85;
        
        animatedElements.forEach(element => {
            const elementTop = element.getBoundingClientRect().top;
            
            if (elementTop < triggerBottom) {
                // Add delay if specified
                const delay = element.getAttribute('data-delay');
                
                if (delay) {
                    setTimeout(() => {
                        element.classList.add('active');
                    }, delay);
                } else {
                    element.classList.add('active');
                }
            }
        });
    }
    
    // Check for animations on load
    checkScroll();
    
    // Check for animations on scroll
    window.addEventListener('scroll', checkScroll);
    
    // Testimonial slider
    const dots = document.querySelectorAll('.dot');
    const slides = document.querySelectorAll('.testimonial-slide');
    const slider = document.querySelector('.testimonial-slider');
    
    dots.forEach((dot, index) => {
        dot.addEventListener('click', () => {
            // Update active dot
            document.querySelector('.dot.active').classList.remove('active');
            dot.classList.add('active');
            
            // Scroll to corresponding slide
            const slideWidth = slides[0].offsetWidth;
            const slideMargin = parseInt(window.getComputedStyle(slides[0]).marginRight);
            const scrollPosition = index * (slideWidth + slideMargin);
            
            slider.scrollTo({
                left: scrollPosition,
                behavior: 'smooth'
            });
        });
    });
    
    // Update dots when scrolling testimonials
    let isScrolling;
    slider.addEventListener('scroll', () => {
        window.clearTimeout(isScrolling);
        
        isScrolling = setTimeout(() => {
            const slideWidth = slides[0].offsetWidth;
            const slideMargin = parseInt(window.getComputedStyle(slides[0]).marginRight);
            const scrollPosition = slider.scrollLeft;
            
            const activeIndex = Math.round(scrollPosition / (slideWidth + slideMargin));
            
            // Update active dot
            document.querySelector('.dot.active').classList.remove('active');
            dots[activeIndex].classList.add('active');
        }, 100);
    });
    
    // Smooth scroll for navigation links
    constnavLinks = document.querySelectorAll('a[href^="#"]');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href');
            
            if (targetId === '#') return;
            
            e.preventDefault();
            
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 100,
                    behavior: 'smooth'
                });
                
                // Close mobile menu if open
                document.querySelector('.nav-links').classList.remove('active');
            }
        });
    });
    
    // Add hover effects to feature cards
    const featureCards = document.querySelectorAll('.feature-card');
    
    featureCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-10px)';
            this.style.boxShadow = '0 15px 35px rgba(0, 0, 0, 0.3)';
            this.style.borderColor = 'rgba(100, 181, 246, 0.3)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = '';
            this.style.boxShadow = '';
            this.style.borderColor = '';
        });
    });
    
    // Add parallax effect to hero section
    const hero = document.querySelector('.hero');
    
    window.addEventListener('scroll', function() {
        const scrollPosition = window.scrollY;
        
        if (scrollPosition < window.innerHeight) {
            hero.style.backgroundPositionY = scrollPosition * 0.5 + 'px';
        }
    });
    
    // Initialize animations for elements already in view
    setTimeout(checkScroll, 100);
});