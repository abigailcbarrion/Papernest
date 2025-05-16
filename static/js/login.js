document.addEventListener('DOMContentLoaded', function () {
    const loginToggle = document.getElementById('loginToggle');
    const loginDropdown = document.getElementById('loginDropdown');

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
<<<<<<< HEAD
=======

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
>>>>>>> f5184448c81a1479e7114aec64b6b9bc69fdf47f
});