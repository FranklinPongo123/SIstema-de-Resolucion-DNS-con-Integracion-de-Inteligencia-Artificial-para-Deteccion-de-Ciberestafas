# GUÍA DE INSTALACIÓN Y CONFIGURACIÓN
## GuardDNS – Sistema de filtrado DNS

**Entorno de instalación:** Windows 10/11  
**Servidor web:** Apache (XAMPP)  
**Base de datos:** MySQL  
**Servicio DNS:** Python + dnslib  
**Fuente de dominios maliciosos:** URLhaus (abuse.ch)

---

## 1. Introducción

GuardDNS es un sistema de filtrado DNS que permite identificar y bloquear solicitudes dirigidas a dominios reportados como maliciosos. Su funcionamiento se basa en la comparación automática de los dominios consultados con una lista de amenazas obtenida desde URLhaus.

El proyecto cuenta con un panel web para visualizar las consultas realizadas, las acciones del servidor DNS y los registros almacenados en la base de datos.

El sistema está compuesto por tres elementos principales:

- **Panel web:** permite visualizar las estadísticas y consultar la bitácora.
- **Servidor DNS:** recibe las consultas, comprueba los dominios y decide si permite o bloquea su resolución.
- **Base de datos:** almacena los registros generados durante las consultas.

La instalación se realiza en un entorno local utilizando XAMPP y PowerShell.

## 2. Requisitos previos

Antes de comenzar, es necesario contar con los siguientes programas:

| Recurso | Requisito |
|---|---|
| Sistema operativo | Windows 10 o 11 |
| XAMPP | Apache y MySQL |
| PHP | Versión incluida en XAMPP |
| Python | 3.10 o superior |
| PowerShell | Windows PowerShell 5.1 o superior |
| Internet | Necesario para actualizar la lista de URLhaus |
| Auth-Key | Clave de autenticación de URLhaus |

También se necesita el archivo comprimido de GuardDNS en su versión DNS Only, con las últimas correcciones del panel y la bitácora.

## 3. Instalación del proyecto

### 3.1. Extraer los archivos

Primero, se debe descargar y descomprimir el proyecto.

Copiar la carpeta `guarddns-xampp` dentro del directorio de XAMPP:

`C:\xampp\htdocs\`

La ubicación final debe ser:

`C:\xampp\htdocs\guarddns-xampp\`

La estructura general del proyecto debe contener los siguientes directorios:

- `api`
- `app`
- `assets`
- `database`
- `dns-gateway`
- `docs`

También deben encontrarse los archivos principales del panel, como `index.php` y `blocked.php`.

La carpeta `ai-service` no forma parte de esta versión, ya que el sistema funciona exclusivamente mediante el filtrado DNS.

### 3.2. Iniciar los servicios de XAMPP

Abrir XAMPP Control Panel y activar los siguientes módulos:

1. Apache.
2. MySQL.

Ambos servicios deben aparecer en ejecución.

Para comprobar que Apache funciona, ingresar en el navegador:

`http://localhost/`

Para comprobar que phpMyAdmin está disponible:

`http://localhost/phpmyadmin/`

## 4. Configuración de la base de datos

### 4.1. Importar el esquema SQL

Abrir phpMyAdmin y seleccionar la opción **Importar**.

Buscar el archivo:

`C:\xampp\htdocs\guarddns-xampp\database\schema.sql`

Seleccionar el archivo y ejecutar la importación.

El proceso creará la base de datos `guarddns_demo` y las estructuras necesarias para almacenar la información del sistema.

### 4.2. Configurar la conexión con MySQL

Abrir el archivo:

`C:\xampp\htdocs\guarddns-xampp\app\config.php`

Verificar que los parámetros de conexión correspondan a la configuración de MySQL:

```php
'db_host' => '127.0.0.1',
'db_port' => '3306',
'db_name' => 'guarddns_demo',
'db_user' => 'root',
'db_pass' => '',
```

Si MySQL utiliza una contraseña, se debe colocar en el parámetro `db_pass`.

Guardar los cambios.

**Nota:** si se está actualizando una instalación anterior, utilizar el archivo `database/migrate_dns_only.sql` según las instrucciones de migración del proyecto. No es necesario importar nuevamente el esquema ni ejecutar la migración en cada inicio.

## 5. Preparación del entorno Python

### 5.1. Comprobar la instalación de Python

Abrir PowerShell y ejecutar:

```powershell
py --version
```

El sistema debe mostrar una versión de Python igual o superior a 3.10.

Si el comando no funciona, comprobar:

```powershell
python --version
```

Si Python no está instalado, descargarlo desde:

https://www.python.org/downloads/windows/

Durante la instalación, activar la opción **Add Python to PATH**.

### 5.2. Acceder al directorio DNS

Desde PowerShell, ingresar a la carpeta del gateway:

```powershell
cd C:\xampp\htdocs\guarddns-xampp\dns-gateway
```

### 5.3. Crear el entorno virtual

Ejecutar:

```powershell
py -m venv .venv
```

Este comando crea un entorno virtual independiente para las dependencias del servidor DNS.

### 5.4. Actualizar pip

Ejecutar:

```powershell
.\.venv\Scripts\python.exe -m pip install --upgrade pip
```

### 5.5. Instalar las dependencias

Ejecutar:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Entre las dependencias se encuentra `dnslib`, utilizada para procesar las solicitudes DNS, y `certifi`, utilizada para proporcionar certificados de confianza durante las conexiones HTTPS.

Esperar hasta que finalice la instalación.

## 6. Configuración de URLhaus

### 6.1. Obtener la clave de autenticación

GuardDNS utiliza URLhaus, un servicio de abuse.ch que proporciona información sobre dominios y direcciones relacionados con la distribución de malware.

Para acceder a las listas de amenazas es necesario contar con una clave de autenticación.

Ingresar al portal:

https://auth.abuse.ch/

Crear una cuenta, verificar el correo electrónico y obtener una Auth-Key.

La clave es necesaria para que el gateway pueda descargar la lista automática.

### 6.2. Configurar la Auth-Key

En PowerShell, ejecutar:

```powershell
$env:GUARDNS_URLHAUS_AUTH_KEY = "TU_AUTH_KEY"
```

Reemplazar `TU_AUTH_KEY` por la clave obtenida en el portal.

Esta variable de entorno permite que el programa utilice la clave sin escribirla directamente en el código fuente.

La configuración se mantiene mientras permanezca abierta esa sesión de PowerShell.

### 6.3. Verificar los certificados SSL

El gateway utiliza conexiones HTTPS para descargar la lista de dominios.

Para comprobar que `certifi` está instalado correctamente, ejecutar:

```powershell
.\.venv\Scripts\python.exe -c "import certifi; print(certifi.where())"
```

Debe aparecer la ubicación del archivo de certificados `cacert.pem`.

Este mecanismo permite verificar los certificados SSL del servidor remoto y evitar conexiones HTTPS sin validación.

## 7. Ejecución del servidor DNS

Una vez completadas las configuraciones, iniciar el gateway desde PowerShell:

```powershell
cd C:\xampp\htdocs\guarddns-xampp\dns-gateway

.\.venv\Scripts\python.exe dns_gateway.py
```

Al ejecutarse, el programa realiza las siguientes actividades:

1. Establece la conexión con el servicio de URLhaus.
2. Envía la clave de autenticación.
3. Descarga la lista de dominios reportados.
4. Carga los dominios en memoria.
5. Inicia el servidor DNS local.
6. Espera las consultas de los dispositivos.

Si todo funciona correctamente, se mostrarán mensajes similares a:

```text
INFO Lista automática actualizada: XXXX dominios

INFO GuardDNS DNS escuchando en
127.0.0.1:5353

upstream=1.1.1.1:53
dominios=XXXX
```

El número de dominios puede variar según la lista descargada.

**Importante:** el valor `dominios` debe ser mayor que cero para confirmar que se ha cargado la lista de amenazas.

La ventana de PowerShell debe permanecer abierta mientras se utiliza el servidor DNS.

## 8. Funcionamiento del filtrado DNS

Cuando un dispositivo realiza una consulta, el gateway recibe el dominio y lo compara con la lista de amenazas descargada.

El proceso contempla dos situaciones:

**Caso 1. Dominio reportado como malicioso**

Si el dominio coincide con la lista de URLhaus, el gateway bloquea la resolución y devuelve la respuesta configurada para los dominios bloqueados.

**Caso 2. Dominio no incluido en la lista**

Si el dominio no coincide con ningún registro, el gateway reenvía la consulta al servidor DNS externo `1.1.1.1` para obtener su resolución.

El proceso permite realizar el filtrado sin que el administrador tenga que registrar manualmente cada dominio.

## 9. Pruebas de funcionamiento

### 9.1. Probar un dominio legítimo

Abrir una segunda ventana de PowerShell, sin cerrar la ventana donde se ejecuta el gateway.

Ingresar en el directorio:

```powershell
cd C:\xampp\htdocs\guarddns-xampp\dns-gateway
```

Ejecutar la siguiente prueba:

```powershell
@'
from dnslib import DNSRecord
import socket

domain = "example.com"

query = DNSRecord.question(domain, "A")

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(5)

sock.sendto(query.pack(), ("127.0.0.1", 5353))

response, _ = sock.recvfrom(4096)

print(DNSRecord.parse(response))

sock.close()
'@ | .\.venv\Scripts\python.exe -
```

Si el gateway funciona correctamente, se recibirá una respuesta DNS con información de resolución para `example.com`.

### 9.2. Probar un dominio bloqueado

Para comprobar el bloqueo, se debe utilizar un dominio que aparezca realmente en la lista descargada de URLhaus.

Enviar una consulta DNS a ese dominio utilizando el mismo procedimiento anterior.

Si existe coincidencia, el gateway debe devolver la respuesta configurada para los dominios bloqueados, en lugar de reenviar la consulta al servidor DNS externo.

No se deben utilizar dominios inventados como evidencia de detección automática, ya que la prueba debe demostrar una coincidencia real con la fuente de amenazas.

## 10. Acceso al panel web

Con Apache, MySQL y el gateway DNS en funcionamiento, abrir:

`http://localhost/guarddns-xampp/`

El panel permite visualizar las estadísticas generales del sistema y acceder a la bitácora DNS.

La bitácora almacena información relacionada con las consultas procesadas por el gateway.

Entre los datos registrados se encuentran:

- Fecha y hora de la consulta.
- Dominio consultado.
- Clasificación del dominio.
- Acción DNS realizada.

Los registros permiten revisar el comportamiento del filtrado y comprobar qué dominios fueron permitidos o bloqueados.

Cada fila representa una consulta DNS. Un mismo dominio puede aparecer varias veces si genera diferentes solicitudes.

## 11. Configuración de la red local

Durante las primeras pruebas, el servidor escucha en:

`127.0.0.1:5353`

Esta configuración permite realizar consultas de laboratorio desde el propio equipo, indicando expresamente la dirección y el puerto del gateway.

Para utilizar GuardDNS como servidor DNS de otros dispositivos de la red, será necesario configurar el gateway para escuchar en una interfaz de red accesible, habilitar el puerto DNS correspondiente y configurar los clientes para utilizar la dirección IP del equipo servidor.

El puerto 5353 no debe confundirse con el puerto DNS convencional 53.

No se recomienda modificar el DNS principal de Windows ni del router hasta completar las pruebas locales.

## 12. Detención del sistema

Para detener el gateway DNS, ingresar a la ventana de PowerShell donde está ejecutándose y presionar:

```text
Ctrl + C
```

Después, desde XAMPP Control Panel, detener Apache y MySQL si ya no se necesitan.

Para volver a iniciar el sistema posteriormente, basta con activar XAMPP, abrir PowerShell, configurar nuevamente la Auth-Key y ejecutar el gateway.

## 13. Solución de problemas frecuentes

### 13.1. Error HTTP 410 Gone

Este error indica que la dirección utilizada para descargar la lista ya no está disponible.

Se debe comprobar que el gateway utiliza el endpoint actualizado de URLhaus y que se está enviando la Auth-Key requerida.

### 13.2. Error CERTIFICATE_VERIFY_FAILED

Este problema aparece cuando Python no puede verificar el certificado SSL del servidor remoto.

Comprobar que `certifi` esté instalado:

```powershell
.\.venv\Scripts\python.exe -m pip install --upgrade certifi
```

Verificar nuevamente la ubicación de los certificados:

```powershell
.\.venv\Scripts\python.exe -c "import certifi; print(certifi.where())"
```

No se debe desactivar la validación SSL para solucionar este problema.

### 13.3. El gateway muestra dominios=0

Significa que no se ha cargado ningún dominio en la lista de bloqueo.

Se debe revisar la conexión a Internet, la Auth-Key, el endpoint de URLhaus y los errores de descarga mostrados en PowerShell.

### 13.4. Error de conexión con MySQL

Comprobar que MySQL esté iniciado en XAMPP y que la base `guarddns_demo` exista.

Revisar también los parámetros de conexión en `app/config.php`.

### 13.5. La bitácora no muestra todos los registros

Verificar que las consultas DNS estén llegando al gateway y que se estén almacenando correctamente en MySQL.

Si el contador muestra más registros que las filas visibles, comprobar que no existan errores PHP al generar la tabla y que el archivo `app/bootstrap.php` corresponda a la versión corregida que incluye la función `badge()`.

---

## 14. Consideraciones finales

GuardDNS utiliza un mecanismo de filtrado basado en listas externas de dominios reportados como maliciosos. Su funcionamiento depende de la disponibilidad de URLhaus, de la correcta autenticación y de la actualización de la información.

La ausencia de un dominio en la lista no garantiza que sea seguro. El sistema tampoco constituye una protección completa contra todas las modalidades de phishing, malware o fraude informático.

Para mantener el servicio operativo es necesario conservar activa la conexión a Internet durante las actualizaciones, proteger la clave de autenticación y mantener ejecutándose el gateway DNS.

**Servicios necesarios para el funcionamiento:**

| Componente | Función |
|---|---|
| Apache | Ejecutar el panel web |
| MySQL | Almacenar la bitácora |
| Python | Ejecutar el gateway DNS |
| dnslib | Procesar consultas DNS |
| certifi | Verificar certificados HTTPS |
| URLhaus | Proporcionar la lista de amenazas |
| DNS 1.1.1.1 | Resolver dominios no bloqueados |

Con estos componentes configurados, GuardDNS queda preparado para realizar pruebas de filtrado DNS y visualizar los resultados desde su panel web.