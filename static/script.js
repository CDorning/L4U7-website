// script.js
// LO2 AC 2.3: This script provides client-side behaviour for form validation.

document.addEventListener('DOMContentLoaded', function() {
    // Select the registration form using a more specific attribute selector
    const registrationForm = document.querySelector('form[action="/register"]');

    // Only run the script if the registration form exists on the current page
    if (registrationForm) {
        registrationForm.addEventListener('submit', function(event) {
            
            // Get the values from the password and confirm password fields
            const passwordInput = document.getElementById('password');
            const confirmPasswordInput = document.getElementById('confirm_password');
            
            const password = passwordInput.value;
            const confirmPassword = confirmPasswordInput.value;

            // Check if the passwords are not empty and if they do not match
            if (password !== confirmPassword) {
                // If they don't match, show an alert to the user
                alert('Passwords do not match. Please try again.');
                
                // Prevent the form from being submitted to the server
                event.preventDefault(); 
            }
        });
    }
});