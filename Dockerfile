 
# MUY IMPORTANTE: Aquí ajustar a la versión de python que estemos utilizando en nuestro equipo
FROM python:3.13.12

# Creamos el usuario no root que ejecutará la aplicación.
RUN useradd --shell /bin/bash app


# Este será el directorio de trabajo dentro del contenedor
WORKDIR /opt/app

# Copiamos el fichero requirements.
COPY requirements.txt /opt/app/
# Y se instalan las dependencias. Lo instalamos como root y sin entorno virtual ya que al estar dentro de Docker, no nos preocupan conflictos con otros paquetes y así estarán disponibles para todos los usuarios.
RUN pip install --no-cache-dir -r requirements.txt


# OPCIONAL: En caso de ser necesario, se crea el usuario y contraseña de administrador. En la mayoría de casos no es necesario.
ENV DJANGO_SUPERUSER_USERNAME=admin
ENV DJANGO_SUPERUSER_EMAIL=admin@example.com
ENV DJANGO_SUPERUSER_PASSWORD=admin

# Copia de la carpeta del proyecto 'my_proyect'
COPY djangoproject /opt/app/djangoproject
COPY .env /opt/app/
# OPCIONAL: Compilamos las librerías en caso de que empleemos librerías C u en otro lenguaje
#RUN gcc -O2 -march=native -fPIC -shared /opt/app/djangoproject/mylib/libmylib.c -o /opt/app/djangoproject/mylib/libmylib.so
# Y damos permisos al usuario 'app' sobre la carpeta donde se ejecutará el fichero recursivamente.
RUN chown -R app:app /opt/app

# Ahora nos dentro de la carpeta del proyecto. Por ejemplo:
WORKDIR /opt/app/djangoproject

# Exponemos el puerto que queramos. En nuestro caso el 8000.
EXPOSE 8000

# Y hacemos su sobre el usuario 'app'.
USER app

# Arrancamos el servidor en todas las interfaces, previa creación de las migraciones si las tenemos en el gitignore, y creación de administrador si es necesario.
# Es necesario ejecutarlo con 'sh -c' ya que la llamada por defecto de Docker no permite ejecutar varios comandos con &&. De aquí se deben eliminar los
# comandos que no vayamos a usar.
CMD ["sh", "-c", "python manage.py makemigrations && python manage.py migrate && python manage.py createsuperuser --noinput && python manage.py && python manage.py runserver 0.0.0.0:8000"]