#!/usr/bin/env python3
"""Gateway DNS local con lista automática de dominios reportados por URLhaus."""
from __future__ import annotations
import json, logging, os, socket, ssl, time, urllib.error, urllib.request
import certifi
from typing import Optional, Tuple
from dnslib import DNSRecord, QTYPE, RCODE, RR, A, AAAA

HOST = os.getenv('GUARDNS_DNS_HOST', '127.0.0.1')
PORT = int(os.getenv('GUARDNS_DNS_PORT', '5353'))
LOG_URL = os.getenv('GUARDNS_LOG_URL', 'http://127.0.0.1/guarddns-xampp/api/log_dns.php')
UPSTREAM = os.getenv('GUARDDNS_UPSTREAM', '1.1.1.1:53')
URLHAUS_AUTH_KEY = os.getenv('GUARDNS_URLHAUS_AUTH_KEY', '').strip()
# URLhaus now requires an Auth-Key for automated hostfile downloads.
FEED_URL_OVERRIDE = os.getenv('GUARDNS_FEED_URL', '').strip()
FEED_REFRESH = int(os.getenv('GUARDNS_FEED_REFRESH', '21600'))
HTTP_TIMEOUT = float(os.getenv('GUARDNS_HTTP_TIMEOUT', '8'))
DNS_TIMEOUT = float(os.getenv('GUARDNS_DNS_TIMEOUT', '3'))
SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
logging.basicConfig(level=os.getenv('GUARDNS_LOG_LEVEL', 'INFO'), format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger('guarddns-dns')
blocked_domains: set[str] = set()
last_feed_update = 0.0


def parse_server(value: str) -> Tuple[str, int]:
    host, sep, port = value.rpartition(':')
    return (value, 53) if not sep else (host.strip('[]'), int(port))


def refresh_feed(force: bool = False) -> None:
    global blocked_domains, last_feed_update
    if not force and time.time() - last_feed_update < FEED_REFRESH:
        return
    if FEED_URL_OVERRIDE:
        feed_url = FEED_URL_OVERRIDE
    elif URLHAUS_AUTH_KEY:
        feed_url = f'https://urlhaus-api.abuse.ch/v2/files/exports/{URLHAUS_AUTH_KEY}/hostfile.txt'
    else:
        log.error('Falta GUARDNS_URLHAUS_AUTH_KEY. URLhaus requiere una Auth-Key para descargar el hostfile; no se actualizará la lista.')
        last_feed_update = time.time()
        return
    request = urllib.request.Request(feed_url, headers={'User-Agent': 'GuardDNS-Lab/1.0'})
    try:
        with urllib.request.urlopen(request, timeout=HTTP_TIMEOUT, context=SSL_CONTEXT) as response:
            content = response.read().decode('utf-8', errors='ignore')
        fresh = set()
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split()
            if len(parts) >= 2 and parts[0] in {'127.0.0.1', '0.0.0.0'}:
                domain = parts[1].strip('.').lower()
                if '.' in domain and not domain.startswith('localhost'):
                    fresh.add(domain)
        if fresh:
            blocked_domains = fresh
            last_feed_update = time.time()
            log.info('Lista automática actualizada: %s dominios', len(blocked_domains))
        else:
            log.warning('La fuente respondió sin dominios; se conserva la última lista válida')
    except (urllib.error.URLError, TimeoutError, UnicodeError) as exc:
        log.error('No se pudo actualizar la lista automática: %s', exc)
        # Reintentar en 5 minutos tras un error, sin esperar el ciclo completo de actualización.
        last_feed_update = time.time() - max(0, FEED_REFRESH - 300)


def is_blocked(domain: str) -> bool:
    return any(domain == item or domain.endswith('.' + item) for item in blocked_domains)


def log_decision(domain: str, blocked: bool) -> None:
    payload = {'domain': domain, 'risk_score': 100 if blocked else 0,
               'classification': 'malicious' if blocked else 'trusted',
               'action': 'blocked' if blocked else 'allowed',
               'reasons': ['Coincidencia en la lista automática URLhaus.'] if blocked else ['Sin coincidencia en la lista automática URLhaus.'],
               'latency_ms': 0}
    body = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(LOG_URL, data=body, headers={'Content-Type': 'application/json'}, method='POST')
    try:
        urllib.request.urlopen(req, timeout=HTTP_TIMEOUT).close()
    except (urllib.error.URLError, TimeoutError) as exc:
        log.warning('No se pudo guardar la consulta en la bitácora: %s', exc)


def blocked_response(request: DNSRecord, qtype: str) -> bytes:
    reply = request.reply()
    reply.header.aa = 1
    if qtype == 'A':
        reply.add_answer(RR(request.q.qname, QTYPE.A, rdata=A('127.0.0.1'), ttl=30))
    elif qtype == 'AAAA':
        reply.add_answer(RR(request.q.qname, QTYPE.AAAA, rdata=AAAA('::1'), ttl=30))
    else:
        reply.header.rcode = RCODE.NXDOMAIN
    return reply.pack()


def forward(packet: bytes) -> bytes:
    upstream_host, upstream_port = parse_server(UPSTREAM)
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(DNS_TIMEOUT)
        sock.sendto(packet, (upstream_host, upstream_port))
        response, _ = sock.recvfrom(4096)
        return response


def handle(packet: bytes) -> bytes:
    refresh_feed()
    request = DNSRecord.parse(packet)
    if len(request.questions) != 1:
        return request.reply().pack()
    question = request.questions[0]
    domain = str(question.qname).rstrip('.').lower()
    qtype = QTYPE[question.qtype]
    blocked = is_blocked(domain)
    log.info('Consulta %s %s: %s', domain, qtype, 'BLOQUEADO' if blocked else 'PERMITIDO')
    log_decision(domain, blocked)
    return blocked_response(request, qtype) if blocked else forward(packet)


def main() -> None:
    refresh_feed(force=True)
    bind = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    bind.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    bind.bind((HOST, PORT))
    log.info('GuardDNS DNS escuchando en %s:%s | upstream=%s | dominios=%s', HOST, PORT, UPSTREAM, len(blocked_domains))
    while True:
        packet, address = bind.recvfrom(4096)
        try:
            bind.sendto(handle(packet), address)
        except Exception:
            log.exception('Error procesando consulta desde %s', address)

if __name__ == '__main__':
    main()
