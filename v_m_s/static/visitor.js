document.addEventListener("DOMContentLoaded", function () {
    const visitorForm = document.getElementById("visitor-form");
    const visitorList = document.getElementById("visitor-list");

    let visitors = JSON.parse(localStorage.getItem("visitors")) || [];

    function updateVisitorTable() {
        visitorList.innerHTML = ""; // Clear table before updating
        visitors.forEach((visitor, index) => {
            let row = document.createElement("tr");

            row.innerHTML = `
                <td>${visitor.name}</td>
                <td>${visitor.contact}</td>
                <td>${visitor.purpose}</td>
                <td>${visitor.status}</td>
                <td>
                    <button onclick="checkIn(${index})">Check-in</button>
                    <button onclick="checkOut(${index})">Check-out</button>
                </td>
            `;
            visitorList.appendChild(row);
        });

        localStorage.setItem("visitors", JSON.stringify(visitors)); // Save updated list
    }

    // Register New Visitor
    visitorForm.addEventListener("submit", function (e) {
        e.preventDefault();

        let newVisitor = {
            name: document.getElementById("visitor-name").value,
            contact: document.getElementById("visitor-contact").value,
            purpose: document.getElementById("visitor-purpose").value,
            status: "Pending"
        };

        visitors.push(newVisitor);
        updateVisitorTable();
        visitorForm.reset();
    });

    // Check-in Visitor
    window.checkIn = function (index) {
        visitors[index].status = "Checked-in";
        updateVisitorTable();
    };

    // Check-out Visitor
    window.checkOut = function (index) {
        visitors[index].status = "Checked-out";
        updateVisitorTable();
    };

    // Initial Table Load
    updateVisitorTable();
});
