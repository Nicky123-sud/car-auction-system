// ✅ Sends API requests to Django REST API
// ✅ Stores JWT token in localStorage

$(document).ready(function () {
    $("#register-form").submit(function (event) {
        event.preventDefault();
        $.ajax({
            url: "/api/register",
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({
                username: $("#username").val(),
                email: $("#email").val(),
                password: $("#password").val(),
            }),
            success: function (response) {
                alert("Registration Successful! Please login.");
                window.location.href = "/login/";
            },
            error: function(){
                alert("Registration Failed!");
            }
        });
    });
    $("#login-form").submit(function (event) {
        event.preventDefault();
        $.ajax({
            url: "/api/login",
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({
                username: $("#username").val(),
                password: $("#password").val()
            }),
            success: function (response) {
                localStorage.setItem("token", response.access);
                alert("Login Successful!");
                window.location.href = "/vehicles/";

            },
            error: function(){
                alert("Invalid credentials!");
            }
        });
    });
});

// ✅ Fetches vehicle data from API
// ✅ Dynamically populates Bootstrap cards
// ✅ Fetches vehicle details
// ✅ Displays highest bid
// ✅ Allows users to place bids
// ✅ Shows bid history
// ✅ Auto-refreshes every 10 seconds

$(document).ready(function() {
    $.ajax({
        url: "/api/vehicles/",
        type: "GET",
        headers: { "Authorization": "Bearer " + localStorage.getItem("token") },
        success: function(response) {
            let vehicles = "";
            response.forEach(vehicle => {
                vehicles += `
                    <div class="col-md-4">
                        <div class="card">
                            <img src="${vehicle.image}" class="card-img-top" alt="Car">
                            <div class="card-body">
                                <h5 class="card-title">${vehicle.title}</h5>
                                <p class="card-text">Price: ${vehicle.price}</p>
                                <a href="/vehicle/${vehicle.id}/" class="btn btn-primary">View</a>
                            </div>
                        </div>
                    </div>
                `;
            });
            $("#vehicle-list").html(vehicles);
        }
    });
});
// 3️⃣ JavaScript for Bidding (AJAX Calls)
$(document).ready(function () {
    const vehicleId = window.location.pathname.split("/")[2];  // Extract vehicle ID from URL

    // Fetch Vehicle Details
    $.ajax({
        url: `/api/vehicles/${vehicleId}/`,
        type: "GET",
        success: function (vehicle) {
            $("#vehicle-title").text(vehicle.title);
            $("#vehicle-image").attr("src", vehicle.image);
            $("#vehicle-price").text(vehicle.price);
            $("#vehicle-description").text(vehicle.description);
        }
    });

    // Fetch Current Highest Bid
    function loadHighestBid() {
        $.ajax({
            url: `/api/highest-bid/?vehicle=${vehicleId}`,
            type: "GET",
            success: function (data) {
                $("#highest-bid").text(data.amount || "No bids yet");
            }
        });
    }

    // Load Bid History
    function loadBids() {
        $.ajax({
            url: `/api/bids/?vehicle=${vehicleId}`,
            type: "GET",
            success: function (bids) {
                $("#bid-history").empty();
                bids.forEach((bid) => {
                    $("#bid-history").append(`<li class="list-group-item">${bid.user}: Ksh ${bid.amount}</li>`);
                });
            }
        });
    }

    // Place a Bid
    $("#bid-form").submit(function (event) {
        event.preventDefault();
        const bidAmount = $("#bid-amount").val();
        $.ajax({
            url: "/api/bids/",
            type: "POST",
            contentType: "application/json",
            headers: { "Authorization": "Bearer " + localStorage.getItem("token") },
            data: JSON.stringify({ vehicle: vehicleId, amount: bidAmount }),
            success: function () {
                alert("Bid placed successfully!");
                $("#bid-amount").val(""); // Clear input
                loadHighestBid(); // Refresh highest bid
                loadBids(); // Refresh bid history
            },
            error: function () {
                alert("Error placing bid. Please try again.");
            }
        });
    });

    // Auto-refresh bid data every 10 seconds
    setInterval(() => {
        loadHighestBid();
        loadBids();
    }, 10000);

    // Initial Load
    loadHighestBid();
    loadBids();
});





