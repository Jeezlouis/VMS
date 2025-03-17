document.addEventListener("DOMContentLoaded", function () {
    const assetForm = document.getElementById("asset-form");
    const assignForm = document.getElementById("assign-asset-form");
    const assetSelect = document.getElementById("asset-select");
    const assetList = document.getElementById("asset-list");
    let assets = [];

    // Handle asset registration
    assetForm.addEventListener("submit", function (e) {
        e.preventDefault();

        const assetName = document.getElementById("asset-name").value.trim();
        const assetCategory = document.getElementById("asset-category").value.trim();

        if (assetName && assetCategory) {
            const asset = {
                name: assetName,
                category: assetCategory,
                status: "Available",
                assignedTo: "N/A"
            };

            assets.push(asset);
            updateAssetList();
            updateAssetDropdown();
        }
    });

    // Update dropdown with available assets
    function updateAssetDropdown() {
        assetSelect.innerHTML = "";
        assets.forEach((asset, index) => {
            if (asset.status === "Available") {
                const option = document.createElement("option");
                option.value = index;
                option.textContent = asset.name;
                assetSelect.appendChild(option);
            }
        });
    }

    // Handle asset assignment
    assignForm.addEventListener("submit", function (e) {
        e.preventDefault();

        const selectedIndex = assetSelect.value;
        const assignedTo = document.getElementById("assign-to").value.trim();

        if (selectedIndex !== "" && assignedTo) {
            assets[selectedIndex].status = "Assigned";
            assets[selectedIndex].assignedTo = assignedTo;
            updateAssetList();
            updateAssetDropdown();
            generateQRCode(assets[selectedIndex]);
        }
    });

    // Update asset list in the table
    function updateAssetList() {
        assetList.innerHTML = "";
        assets.forEach((asset, index) => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td>${asset.name}</td>
                <td>${asset.category}</td>
                <td>${asset.status}</td>
                <td>${asset.assignedTo}</td>
                <td><button onclick="returnAsset(${index})">Return</button></td>
            `;
            assetList.appendChild(row);
        });
    }

    // Return an asset
    window.returnAsset = function (index) {
        assets[index].status = "Available";
        assets[index].assignedTo = "N/A";
        updateAssetList();
        updateAssetDropdown();
        document.getElementById("qr-code-container").innerHTML = ""; // Clear QR code on return
    };

    // Generate QR Code
    function generateQRCode(asset) {
        const qrContainer = document.getElementById("qr-code-container");
        qrContainer.innerHTML = ""; // Clear previous QR codes

        const qr = new QRCode(qrContainer, {
            text: `Asset: ${asset.name}\nCategory: ${asset.category}\nAssigned To: ${asset.assignedTo}`,
            width: 150,
            height: 150
        });
    }
});