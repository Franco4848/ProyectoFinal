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