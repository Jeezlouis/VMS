document.addEventListener("DOMContentLoaded", function () {
    const registerForm = document.getElementById("register-form");
    const loginForm = document.getElementById("login-form");

    // Handle Registration
    if (registerForm) {
        registerForm.addEventListener("submit", function (e) {
            e.preventDefault();

            let name = document.getElementById("name").value.trim();
            let email = document.getElementById("email").value.trim();
            let password = document.getElementById("password").value.trim();
            let role = document.getElementById("role").value;

            if (!name || !email || !password || !role) {
                alert("All fields are required!");
                return;
            }

            let existingUser = localStorage.getItem(email);
            if (existingUser) {
                alert("User with this email already exists! Please log in.");
                return;
            }

            let user = { name, email, password, role };
            localStorage.setItem(email, JSON.stringify(user)); // Store user data

            alert("Registration successful! Redirecting...");

            // Redirect visitors to visitor registration page
            if (role === "visitor") {
                window.location.href = "{% url 'VMS:visitor_registration' %}"; // Updated redirection
            } else {
                window.location.href = "{% url 'VMS:dashboard' %}";
            }
        });
    }

    // Handle Login
    if (loginForm) {
        loginForm.addEventListener("submit", function (e) {
            e.preventDefault();

            let email = document.getElementById("email").value.trim();
            let password = document.getElementById("password").value.trim();

            let storedUser = JSON.parse(localStorage.getItem(email));

            if (storedUser && storedUser.password === password) {
                alert(`Welcome back, ${storedUser.name}! Redirecting...`);
                sessionStorage.setItem("loggedInUser", JSON.stringify(storedUser));

                // Redirect visitors to visitor page, others to dashboard
                if (storedUser.role === "visitor") {
                    window.location.href = "{% url 'VMS:visitor_registration' %}"; // Ensures visitors go to visitor page
                } else {
                    window.location.href = "{% url 'VMS:dashboard' %}";
                }
            } else {
                alert("Invalid email or password!");
            }
        });
    }
});
