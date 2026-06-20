#!/usr/bin/env node
/**
 * TrendRadar License Server
 * Validates license keys for hermes-trendradar Pro
 * 
 * Usage: node license-server.js
 * Runs on port 3334
 */

const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 3334;
const KEYS_FILE = path.join(__dirname, 'license-keys.json');

// In-memory store (keys also persisted to file)
let keys = {};

function loadKeys() {
  try {
    if (fs.existsSync(KEYS_FILE)) {
      keys = JSON.parse(fs.readFileSync(KEYS_FILE, 'utf8'));
    }
  } catch (e) {
    keys = {};
  }
}

function saveKeys() {
  fs.writeFileSync(KEYS_FILE, JSON.stringify(keys, null, 2));
}

// Generate a new license key
function generateKey(tier, months = 1) {
  const key = `tr-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8).toUpperCase()}`;
  const expiresAt = new Date();
  expiresAt.setMonth(expiresAt.getMonth() + months);
  
  keys[key] = { tier, expiresAt: expiresAt.toISOString(), createdAt: new Date().toISOString() };
  saveKeys();
  return { key, expiresAt: expiresAt.toISOString() };
}

// Validate a license key
function validateKey(key) {
  const entry = keys[key];
  if (!entry) return { valid: false, tier: 'free' };
  
  if (new Date(entry.expiresAt) < new Date()) {
    return { valid: false, tier: 'free', reason: 'expired' };
  }
  
  return { valid: true, tier: entry.tier, expiresAt: entry.expiresAt };
}

const server = http.createServer((req, res) => {
  // CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  
  if (req.method === 'OPTIONS') {
    res.writeHead(204);
    res.end();
    return;
  }

  const url = new URL(req.url, `http://localhost:${PORT}`);
  
  // POST /validate — validate a license key
  if (req.method === 'POST' && url.pathname === '/validate') {
    let body = '';
    req.on('data', chunk => { body += chunk; });
    req.on('end', () => {
      try {
        const { key } = JSON.parse(body);
        const result = validateKey(key);
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify(result));
      } catch (e) {
        res.writeHead(400, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ valid: false, tier: 'free', reason: 'bad request' }));
      }
    });
    return;
  }

  // GET /keys — list all keys (for admin)
  if (req.method === 'GET' && url.pathname === '/keys') {
    const all = Object.entries(keys).map(([k, v]) => ({ key: k, ...v }));
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(all));
    return;
  }

  // POST /generate — generate a new license key
  // Usage: POST /generate?tier=pro&months=1
  if (req.method === 'POST' && url.pathname === '/generate') {
    const tier = url.searchParams.get('tier') || 'pro';
    const months = parseInt(url.searchParams.get('months') || '1');
    const result = generateKey(tier, months);
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(result));
    return;
  }

  // GET /health — health check
  if (req.method === 'GET' && url.pathname === '/health') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ status: 'ok', keys: Object.keys(keys).length }));
    return;
  }

  res.writeHead(404, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({ error: 'not found' }));
});

loadKeys();

server.listen(PORT, () => {
  console.log(`✓ License server running on http://localhost:${PORT}`);
  console.log(`  POST /validate        — validate a license key`);
  console.log(`  POST /generate?tier=pro&months=1 — generate a key`);
  console.log(`  GET  /keys            — list all keys`);
  console.log(`  GET  /health          — health check`);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  server.close();
  process.exit(0);
});