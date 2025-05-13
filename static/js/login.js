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
});