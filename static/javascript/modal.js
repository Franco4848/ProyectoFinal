// Obtén el modal y el botón que lo abre
var modal = document.getElementById("myModal");
var btn = document.getElementById("openModal");
var span = document.getElementsByClassName("close")[0];

// Cuando se hace clic en el botón, se muestra el modal
btn.onclick = function() {
  modal.style.display = "block";
}

// Cuando se hace clic en la 'x', se cierra el modal
span.onclick = function() {
  modal.style.display = "none";
}

// Si el usuario hace clic fuera del modal, también se cierra
window.onclick = function(event) {
  if (event.target == modal) {
    modal.style.display = "none";
  }
}
