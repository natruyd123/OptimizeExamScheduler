document.addEventListener('DOMContentLoaded', function() {
  
    var addNewUserBtn = document.getElementById('addnewuser');
    var addNewUserOverlay = document.getElementById('addNewUserOverlay');
    var addNewUserContainer = document.querySelector('.addNewUser-container');

    const passwordInput = document.getElementById('password');
    const toggleButton = document.getElementById('togglePassword');
    const toggleIcon = document.getElementById('toggleIcon');

    const passwordInput2 = document.getElementById('confirm_password');
    const toggleButton2 = document.getElementById('togglePassword2');
    const toggleIcon2 = document.getElementById('toggleIcon2');
    
    // Function to show the overlay
    function showOverlay() {
        addNewUserOverlay.style.display = 'block';
    }
    
    // Function to hide the overlay
    function hideOverlay() {
        addNewUserOverlay.style.display = 'none';
    }
    
    // Attach click event listener to the Add New User button
    addNewUserBtn.addEventListener('click', function() {
        showOverlay();
    });
    
    // Attach click event listener to the overlay
    addNewUserOverlay.addEventListener('click', function(event) {
        // Check if the click is outside the container
        if (!addNewUserContainer.contains(event.target)) {
            hideOverlay();
        }
    });

    // Toggle password visibility
    toggleButton.addEventListener('click', function () {
        const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
        passwordInput.setAttribute('type', type);
        const icon = type === 'password' ? 'eye-close.svg' : 'eye-open.svg';
        toggleIcon.setAttribute('src', `/static/images/${icon}`);
    });

    // Toggle password visibility 2
    toggleButton2.addEventListener('click', function () {
        const type = passwordInput2.getAttribute('type') === 'password' ? 'text' : 'password';
        passwordInput2.setAttribute('type', type);
        const icon = type === 'password' ? 'eye-close.svg' : 'eye-open.svg';
        toggleIcon2.setAttribute('src', `/static/images/${icon}`);
    });
});
