document.addEventListener("DOMContentLoaded", function () {
    // Dummy data for visitors and assets
    let visitors = [
        { name: "John Doe", status: "Checked-in" },
        { name: "Jane Smith", status: "Checked-out" }
    ];

    let assets = [
        { item: "Laptop", assignedTo: "John Doe" },
        { item: "ID Badge", assignedTo: "Jane Smith" }
    ];

    // Display stats
    document.getElementById("total-visitors").innerText = visitors.length;
    document.getElementById("active-visitors").innerText = visitors.filter(v => v.status === "Checked-in").length;
    document.getElementById("total-assets").innerText = assets.length;
    document.getElementById("assigned-assets").innerText = assets.length; // Assuming all are assigned

    // Populate recent activities
    let visitorActivity = document.getElementById("visitor-activity");
    visitors.forEach(visitor => {
        let li = document.createElement("li");
        li.innerText = `${visitor.name} - ${visitor.status}`;
        visitorActivity.appendChild(li);
    });

    let assetActivity = document.getElementById("asset-activity");
    assets.forEach(asset => {
        let li = document.createElement("li");
        li.innerText = `${asset.item} assigned to ${asset.assignedTo}`;
        assetActivity.appendChild(li);
    });

    // Logout functionality
    document.getElementById("logout").addEventListener("click", function () {
        alert("Logging out...");
        window.location.href = "{% url 'VMS:login' %}";
    });
});
