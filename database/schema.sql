CREATE DATABASE IF NOT EXISTS guarddns_demo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE guarddns_demo;

CREATE TABLE IF NOT EXISTS analyses (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  domain VARCHAR(253) NOT NULL,
  risk_score TINYINT UNSIGNED NOT NULL DEFAULT 0,
  classification ENUM('trusted','suspicious','malicious') NOT NULL,
  action ENUM('allowed','blocked') NOT NULL,
  reasons_json JSON NOT NULL,
  latency_ms DECIMAL(10,3) NOT NULL DEFAULT 0,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_analyses_created (created_at),
  INDEX idx_analyses_classification (classification),
  INDEX idx_analyses_domain_action (domain, action, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
