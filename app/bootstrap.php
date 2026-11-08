<?php
declare(strict_types=1);
date_default_timezone_set('America/La_Paz');
if (session_status() !== PHP_SESSION_ACTIVE) session_start();

function db(): PDO {
    static $pdo = null;
    if ($pdo instanceof PDO) return $pdo;
    $config = require __DIR__ . '/config.php';
    $dsn = sprintf('mysql:host=%s;port=%s;dbname=%s;charset=utf8mb4', $config['db_host'], $config['db_port'], $config['db_name']);
    $pdo = new PDO($dsn, $config['db_user'], $config['db_pass'], [
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
        PDO::ATTR_EMULATE_PREPARES => false,
    ]);
    return $pdo;
}
function h(?string $value): string { return htmlspecialchars((string)$value, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8'); }
function badge(string $classification): string {
    $badges = [
        'trusted' => ['Confiable', 'badge-trusted'],
        'suspicious' => ['Sospechoso', 'badge-suspicious'],
        'malicious' => ['Malicioso', 'badge-malicious'],
    ];
    [$label, $class] = $badges[$classification] ?? ['Sin clasificar', 'badge-suspicious'];
    return '<span class="badge ' . $class . '">' . h($label) . '</span>';
}
function normalize_domain(string $input): string {
    $input = trim($input);
    if ($input === '' || strlen($input) > 2048) return '';
    if (preg_match('~^[a-z][a-z0-9+.-]*://~i', $input)) {
        $host = parse_url($input, PHP_URL_HOST);
        if (!is_string($host)) return '';
    } else {
        $host = preg_split('~[/\?#]~', $input, 2)[0] ?? '';
        // Permite copiar el valor host:puerto, pero descarta el puerto.
        if (substr_count($host, ':') === 1 && !filter_var($host, FILTER_VALIDATE_IP, FILTER_FLAG_IPV6)) $host = explode(':', $host, 2)[0];
    }
    $host = strtolower(rtrim(trim($host, " .\t\n\r\0\x0B"), '.'));
    if ($host === '' || strlen($host) > 253 || preg_match('/[^a-z0-9.\-]/', $host)) return '';
    $labels = explode('.', $host);
    foreach ($labels as $label) {
        if ($label === '' || strlen($label) > 63 || !preg_match('/^[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$/', $label)) return '';
    }
    return $host;
}
