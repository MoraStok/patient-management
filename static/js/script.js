document.addEventListener('DOMContentLoaded', function () {
    const logoutLink = document.getElementById("logout-link");
    
    if (logoutLink) {
        logoutLink.addEventListener("click", function (e) {
            e.preventDefault();  // Prevent the default link behavior
            
            // Create a form to submit POST request for logout
            const logoutForm = document.createElement("form");
            logoutForm.method = "POST";
            logoutForm.action = "/auth/logout/";  // The URL for logout

            // Retrieve the CSRF token from the meta tag
            const csrfToken = document.createElement("input");
            csrfToken.type = "hidden";
            csrfToken.name = "csrfmiddlewaretoken";
            csrfToken.value = document.querySelector('[name="csrf-token"]').content; // This line fetches the CSRF token

            logoutForm.appendChild(csrfToken);
            document.body.appendChild(logoutForm);  // Append the form to the body
            logoutForm.submit();  // Submit the form
        });
    }
});