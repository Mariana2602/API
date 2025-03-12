const API_URL = "http://127.0.0.1:8000";

document.getElementById("registro-form").addEventListener("submit", async function(event) {
    event.preventDefault();

    const nombre = document.getElementById("nombre").value;
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    const response = await fetch(`${API_URL}/usuarios/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ nombre, email, password })
    });

    const data = await response.json();
    alert(data.mensaje || data.detail);
});

