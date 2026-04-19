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

<p align="justify">
El núcleo de la propuesta reside en el análisis avanzado con la librería Pandas, que se encargará de realizar una limpieza exhaustiva de los datos y calcular métricas críticas como la probabilidad de victoria basada en medias móviles de goles. Además, se procesarán ratios de eficiencia de delanteros (goles por tiro a puerta) para ofrecer una visión profunda del estado de forma de los deportistas. El backend de Django también gestionará una base de datos de usuarios para permitir la personalización de ligas y equipos favoritos.
</p>

Listado de las funcionalidades:

- F1. Selección de liga: Permite al usuario seleccionar una liga desde un menú desplegable o buscador.
Entrada: Selección de liga por nombre o identificador.
Salida: Liga seleccionada y carga de equipos asociados.

- F2. Selección de equipos: Permite seleccionar dos equipos pertenecientes a la liga elegida, validando que no sean iguales.
Entrada: Selección de dos equipos mediante dropdown o búsqueda.
Salida: Equipos seleccionados y validados para la comparación.

- F3. Filtrado dinámico de equipos: Actualiza la lista de equipos disponibles en función de la liga seleccionada.
Entrada: Cambio en la selección de liga.
Salida: Lista de equipos filtrada según la liga.

- F4. Comparativa de métricas basadas en el rendimiento reciente: Muestra una comparación entre dos equipos basada en sus últimos 10 partidos.
Entrada: IDs de ambos equipos y datos históricos obtenidos de la API.
Salida: Métricas comparadas como goles a favor, goles en contra y puntos obtenidos.

- F5. Gráficas comparativas de equipo: Identifica patrones específicos de rendimiento como resultados de cada jornada.
Entrada: Historial de encuentros recientes y métricas.
Salida: Gráfica de resultados y de estadísticas varias.

- F6. Estimación de probabilidad de resultado: Genera una predicción basada en las estadísticas calculadas.
Entrada: Métricas agregadas de ambos equipos.
Salida: Probabilidad estimada de victoria, empate o derrota.

- F7. Consulta de detalle de equipo: Permite visualizar información detallada de uno de los equipos seleccionados.
Entrada: Selección de equipo.
Salida: Información general y estadísticas del equipo.

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

## Integrantes Grupo
- Ismael Brea Arias <ismael.brea@udc.es>
- Rubén González Ouzounis <ruben.gonzalez.ouzounis@udc.es>
- Manuel Valiña Pérez  <manuel.valina.perez@udc.es>

---

## Cómo ejecutar
### Prerrequisitos y máquina(s) de desarrollo/prueba:
- Sistema Operativo: Ubuntu 24.04 // Arch Linux // fedora // WSL // macOS
- Versión de Docker: `1:28.0.1-1`
- Cualquier otra información de relevancia

### Secuencia de comandos (docker) para descargar y lanzar la aplicación:
- `docker run --rm -it -v /var/lib/docker:/docker -v ~/volume-backup/docker/volumes:/volume-backup alpine:edge cp -r /volume-backup/data-vol /docker/volumes`
- `[...]`

---

## Problemas conocidos
- Lorem
- Ipsum

(if any)

---
