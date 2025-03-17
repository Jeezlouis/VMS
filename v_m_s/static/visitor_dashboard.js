document.addEventListener("DOMContentLoaded", function () {
    const visitorForm = document.getElementById("visitor-form");

    // Handle Visitor Registration
    if (visitorForm) {
        visitorForm.addEventListener("submit", function (e) {
            e.preventDefault();

            let formData = new FormData(visitorForm);

            fetch("/visitor_dashboard/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCSRFToken(),
                },
                body: formData,
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert("Visitor registration completed!");
                    window.location.reload();
                } else {
                    alert("Registration failed: " + (data.error || "Please try again."));
                }
            })
            .catch(error => {
                console.error("Error:", error);
                alert("Something went wrong. Please try again later.");
            });
        });
    }

    // Logout function
    document.getElementById("logout").addEventListener("click", function () {
        fetch("/logout/", {
            method: "POST",
            headers: {
                "X-CSRFToken": getCSRFToken(),
            }
        })
        .then(() => {
            window.location.href = "/login/";
        })
        .catch(error => console.error("Error:", error));
    });

    // Function to get CSRF token from cookies
    function getCSRFToken() {
        let cookieValue = null;
        let cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            let cookie = cookies[i].trim();
            if (cookie.startsWith("csrftoken=")) {
                cookieValue = cookie.substring("csrftoken=".length, cookie.length);
                break;
            }
        }
        return cookieValue;
    }
});
