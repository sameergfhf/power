document.addEventListener('DOMContentLoaded', function() {
    // FAQ Data
    const faqData = [
        {
            id: 1,
            question: "How does the lost and found service work?",
            answer: "Our lost and found service connects people who have lost items with those who have found them. When you report a lost item, our system searches for matching found items. Similarly, when someone reports a found item, we look for matching lost item reports. When a potential match is identified, both parties are notified and can communicate through our secure platform.",
            category: "general"
        },
        {
            id: 2,
            question: "Is the service free to use?",
            answer: "We offer both free and premium services. Basic reporting of lost or found items is completely free. Premium features, such as priority matching, extended search radius, and dedicated support, are available with our subscription plans starting at $4.99 per month.",
            category: "general"
        },
        {
            id: 3,
            question: "How do I report a lost item?",
            answer: "To report a lost item, click on the 'Report Item' button in the navigation bar. Select 'Lost Item' from the form, then provide as much detail as possible about the item, including when and where it was lost, a description, and photos if available. The more information you provide, the better chance we have of finding a match.",
            category: "reporting"
        },
        {
            id: 4,
            question: "How do I report a found item?",
            answer: "To report a found item, click on the 'Report Item' button in the navigation bar. Select 'Found Item' from the form, then provide details about the item, including when and where it was found, a description, and photos if possible. Please do not include unique identifying information that only the owner would know, as this helps us verify legitimate claims.",
            category: "reporting"
        },
        {
            id: 5,
            question: "How are matches determined?",
            answer: "Our system uses advanced algorithms to match lost and found items based on multiple factors, including location, time, item category, description, and visual similarity (if photos are provided). Human moderators also review potential matches to ensure accuracy before notifying users.",
            category: "finding"
        },
        {
            id: 6,
            question: "What happens when a match is found?",
            answer: "When our system identifies a potential match, both the person who reported the lost item and the person who found it are notified. They can then communicate through our secure messaging system to verify details and arrange for the return of the item. We provide guidelines for safe meetups or shipping options.",
            category: "finding"
        },
        {
            id: 7,
            question: "How is my privacy protected?",
            answer: "We take privacy seriously. Your personal contact information is never shared publicly. When a match is found, our secure messaging system allows communication without revealing personal details. You choose what information to share and when. All data is encrypted and stored securely according to industry standards.",
            category: "account"
        },
        {
            id: 8,
            question: "Do I need to create an account to use the service?",
            answer: "Yes, a basic account is required to report lost or found items. This helps us maintain the quality of listings and enables our matching system to work effectively. Creating an account is free and takes just a minute with email or social login options.",
            category: "account"
        },
        {
            id: 9,
            question: "How long do listings stay active?",
            answer: "Free listings remain active for 30 days. Premium users can extend listings for up to 90 days. You can manually renew listings at any time. We recommend keeping listings active as items are sometimes found weeks after being lost.",
            category: "general"
        },
        {
            id: 10,
            question: "What areas does your service cover?",
            answer: "Our service currently covers major cities in the United States, Canada, and the United Kingdom. We're expanding to new regions regularly. Even if your specific location isn't listed, we encourage you to report items as our user base is growing and someone might find your item.",
            category: "general"
        },
        {
            id: 11,
            question: "How do I verify that someone claiming my item is the real owner?",
            answer: "When reporting a found item, you should withhold some identifying details that only the true owner would know. When someone claims the item, ask them to provide these specific details. Our system also provides verification questions to help confirm ownership.",
            category: "finding"
        },
        {
            id: 12,
            question: "Is there a reward system for returning items?",
            answer: "We don't require rewards for returning items, but many users choose to offer rewards for valuable or sentimental items. If you're offering a reward, you can mention this in your lost item report. If you're returning an item, it's up to you whether to accept any reward offered.",
            category: "finding"
        },
        {
            id: 13,
            question: "How can I delete my account?",
            answer: "To delete your account, go to Account Settings and select 'Delete Account' at the bottom of the page. You'll be asked to confirm this action. Please note that deleting your account will remove all your active listings and you won't receive notifications about potential matches.",
            category: "account"
        },
        {
            id: 14,
            question: "What should I do if I suspect fraudulent activity?",
            answer: "If you suspect someone is attempting to fraudulently claim an item or is misusing our platform in any way, please report it immediately using the 'Report' button on their message or profile. Our trust and safety team investigates all reports promptly.",
            category: "account"
        },
        {
            id: 15,
            question: "Can I report items lost or found while traveling?",
            answer: "Yes, you can report items lost or found anywhere, even while traveling. Be sure to specify the exact location and date. For international locations, provide as much detail as possible, including the name of the establishment, address, and city.",
            category: "reporting"
        }
    ];

    // DOM Elements
    const faqsContainer = document.getElementById('faqs-container');
    const searchInput = document.getElementById('faq-search');
    const categoryTabs = document.querySelectorAll('.category-tab');

    // Initialize the page
    function init() {
        // Render all FAQs
        renderFAQs(faqData);
        
        // Initialize animations
        initAnimations();
        
        // Add event listeners
        addEventListeners();
    }

    // Render FAQs to the container
    function renderFAQs(faqsToRender) {
        // Clear the container
        faqsContainer.innerHTML = '';
        
        // Check if there are FAQs to display
        if (faqsToRender.length === 0) {
            faqsContainer.innerHTML = `
                <div class="no-results animate-on-scroll fade-in">
                    <i class="fas fa-search"></i>
                    <h3>No Questions Found</h3>
                    <p>We couldn't find any FAQs matching your search. Try different keywords or browse all questions.</p>
                    <button class="btn primary-btn" id="reset-search-btn">
                        <i class="fas fa-redo"></i> Reset Search
                    </button>
                </div>
            `;
            
            // Add event listener to the reset button
            document.getElementById('reset-search-btn').addEventListener('click', () => {
                searchInput.value = '';
                renderFAQs(faqData);
                document.querySelector('.category-tab[data-category="all"]').click();
            });
            
            return;
        }
        
        // Create FAQ items
        faqsToRender.forEach(faq => {
            const faqItem = document.createElement('div');
            faqItem.className = 'faq-item animate-on-scroll fade-in';
            faqItem.setAttribute('data-category', faq.category);
            faqItem.setAttribute('data-id', faq.id);
            
            faqItem.innerHTML = `
                <div class="faq-question">
                    <span>${faq.question}</span>
                    <i class="fas fa-chevron-down"></i>
                </div>
                <div class="faq-answer">
                    <div class="faq-answer-content">
                        ${faq.answer}
                    </div>
                </div>
            `;
            
            faqsContainer.appendChild(faqItem);
            
            // Add event listener to toggle answer
            const question = faqItem.querySelector('.faq-question');
            question.addEventListener('click', () => {
                toggleFAQ(faqItem);
            });
        });
        
        // Initialize animations for the newly added FAQs
        initAnimations();
    }

    // Toggle FAQ open/closed
    function toggleFAQ(faqItem) {
        // Close all other FAQs
        const allFAQs = document.querySelectorAll('.faq-item');
        allFAQs.forEach(item => {
            if (item !== faqItem && item.classList.contains('active')) {
                item.classList.remove('active');
            }
        });
        
        // Toggle the clicked FAQ
        faqItem.classList.toggle('active');
    }

    // Add event listeners
    function addEventListeners() {
        // Search input
        searchInput.addEventListener('input', handleSearch);
        
        // Category tabs
        categoryTabs.forEach(tab => {
            tab.addEventListener('click', () => {
                // Remove active class from all tabs
                categoryTabs.forEach(t => t.classList.remove('active'));
                
                // Add active class to clicked tab
                tab.classList.add('active');
                
                // Filter FAQs by category
                const category = tab.getAttribute('data-category');
                filterFAQs(category);
            });
        });
        
        // Navbar scroll effect
        window.addEventListener('scroll', () => {
            const navbar = document.querySelector('.navbar');
            if (window.scrollY > 50) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        });
        
        // Mobile menu toggle
        const menuToggle = document.querySelector('.menu-toggle');
        const navLinks = document.querySelector('.nav-links');
        
        menuToggle.addEventListener('click', () => {
            navLinks.classList.toggle('active');
        });
    }

    // Handle search
    function handleSearch() {
        const searchTerm = searchInput.value.toLowerCase();
        const activeCategory = document.querySelector('.category-tab.active').getAttribute('data-category');
        
        // Filter FAQs based on search term and active category
        let filteredFAQs;
        
        if (searchTerm === '') {
            // If search is empty, just filter by category
            if (activeCategory === 'all') {
                filteredFAQs = faqData;
            } else {
                filteredFAQs = faqData.filter(faq => faq.category === activeCategory);
            }
        } else {
            // Filter by search term and category
            filteredFAQs = faqData.filter(faq => {
                const matchesSearch = 
                    faq.question.toLowerCase().includes(searchTerm) ||
                    faq.answer.toLowerCase().includes(searchTerm);
                
                if (activeCategory === 'all') {
                    return matchesSearch;
                } else {
                    return matchesSearch && faq.category === activeCategory;
                }
            });
        }
        
        // Render filtered FAQs
        renderFAQs(filteredFAQs);
        
        // Highlight search terms in the rendered FAQs
        if (searchTerm !== '') {
            highlightSearchTerms(searchTerm);
        }
    }

    // Filter FAQs by category
    function filterFAQs(category) {
        const searchTerm = searchInput.value.toLowerCase();
        
        let filteredFAQs;
        
        if (category === 'all') {
            if (searchTerm === '') {
                filteredFAQs = faqData;
            } else {
                filteredFAQs = faqData.filter(faq => 
                    faq.question.toLowerCase().includes(searchTerm) ||
                    faq.answer.toLowerCase().includes(searchTerm)
                );
            }
        } else {
            if (searchTerm === '') {
                filteredFAQs = faqData.filter(faq => faq.category === category);
            } else {
                filteredFAQs = faqData.filter(faq => 
                    faq.category === category && (
                        faq.question.toLowerCase().includes(searchTerm) ||
                        faq.answer.toLowerCase().includes(searchTerm)
                    )
                );
            }
        }
        
        // Render filtered FAQs
        renderFAQs(filteredFAQs);
        
        // Highlight search terms if there's a search
        if (searchTerm !== '') {
            highlightSearchTerms(searchTerm);
        }
    }

    // Highlight search terms in the rendered FAQs
    function highlightSearchTerms(searchTerm) {
        const faqItems = document.querySelectorAll('.faq-item');
        
        faqItems.forEach(item => {
            const question = item.querySelector('.faq-question span');
            const answer = item.querySelector('.faq-answer-content');
            
            // Highlight in question
            question.innerHTML = highlightText(question.textContent, searchTerm);
            
            // Highlight in answer
            answer.innerHTML = highlightText(answer.textContent, searchTerm);
            
            // Add highlight class to the item
            if (
                question.textContent.toLowerCase().includes(searchTerm) ||
                answer.textContent.toLowerCase().includes(searchTerm)
            ) {
                item.classList.add('highlight');
            }
        });
    }

    // Helper function to highlight text
    function highlightText(text, term) {
        const regex = new RegExp(`(${escapeRegExp(term)})`, 'gi');
        return text.replace(regex, '<span style="background-color: rgba(30, 136, 229, 0.2); color: var(--primary-color); padding: 0 2px; border-radius: 3px;">$1</span>');
    }

    // Helper function to escape special characters in regex
    function escapeRegExp(string) {
        return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }

    // Initialize animations
    function initAnimations() {
        const animatedElements = document.querySelectorAll('.animate-on-scroll');
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('active');
                }
            });
        }, { threshold: 0.1 });
        
        animatedElements.forEach(element => {
            observer.observe(element);
        });
    }

    // Initialize the page
    init();
});