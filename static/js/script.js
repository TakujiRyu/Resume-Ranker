document.addEventListener('DOMContentLoaded', function() {
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });

    // Animate profession cards when they come into view
    const animateCards = () => {
        const cards = document.querySelectorAll('.profession-card');
        const windowHeight = window.innerHeight;
        
        cards.forEach((card, index) => {
            const cardPosition = card.getBoundingClientRect().top;
            const animationDelay = index * 100; // 100ms delay between each card
            
            if (cardPosition < windowHeight - 100) {
                setTimeout(() => {
                    card.classList.add('visible');
                }, animationDelay);
            }
        });
    };

    // Initial check on page load
    animateCards();

    // Check when scrolling
    window.addEventListener('scroll', animateCards);

    // Button click handlers
    // const signUpBtn = document.querySelector('.btn-signup');
    // const signInBtn = document.querySelector('.btn-signin');
    // const getStartedBtn = document.querySelector('.btn-primary');
    
    signUpBtn.addEventListener('click', function(e) {
        e.preventDefault();
        alert('Sign up form will be displayed here!');
    });
    
    signInBtn.addEventListener('click', function(e) {
        e.preventDefault();
        alert('Sign in form will be displayed here!');
    });
    
    getStartedBtn.addEventListener('click', function(e) {
        e.preventDefault();
        alert('Get started with SkillRank! This would navigate to the sign up page.');
    });

    // Card button click handlers
    const cardButtons = document.querySelectorAll('.card-btn');
    cardButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const profession = this.closest('.profession-card').querySelector('h3').textContent;
            alert(`More information about ${profession} ranking criteria would be displayed here.`);
        });
    });
});