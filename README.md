[//]: # (TeamName: IRM Performance Tracker)
[//]: # (Member1: Ismael Brea Arias::ismael.brea@udc.es)
[//]: # (Member2: Ruben González Ouzounis::ruben.gonzalez.ouzounis@udc.es)
[//]: # (Member3: Manuel Valiña Pérez::manuel.valina.perez@udc.es)
[//]: # (Teacher: Alonso Rodríguez Iglesias)
<!-- Si quereis hacerle un logo (con IA o como prefirais) ya es lucirse y queda muy bien :) -->
<img width="300" src="https://github.com/user-attachments/assets/bdbafec2-f468-4623-9175-80f9ed86fd1c" align="right"/>

# IRM Performance
<p align="justify">
El proyecto IRM Performance Tracker consiste en el desarrollo de una aplicación web bajo el framework Django que permite analizar el rendimiento de equipos y jugadores de fútbol mediante el uso de Python en el lado del servidor. El sistema integrará datos en tiempo real consultados a APIs externas, para transformar estadísticas brutas en indicadores de valor. Toda la aplicación se desplegará utilizando contenedores de Docker y se gestionará mediante control de versiones en Git, asegurando un entorno de ejecución profesional y colaborativo.
</p>

<p align="justify"> El núcleo de la propuesta consiste en un comparador estadístico entre dos equipos de una competición, implementado mediante la librería Pandas. Esta se encarga de realizar una limpieza rigurosa de los datos y de calcular métricas clave, como la probabilidad de victoria de cada equipo a partir de sus estadísticas. Además, se presentarán tablas con los máximos goleadores, asistentes y jugadores con mayor número de infracciones (calculadas en función de tarjetas amarillas y rojas), con el objetivo de ofrecer una visión detallada del rendimiento de los deportistas. La aplicación incluirá también una sección dedicada a cada equipo de la liga seleccionada, donde se mostrará información básica, la localización de su estadio mediante un mapa y tablas con su posición en la clasificación, así como el listado de jugadores junto a sus nacionalidades. Por otro lado, se dispondrá de una pantalla de partidos para cada competición, que permitirá consultar resultados de jornadas pasadas y acceder a los horarios de los encuentros futuros de la temporada. Asimismo, se han integrado cuotas de casas de apuestas para los partidos aún no disputados. Finalmente, el backend desarrollado con Django gestionará una base de datos de usuarios que permitirá la personalización de ligas y equipos favoritos.

</p>

## Vistas

## APIs utilizadas


## Listado de las funcionalidades

### F1. Selección de liga:
Permite al usuario seleccionar una liga desde un menú anclado a la izquierda.

![alt text](imagenes/f1.png)
<img src="imagenes/f1.png" alt="Foto" width="1000" />

Una vez seleccionada la liga aparecería el comparador de equipos.

### F2. Selección de equipos:

 Permite seleccionar dos equipos pertenecientes a la liga elegida, validando que no sean iguales. La selección se puede llevar a cabo mediante un dropdown o mediante un buscador de texto que filtra en función de coincidencias de cadenas de caracteres. 

<img src="imagenes/f2.png" alt="Foto" width="1000" />


### F3. Estimación de probabilidad de resultado:

 Genera una predicción basada en las estadísticas calculadas. Calcula usando Pandas la probabilidad de victoria de un equipo respecto al otro basándose en ciertas métricas ofrecidas por la API. La fórmula de probabibilidad la calculamos de la siguiente manera:
 35% puntos liga + 25% ataque + 15% defensa + 15% forma reciente + 5% porterías a cero + 5% efectividad
 
<img src="imagenes/f3.png" alt="Foto" width="300" />

### F4. Comparativa de métricas basadas en el rendimiento reciente y muestreo mediante gráfico de barras

 Muestra una comparación entre dos equipos basada en sus datos recientes. Muestra los siguientes datos de cada equipo en la competición seleccionada:

<img src="imagenes/f4.png" alt="Foto" width="1000" />

- Posición
- Puntos
- Goles a favor
- Goles en contra
- Porterías a cero
- Partidos empatados
- Partidos perdidos

 Por otro lado, mostramos un gráfico de barras mediante **Plotly.js** que muestra la comparativa de las métricas previamente descritas, facilitando una visión clara de las diferencias entre ambos equipos.

<img src="imagenes/f4(2).png" alt="Foto" width="1000" />



### F5. Gráficas de líneas de forma reciente de los dos equipos: 

Permiten identificar patrones específicos de rendimiento de forma visual. Para ello, empleamos una gráfica de líneas mediante **Plotly.js** que representa los cinco últimos resultados de cada equipo en todas las competiciones (solo aquellas que nosotros mostramos, si juegan por ejemplo Europa League o Copa del Rey no se mostrarán): el valor superior (3 puntos) indica victoria, el intermedio empate y el inferior derrota.

<img src="imagenes/f5.png" alt="Foto" width="1000" />


### F6. Últimos resultados entre los dos equipos

Se muestran los enfrentamientos más recientes entre los dos equipos seleccionados, considerando únicamente las competiciones disponibles en la web. En caso de participar en torneos no incluidos (como Europa League o Copa del Rey), estos no se tendrán en cuenta. El número máximo de resultados mostrados es de cinco.

<img src="imagenes/f6.png" alt="Foto" width="1000" />


### F7. Consulta de información básica de un equipo:

Permite visualizar información detallada de uno de los equipos seleccionados tras seleccionar la competición a la que pertenece. Muestra información general del club como el estadio, el año de fundación, colores con los que juega, página web del club, ubicación de la sede/estadio y el nombre la plantilla de sus jugadores.

<img src="imagenes/f7.png" alt="Foto" width="1000" />
<img src="imagenes/f7(2).png" alt="Foto" width="300" />


### F8. Consulta de la ubicación exacta de la sede/estadio

Basándonos en la información básica utilizamos dos APIs para mostrar la dirección indicada en texto a través de un mapa interactivo que nos permite ver exactamente dónde se encuentra la localización de la sede/estadio del club específico.

<img src="imagenes/f8.png" alt="Foto" width="1000" />


### F9. Consulta de los últimos 10 resultados de un equipo

En la vista de Análisis Avanzado tras analizar los datos del mismo, se muestra los últimos 10 resultados del equipo seleccionado unicamente en las competiciones que mostramos en la web.

<img src="imagenes/f9.png" alt="Foto" width="1000" />


### F10. Consulta de la posición actual de la clasificación de un equipo en la competición seleccionada

En la misma vista que las dos funcionalidades anteriores, se muestra una clasificación actualizada de la competición seleccionada, incluyendo datos como puntos y goles entre otros. El equipo analizado aparece resaltado en color verde para facilitar la identificación de su posición en la tabla y sus estadísticas dentro de dicha competición.

<img src="imagenes/f10.png" alt="Foto" width="1000" />


### F11. Consulta de máximos goleadores de una competición

Tras la selección de la competición, en la vista de Rendimiento Individual mostramos los máximos goleadores de la misma.

<img src="imagenes/f11.png" alt="Foto" width="1000" />


### F12. Consulta de máximos asistentes de una competición

Tras la selección de la competición, en la vista de Rendimiento Individual mostramos los máximos asistentes de la misma.

<img src="imagenes/f12.png" alt="Foto" width="1000" />


### F13. Consulta de máximos infractores de una competición

Tras la selección de la competición, en la vista de Rendimiento Individual mostramos los máximos infractores (sumando el número de tarjetas amarillas + rojas) de la misma.

<img src="imagenes/f13.png" alt="Foto" width="1000" />

### F14. Consulta de la clasificación acual en la competición seleccionada

En la vista de Rendimiento Individual tras mostrar rankings individuales de jugadores, se muestra una clasificación de dicha competición con sus datos.

<img src="imagenes/f14.png" alt="Foto" width="1000" />


### F15. Consulta de los datos de un jugador de un equipo

En la vista de Datos Jugador, se puede obtener información de un jugador de un equipo concreto

<img src="imagenes/f15.png" alt="Foto" width="1000" />


### F16. Consulta de resultados de partidos anteriores y fechas de próximos partidos 


<img src="imagenes/f16.png" alt="Foto" width="1000" />


### F17. Consulta de cuotas deportivas para futuros partidos 



### F18. 








- F8. Consulta de últimos partidos de un equipo: Permite visualizar el historial reciente de un equipo.
Entrada: ID del equipo.
Salida: Lista de los últimos 10 partidos (ampliables) con resultados.

- F9. Consulta de estadísticas de jugadores: Permite visualizar estadísticas individuales de jugadores de un equipo.
Entrada: ID del equipo.
Salida: Lista de jugadores con estadísticas relevantes.

- F10. Ranking de jugadores por liga: Muestra rankings de jugadores dentro de una liga.
Entrada: ID de liga.
Salida: Máximos goleadores, máximos asistentes, mayor número de tarjetas rojas y mayor número de tarjetas amarillas.

- F11. Navegación entre módulos: Permite moverse entre las distintas secciones de la aplicación.
Entrada: Interacciones del usuario.
Salida: Cambio de vista manteniendo el contexto.

- F12. Persistencia de estado: Mantiene la selección de liga y equipos durante la navegación.
Entrada: Acciones del usuario.
Salida: Estado guardado durante la sesión.

- F13. Obtención de datos desde API-Football: Recupera datos de ligas, equipos, partidos y jugadores desde la API externa.
Entrada: Peticiones HTTP a la API.
Salida: Datos estructurados en formato JSON.

- F14. Procesamiento de datos: Transforma los datos obtenidos en información útil para el sistema.
Entrada: Datos en bruto de la API.
Salida: Datos procesados para visualización y análisis.

- F15. Gestión de errores: Maneja errores en peticiones o datos inconsistentes.
Entrada: Fallos en la API o datos inválidos.
Salida: Mensajes de error controlados para el usuario.

---


## Integrantes Grupos
- Ismael Brea Arias <ismael.brea@udc.es>
- Rubén González Ouzounis <ruben.gonzalez.ouzounis@udc.es>
- Manuel Valiña Pérez  <manuel.valina.perez@udc.es>

---

## Cómo ejecutar
### Prerrequisitos y máquina(s) de desarrollo/prueba:
- Sistema Operativo: Ubuntu 24.04 // Arch Linux // fedora // WSL // macOS
- Versión de Docker: 1:28.0.1-1
- Cualquier otra información de relevancia

### Secuencia de comandos (docker) para descargar y lanzar la aplicación:
*Paso 1:* Clonar este repositorio de GitHub y cambiarnos a su carpeta principal
bash 
git clone <>
cd pi2526-irm2526


*Paso 2:* Una vez dentro ejecutar el siguiente comando de docker. IMPORTANTE: copiar antes el .env a la carpeta raíz del proyecto (al nivel del Dockerfile). Una vez hecho eso ejecutar:
bash
docker build -t irm .


*Paso 3:* Finalmente, ejecutar el contenedor creado con:
bash
docker run -it -p 8000:8000 irm


*Paso 4:* Acceder a http://127.0.0.1:8000/ para visualizar la aplicación

- docker run --rm -it -v /var/lib/docker:/docker -v ~/volume-backup/docker/volumes:/volume-backup alpine:edge cp -r /volume-backup/data-vol /docker/volumes
- [...]

---



## Problemas conocidos
- Lorem
- Ipsum

(if any)

---