const defaultFile= 'static/img/fotoPerfil.jpg'
const file = document.getElementById('fotoPerfil');
const img = document.getElementById('imgPreview');
const eliminar_foto = document.getElementById('eliminar_foto')
const img_actual= img.src
file.addEventListener('change', e => {
    if (e.target.files[0]){
        const reader = new FileReader();
        reader.onload = function(e){
            img.src= e.target.result;
        }
        reader.readAsDataURL(e.target.files[0])
    }else{
        img.src= img_actual
    }
});
eliminar_foto.addEventListener('change', e => {
    img.src = defaultFile;
});