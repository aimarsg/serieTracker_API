# Serie Tracker API

Este repositorio contiene el código necesario para establecer una base de datos remota utilizando un servidor de Google Cloud con Ubuntu. Se ha implementado un entorno de base de datos PostgreSQL accesible mediante una API, utilizando Docker y Docker Compose para la gestión del entorno.
Para poner en marcha el entorno, basta con ejecutar:
```
docker-compose up
````

## Despliegue

El despliegue incluye los siguientes componentes:

- **Base de datos PostgreSQL:** 

- **Adminer:** 
  - Un servicio que permite acceder y gestionar la base de datos desde una interfaz gráfica. 
  - Se puede acceder a través del puerto 80 con las credenciales.
  - [Adminer](http://35.246.246.159/)

- **API creada con FastAPI:** 
  - Una API que ofrece operaciones CRUD (create, read, update y delete) en la base de datos.
  - Se puede acceder a través del puerto 8080.
  - [Documentación de la API](http://35.246.246.159:8080/docs#/)

## Detalles de la API

La API se ha creado utilizando FastAPI, un framework de Python que permite crear de forma fácil y rápida una API. Los detalles más relevantes de la API se describen en la documentación proporcionada en el enlace mencionado anteriormente.
Los métodos de acceso a los datos de los usuarios se protegen mediante el protocolo OAuth.
