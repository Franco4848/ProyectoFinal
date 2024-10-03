var modal = document.getElementById("searchModal");

var btn = document.getElementById("searchBtn");

var span = document.getElementsByClassName("close")[0];

btn.onclick = function() {
    modal.style.display = "block";
}

span.onclick = function() {
    modal.style.display = "none";
}

window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
}

document.getElementById("searchForm").addEventListener("submit", function(event) {
    event.preventDefault();

    const tipo = document.getElementById("tipo").value;
    const pais = document.getElementById("pais").value;
    const precioMin = document.getElementById("precio_min").value;
    const precioMax = document.getElementById("precio_max").value;

    fetch(`/buscar_vinos?tipo=${tipo}&pais=${pais}&precio_min=${precioMin}&precio_max=${precioMax}`)
        .then(response => response.json())
        .then(data => {
            const resultsDiv = document.getElementById("results");
            resultsDiv.innerHTML = "";

            if (data.length === 0) {
                resultsDiv.innerHTML = "<p>No se encontraron vinos.</p>";
            } else {
                data.forEach(vino => {
                    resultsDiv.innerHTML += `
                        <div>
                            <h3>${vino.nombre}</h3>
                            <p>Tipo: ${vino.tipo}</p>
                            <p>País: ${vino.pais}</p>
                            <p>Precio: $${vino.precio}</p>
                        </div>
                    `;
                });
            }
        })
        .catch(error => console.error('Error en la búsqueda:', error));

    modal.style.display = "none";
});
