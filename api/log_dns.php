<?php
declare(strict_types=1);
require __DIR__ . '/../app/bootstrap.php';
header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['ok'=>false, 'error'=>'Método no permitido.'], JSON_UNESCAPED_UNICODE);
    exit;
}
try {
    $payload = json_decode((string)file_get_contents('php://input'), true, 512, JSON_THROW_ON_ERROR);
    $domain = normalize_domain((string)($payload['domain'] ?? ''));
    if ($domain === '') throw new InvalidArgumentException('Dominio inválido.');
    $classification = (string)($payload['classification'] ?? 'trusted');
    if (!in_array($classification, ['trusted','suspicious','malicious'], true)) $classification = 'suspicious';
    $action = (string)($payload['action'] ?? 'allowed');
    if (!in_array($action, ['allowed','blocked'], true)) $action = 'allowed';
    $score = max(0, min(100, (int)($payload['risk_score'] ?? 0)));
    $latency = max(0, min(60000, (float)($payload['latency_ms'] ?? 0)));
    $reasons = $payload['reasons'] ?? [];
    if (!is_array($reasons)) $reasons = [];
    $insert = db()->prepare('INSERT INTO analyses (domain, risk_score, classification, action, reasons_json, latency_ms) VALUES (?, ?, ?, ?, ?, ?)');
    $insert->execute([$domain, $score, $classification, $action, json_encode($reasons, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES), number_format($latency, 3, '.', '')]);
    echo json_encode(['ok'=>true, 'data'=>['id'=>(int)db()->lastInsertId(), 'domain'=>$domain]], JSON_UNESCAPED_UNICODE);
} catch (InvalidArgumentException $e) {
    http_response_code(422); echo json_encode(['ok'=>false, 'error'=>$e->getMessage()], JSON_UNESCAPED_UNICODE);
} catch (JsonException $e) {
    http_response_code(400); echo json_encode(['ok'=>false, 'error'=>'JSON inválido.'], JSON_UNESCAPED_UNICODE);
} catch (Throwable $e) {
    http_response_code(500); echo json_encode(['ok'=>false, 'error'=>'No fue posible registrar la decisión.'], JSON_UNESCAPED_UNICODE);
}
