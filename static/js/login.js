document.addEventListener('DOMContentLoaded', function () {
    // Password toggle functionality only
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
