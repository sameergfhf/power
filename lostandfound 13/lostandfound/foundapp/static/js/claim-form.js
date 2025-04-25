document.addEventListener('DOMContentLoaded', function() {
    // Add animation to claim cards
    const claimCards = document.querySelectorAll('.col');
    claimCards.forEach((card, index) => {
      card.style.animationDelay = `${0.1 * (index + 1)}s`;
    });
    
    // Tab functionality
    const tabButtons = document.querySelectorAll('.claim-tabs .btn');
    const allCards = document.querySelectorAll('.col');
    
    tabButtons.forEach(button => {
      button.addEventListener('click', function() {
        // Remove active class from all buttons
        tabButtons.forEach(btn => {
          btn.classList.remove('active');
          btn.classList.remove('btn-primary');
          btn.classList.add('btn-dark-blue');
        });
        
        // Add active class to clicked button
        this.classList.add('active');
        this.classList.add('btn-primary');
        this.classList.remove('btn-dark-blue');
        
        // Filter cards based on selected tab
        const tabText = this.textContent.trim().toLowerCase();
        
        allCards.forEach(card => {
          // Reset animations
          card.style.animation = 'none';
          card.offsetHeight; // Trigger reflow
          card.style.animation = null;
          
          if (tabText === 'all claims' || tabText === 'all items') {
            card.style.display = 'block';
            setTimeout(() => {
              card.style.opacity = '1';
              card.style.transform = 'translateY(0)';
            }, 10);
          } else {
            const statusBadge = card.querySelector('.badge').textContent.trim().toLowerCase();
            if (statusBadge.includes(tabText.toLowerCase())) {
              card.style.display = 'block';
              setTimeout(() => {
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
              }, 10);
            } else {
              card.style.display = 'none';
            }
          }
        });
      });
    });
    
    // Enhance form inputs with animation
    const formInputs = document.querySelectorAll('input, textarea');
    formInputs.forEach(input => {
      input.addEventListener('focus', function() {
        this.parentElement.classList.add('focused');
      });
      
      input.addEventListener('blur', function() {
        this.parentElement.classList.remove('focused');
      });
    });
    
    // Form validation
    const claimForm = document.querySelector('.claim-form');
    if (claimForm) {
      claimForm.addEventListener('submit', function(e) {
        const phoneInput = document.getElementById('phone');
        const detailsInput = document.getElementById('details');
        let isValid = true;
        
        if (!phoneInput.value.trim()) {
          isValid = false;
          showError(phoneInput, 'Phone number is required');
        } else if (!isValidPhone(phoneInput.value)) {
          isValid = false;
          showError(phoneInput, 'Please enter a valid phone number');
        } else {
          removeError(phoneInput);
        }
        
        if (!detailsInput.value.trim()) {
          isValid = false;
          showError(detailsInput, 'Details are required');
        } else if (detailsInput.value.trim().length < 20) {
          isValid = false;
          showError(detailsInput, 'Please provide more detailed information (at least 20 characters)');
        } else {
          removeError(detailsInput);
        }
        
        if (!isValid) {
          e.preventDefault();
        } else {
          // Add submit animation
          const submitBtn = document.querySelector('button[type="submit"]');
          submitBtn.innerHTML = '<span class="spinner"></span> Submitting...';
          submitBtn.disabled = true;
        }
      });
    }
    
    function showError(input, message) {
      const formGroup = input.parentElement;
      let errorElement = formGroup.querySelector('.error-message');
      
      if (!errorElement) {
        errorElement = document.createElement('p');
        errorElement.className = 'error-message';
        formGroup.appendChild(errorElement);
      }
      
      errorElement.textContent = message;
      input.classList.add('error');
      
      // Shake animation
      input.style.animation = 'none';
      input.offsetHeight; // Trigger reflow
      input.style.animation = 'shake 0.5s ease';
    }
    
    function removeError(input) {
      const formGroup = input.parentElement;
      const errorElement = formGroup.querySelector('.error-message');
      
      if (errorElement) {
        formGroup.removeChild(errorElement);
      }
      
      input.classList.remove('error');
    }
    
    function isValidPhone(phone) {
      // Simple phone validation - can be improved based on requirements
      const phonePattern = /^[\d\s\-\(\)\.+]+$/;
      return phonePattern.test(phone) && phone.replace(/[^\d]/g, '').length >= 7;
    }
    
    // Add CSS for animation
    const style = document.createElement('style');
    style.textContent = `
      @keyframes shake {
        0%, 100% { transform: translateX(0); }
        10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
        20%, 40%, 60%, 80% { transform: translateX(5px); }
      }
  
      .error {
        border-color: #ef4444 !important;
      }
  
      .error-message {
        color: #ef4444;
        font-size: 0.85rem;
        margin-top: 0.25rem;
        margin-bottom: 0;
      }
  
      .form-group.focused label {
        color: var(--accent);
      }
  
      .spinner {
        display: inline-block;
        width: 1rem;
        height: 1rem;
        border: 2px solid rgba(255, 255, 255, 0.3);
        border-radius: 50%;
        border-top-color: white;
        animation: spin 0.8s linear infinite;
        margin-right: 0.5rem;
      }
  
      @keyframes spin {
        to { transform: rotate(360deg); }
      }
    `;
    document.head.appendChild(style);
  });