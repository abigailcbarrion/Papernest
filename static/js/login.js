document.addEventListener('DOMContentLoaded', function () {
    const loginToggle = document.getElementById('loginToggle');
    const loginDropdown = document.getElementById('loginDropdown');
    const loginForm = document.getElementById('loginForm');

    // Toggle dropdown visibility on click
    loginToggle.addEventListener('click', function (event) {
        event.preventDefault();
        const isVisible = loginDropdown.style.display === 'block';
        loginDropdown.style.display = isVisible ? 'none' : 'block';
    });

    // Close dropdown if clicked outside
    document.addEventListener('click', function (event) {
        if (!loginDropdown.contains(event.target) && event.target !== loginToggle) {
            loginDropdown.style.display = 'none';
        }
    });

    const toggle = document.getElementById('toggleLoginPassword');
    const pwdInput = document.querySelector('.password-wrapper input');
    if (toggle && pwdInput) {
        toggle.addEventListener('click', function (event) {
            event.stopPropagation();
            if (pwdInput.type === 'password') {
                pwdInput.type = 'text';
                toggle.innerHTML = '<i class="fas fa-eye-slash"></i>';
            } else {
                pwdInput.type = 'password';
                toggle.innerHTML = '<i class="fas fa-eye"></i>';
            }
        });
    }
});

// filepath: static/js/login.js
document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const loginModal = document.querySelector('.login-modal') || document.getElementById('loginModal');
    
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(loginForm);
            
            fetch('/login', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Accept': 'application/json'
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    // Close modal if it exists
                    if (loginModal) {
                        loginModal.style.display = 'none';
                    }
                    window.location.reload();
                } else {
                    alert(data.message || 'Login failed. Please try again.');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred. Please try again.');
            });
        });
    }
});