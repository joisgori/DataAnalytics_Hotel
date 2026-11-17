# Proyecto de de ingeniería y analítica de datos sobre hotel

El proyecto sigue una arquitectura medallion (bronze → silver → gold) y termina en tres gráficos que cuentan los hallazgos principales del negocio.

### ¿Cómo ejecutarlo?

> Se debe clonar el actual repositorio público con los comandos git clone
- Luego, ejecutar los siguientes comandos:
`cd proyecto_TCA`
`python3 -m venv .venv`
`source .venv/bin/activate`
`pip install -r requirements.txt`

> Después es necesario colocar los archivos .parquet en la carpeta `data/bronze`

El formato de los nombres de los archivos debe mantenerse fiel a como se me proporcionaron:
- iar_agencias.parquet
- iar_empresas.parquet
- iar_ocupaciones.parquet
- iar_reservaciones.parquet
- iar_segmentos_mercados.parquet

> después: 
Abrir el proyecto en VS Code (o Jupyter), selecciona el kernel de .venv y ejecuta los notebooks en orden, del 01 al 06. Los notebooks 05 y 06 regeneran por completo data/silver/ y data/gold/, así que pueden volver a ejecutarse sin dejar archivos de ejecuciones anteriores.

**Nota: tenía pensado automatizar los flujos de transformación estableciendo las funciones en módulos de python que creé en la carpeta `src`, pero por falta de tiempo la lógica crucial quedó en el notebook 05, y en el notebook 06 es que se pueden ver los resultados.**
