# Gateway DNS GuardDNS

Servidor DNS local de laboratorio. Contrasta cada dominio consultado con la lista pública de amenazas de URLhaus, bloquea las coincidencias y reenvía el resto al DNS upstream configurado. No utiliza IA ni reglas manuales.

## Requisitos

- Python 3.10 o posterior.
- `pip install -r requirements.txt`
- Apache y MySQL activos en XAMPP para guardar la bitácora.
- Conexión a Internet para descargar y actualizar la lista URLhaus.

## Ejecución

Desde la carpeta `guarddns-xampp`:

```bash
pip install -r dns-gateway/requirements.txt
python dns-gateway/dns_gateway.py
```

El gateway escucha en `127.0.0.1:5353`, utiliza `1.1.1.1:53` como upstream y actualiza la lista cada seis horas. URLhaus requiere una Auth-Key gratuita. Configura `GUARDNS_URLHAUS_AUTH_KEY` en PowerShell antes de iniciar el gateway.

Prueba con:

```bash
dig @127.0.0.1 -p 5353 google.com A
```

## Variables opcionales

- `GUARDNS_DNS_HOST`: dirección de escucha.
- `GUARDNS_DNS_PORT`: puerto DNS (predeterminado 5353).
- `GUARDDNS_UPSTREAM`: servidor upstream `IP:PUERTO`.
- `GUARDNS_FEED_URL`: URL alternativa de la fuente (opcional).
- `GUARDNS_URLHAUS_AUTH_KEY`: Auth-Key personal gratuita de URLhaus (necesaria para descargar el hostfile).
- `GUARDNS_FEED_REFRESH`: intervalo de actualización en segundos (21600).
- `GUARDNS_LOG_URL`: endpoint PHP para registrar consultas.

## Alcance

La lista URLhaus contiene dominios asociados con URLs maliciosas reportadas. No detecta por sí sola todos los sitios de phishing ni certifica como seguro un dominio que no aparezca en la lista. Si no puede descargar la fuente, conserva la última lista válida; si aún no tiene una lista, reenvía las consultas sin filtrarlas. El puerto 5353 evita modificar la configuración DNS del equipo durante las pruebas. Para usarlo en una red se necesita configuración administrativa, pruebas y controles adicionales.
