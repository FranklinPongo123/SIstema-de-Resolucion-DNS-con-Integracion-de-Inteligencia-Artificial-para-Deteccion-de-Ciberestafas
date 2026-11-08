# GuardDNS — filtrado automático mediante DNS

Prototipo académico de protección DNS para laboratorio. El gateway contrasta automáticamente los dominios consultados con la lista pública de amenazas de URLhaus. Si encuentra una coincidencia, devuelve una respuesta DNS de bloqueo; si no, reenvía la consulta al resolvedor upstream.

## Componentes

- Panel web PHP para consultar estadísticas y bitácora.
- Gateway DNS en Python con `dnslib`.
- Fuente automática de dominios reportados: URLhaus.
- MySQL/MariaDB para almacenar las decisiones DNS.

No incluye inteligencia artificial, análisis manual de dominios ni administración de reglas individuales.

## Instalación en XAMPP

1. Copia `guarddns-xampp` en `C:\xampp\htdocs\guarddns-xampp`.
2. Inicia Apache y MySQL desde XAMPP.
3. Abre `http://localhost/phpmyadmin` e importa `database/schema.sql`. Si ya tenías una instalación anterior, importa también `database/migrate_dns_only.sql` para eliminar las antiguas tablas de reglas y umbrales manuales.
4. Revisa las credenciales de MySQL en `app/config.php`.
5. Abre `http://localhost/guarddns-xampp/`.

## Iniciar el gateway DNS

Instala Python 3.10+ y, desde la carpeta del proyecto, ejecuta:

```bash
pip install -r dns-gateway/requirements.txt
python dns-gateway/dns_gateway.py
```

El servicio escucha en `127.0.0.1:5353`, consulta URLhaus al iniciar y renueva la lista cada seis horas. URLhaus ahora exige una Auth-Key gratuita: define `GUARDNS_URLHAUS_AUTH_KEY` en PowerShell antes de iniciar el gateway. Las consultas se reenvían por defecto a `1.1.1.1:53` cuando no coinciden con la lista.

Prueba una consulta con `dig @127.0.0.1 -p 5353 example.com A` o una herramienta DNS equivalente.

## Panel

- **Resumen DNS:** total de consultas, dominios bloqueados y consultas permitidas.
- **Bitácora DNS:** historial de decisiones recibidas desde el gateway.
- **Estado del servicio:** fuente de datos, parámetros y limitaciones.

El panel no inicia el gateway por sí mismo. El proceso Python debe permanecer ejecutándose para que exista filtrado DNS.

## Limitaciones y seguridad

URLhaus recopila URLs maliciosas reportadas; la lista no cubre todos los dominios de phishing ni garantiza que un dominio ausente sea legítimo. Si la fuente falla, se conserva la última lista descargada; si nunca se descargó correctamente, el gateway reenvía las consultas sin bloquear. El puerto 5353 es para pruebas locales y no cambia automáticamente el DNS del sistema. No apuntes una red de producción a este prototipo sin controles, pruebas, supervisión y un procedimiento de reversión.
