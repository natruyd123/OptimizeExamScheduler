document.addEventListener('DOMContentLoaded', function() {
    // Get the Add New User button
    var addNewUserBtn = document.getElementById('addnewuser');
    
    // Get the Add New User overlay
    var addNewUserOverlay = document.getElementById('addNewUserOverlay');
    
    // Get the Add New User container
    var addNewUserContainer = document.querySelector('.addNewUser-container');
    
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
});
