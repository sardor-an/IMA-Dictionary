document.querySelector("#registerForm").addEventListener("submit", function (event) {
    event.preventDefault(); // Prevent default form submission

    let formData = {
        first_name: document.getElementById("firstName").value,
        last_name: document.getElementById("lastName").value,
        email: document.getElementById("email").value,
        password: document.getElementById("password").value
    };

    fetch("/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === "success") {
            alert(data.message); // Show success alert (you can replace with a modal)
            window.location.href = "/login"; // Redirect to login page
        } else {
            alert(data.message); // Show error alert
        }
    })
    .catch(error => console.error("Error:", error));
});
