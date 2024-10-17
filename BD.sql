--TABLA PARA MURO--
CREATE DATABASE 
proyecto_final CHARACTER SET utf8mb4;
USE proyecto_final;

CREATE TABLE publi (
  id INT AUTO_INCREMENT PRIMARY KEY,
  titulo VARCHAR(255) NOT NULL,
  imagen VARCHAR(255) NOT NULL,
  descripcion VARCHAR(255)
);

CREATE TABLE comentarios (
  id INT AUTO_INCREMENT PRIMARY KEY,
  descripcion VARCHAR(255),
  publi_id INT,
  FOREIGN KEY (publi_id) REFERENCES publi(id)

);

CREATE TABLE usuario (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre_completo VARCHAR(100) NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    contraseña VARCHAR(100) NOT NULL,
    fotoPerfil VARCHAR(100) NOT NULL,
    presentacion VARCHAR(100) NOT NULL,
    enlace VARCHAR(100) NOT NULL,
    fechaNac DATE NULL,
    ubicacion VARCHAR(100) NOT NULL,
    mostrarSiNo VARCHAR(10) NOT NULL
);

ALTER TABLE publi 
ADD COLUMN id_usuario INT, 
ADD CONSTRAINT fk_usuario 
FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario);

CREATE TABLE vinos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    tipo VARCHAR(100),
    pais VARCHAR(100),
    precio DECIMAL(10, 2),
);
