# Integración DNS de GuardDNS

## Arquitectura

1. El dispositivo de prueba envía una consulta DNS al gateway local.
2. El gateway comprueba el dominio contra la lista URLhaus descargada automáticamente.
3. Si existe coincidencia, responde con una dirección local de bloqueo (A/AAAA) o NXDOMAIN para otros tipos.
4. Si no existe coincidencia, reenvía la consulta al resolvedor upstream.
5. La decisión se envía a `api/log_dns.php` para almacenarla en MySQL.
6. El panel PHP presenta estadísticas y el historial.

## Instalación

- Iniciar Apache y MySQL en XAMPP.
- Importar `database/schema.sql` en phpMyAdmin.
- Verificar `app/config.php`.
- Instalar dependencias: `pip install -r dns-gateway/requirements.txt`.
- Ejecutar `python dns-gateway/dns_gateway.py`.

## Configuración predeterminada

- Escucha: `127.0.0.1:5353`.
- Upstream: `1.1.1.1:53`.
- Fuente: `https://urlhaus-api.abuse.ch/v2/files/exports/<AUTH-KEY>/hostfile.txt`.
- Actualización: cada 21600 segundos (6 horas).

Las variables `GUARDNS_DNS_HOST`, `GUARDNS_DNS_PORT`, `GUARDDNS_UPSTREAM`, `GUARDNS_FEED_URL`, `GUARDNS_FEED_REFRESH`, `GUARDNS_LOG_URL` y `GUARDNS_URLHAUS_AUTH_KEY` permiten cambiar estos valores. URLhaus requiere una Auth-Key gratuita para descargar el hostfile.

## Alcance

No existen reglas locales que el usuario deba crear. El filtrado se deriva de la lista externa. URLhaus no es una lista exhaustiva de phishing: los dominios nuevos, no reportados o retirados pueden no ser bloqueados. La disponibilidad de la fuente condiciona la actualización. En caso de error se mantiene la última lista válida; en un primer inicio sin lista, el comportamiento es permitir y reenviar.

El puerto 5353 está destinado a pruebas. El uso como DNS de una red real requiere configuración de red, permisos administrativos, redundancia, monitoreo y evaluación de falsos positivos.
