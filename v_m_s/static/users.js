document.addEventListener("DOMContentLoaded", function () {
    const userForm = document.getElementById("user-form");
    const userList = document.getElementById("user-list");

    let users = JSON.parse(localStorage.getItem("users")) || [];

    function updateUserTable() {
        userList.innerHTML = "";

        users.forEach((user, index) => {
            let row = document.createElement("tr");

            row.innerHTML = `
                <td>${user.name}</td>
                <td>${user.email}</td>
                <td>${user.role}</td>
                <td>
                    <button onclick="removeUser(${index})">Remove</button>
                </td>
            `;

            userList.appendChild(row);
        });

        localStorage.setItem("users", JSON.stringify(users));
    }

    // Register New User
    userForm.addEventListener("submit", function (e) {
        e.preventDefault();

        let newUser = {
            name: document.getElementById("user-name").value,
            email: document.getElementById("user-email").value,
            password: document.getElementById("user-password").value,
            role: document.getElementById("user-role").value
        };

        users.push(newUser);
        updateUserTable();
        userForm.reset();
    });

    // Remove User
    window.removeUser = function (index) {
        users.splice(index, 1);
        updateUserTable();
    };

    // Initial Table Load
    updateUserTable();
});
