import os
import json
import re

import requests
from flask import Flask, make_response, request, jsonify
from dotenv import load_dotenv

# Load environment variables from .env (local dev) or system env (production)
load_dotenv()

app = Flask(__name__)

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Vision-capable models tried in order of preference.
# DeepSeek V3 is text-only and cannot process images.
VISION_MODELS = [
    "google/gemini-2.0-flash-001",
    "google/gemini-flash-1.5",
    "meta-llama/llama-4-maverick",
]



# HTML served inline — no templates/ folder needed on Railway
INDEX_HTML = '''<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>NutriScan AI — Food Intelligence</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Playfair+Display:ital,wght@0,400..900;1,400..900&display=swap" rel="stylesheet">
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<style>
:root{--bg-deep:#080d14;--bg-mid:#0e1623;--bg-card:#111c2e;--bg-glass:rgba(255,255,255,0.04);--border:rgba(255,255,255,0.07);--border-active:rgba(59,130,246,0.4);--accent:#3b82f6;--accent-hover:#2563eb;--accent-glow:rgba(59,130,246,0.2);--teal:#2dd4bf;--lime:#a3e635;--rose:#fb7185;--amber:#fbbf24;--purple:#a78bfa;--orange:#fb923c;--text:#e2e8f0;--text-muted:#64748b;--text-dim:#94a3b8;--shadow-card:0 8px 32px rgba(0,0,0,0.4),0 1px 0 rgba(255,255,255,0.05) inset;--shadow-btn:0 4px 20px rgba(59,130,246,0.35);--radius-lg:20px;--radius-md:14px;--radius-sm:10px;--blur:blur(16px);--transition:all 0.3s cubic-bezier(0.4,0,0.2,1)}
[data-theme="light"]{--bg-deep:#f0f4ff;--bg-mid:#ffffff;--bg-card:#f8faff;--bg-glass:rgba(255,255,255,0.7);--border:rgba(0,0,0,0.08);--border-active:rgba(59,130,246,0.5);--text:#0f172a;--text-muted:#94a3b8;--text-dim:#64748b;--shadow-card:0 8px 32px rgba(59,130,246,0.1),0 1px 0 rgba(255,255,255,0.8) inset}
*,*::before,*::after{margin:0;padding:0;box-sizing:border-box}
html{scroll-behavior:smooth}
body{background:var(--bg-deep);color:var(--text);font-family:'Playfair Display',serif;font-size:15px;line-height:1.6;min-height:100vh;overflow-x:hidden}
.bg-orbs{position:fixed;inset:0;z-index:0;pointer-events:none;overflow:hidden}
.orb{position:absolute;border-radius:50%;filter:blur(80px);opacity:.12;animation:drift 20s ease-in-out infinite}
.orb-1{width:600px;height:600px;background:radial-gradient(circle,#3b82f6,transparent);top:-200px;left:-100px;animation-delay:0s}
.orb-2{width:400px;height:400px;background:radial-gradient(circle,#2dd4bf,transparent);bottom:10%;right:-100px;animation-delay:-7s;opacity:.08}
.orb-3{width:300px;height:300px;background:radial-gradient(circle,#a78bfa,transparent);top:40%;left:30%;animation-delay:-14s;opacity:.07}
@keyframes drift{0%,100%{transform:translate(0,0) scale(1)}33%{transform:translate(30px,-40px) scale(1.05)}66%{transform:translate(-20px,30px) scale(0.95)}}
.bg-grid{position:fixed;inset:0;z-index:0;pointer-events:none;background-image:linear-gradient(rgba(59,130,246,0.03) 1px,transparent 1px),linear-gradient(90deg,rgba(59,130,246,0.03) 1px,transparent 1px);background-size:60px 60px}
.container{max-width:860px;margin:0 auto;padding:40px 20px 80px;position:relative;z-index:1}
header{text-align:center;margin-bottom:52px;animation:fadeDown .7s ease both}
.header-top{display:flex;align-items:center;justify-content:center;gap:12px;margin-bottom:28px}
.theme-toggle{position:absolute;right:20px;top:40px;width:42px;height:42px;border-radius:50%;border:1px solid var(--border);background:var(--bg-glass);backdrop-filter:var(--blur);color:var(--text-dim);cursor:pointer;display:flex;align-items:center;justify-content:center;font-size:18px;transition:var(--transition);z-index:10}
.theme-toggle:hover{border-color:var(--border-active);color:var(--accent);transform:rotate(20deg)}
.badge{display:inline-flex;align-items:center;gap:6px;background:var(--bg-glass);border:1px solid var(--border-active);backdrop-filter:var(--blur);border-radius:100px;padding:5px 14px;font-size:11px;font-weight:600;color:var(--accent);letter-spacing:.06em;text-transform:uppercase}
.badge-dot{width:6px;height:6px;border-radius:50%;background:var(--teal);animation:pulse-dot 2s infinite}
@keyframes pulse-dot{0%,100%{opacity:1;box-shadow:0 0 0 0 rgba(45,212,191,0.5)}50%{opacity:.7;box-shadow:0 0 0 6px rgba(45,212,191,0)}}
h1{font-family:'Bebas Neue',sans-serif;font-size:clamp(48px,9vw,88px);font-weight:400;letter-spacing:.08em;line-height:1;margin-bottom:14px;background:linear-gradient(135deg,#e2e8f0 0%,#3b82f6 50%,#2dd4bf 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.subtitle{font-size:15px;color:var(--text-muted);font-weight:400;max-width:380px;margin:0 auto;line-height:1.7}
.card{background:var(--bg-glass);backdrop-filter:var(--blur);-webkit-backdrop-filter:var(--blur);border:1px solid var(--border);border-radius:var(--radius-lg);padding:32px;box-shadow:var(--shadow-card);transition:var(--transition);margin-bottom:20px;animation:fadeUp .5s ease both}
.card:hover{border-color:rgba(255,255,255,0.1);box-shadow:0 12px 48px rgba(0,0,0,0.5),0 1px 0 rgba(255,255,255,0.07) inset}
.section-label{font-size:10px;font-weight:700;color:var(--accent);letter-spacing:.16em;text-transform:uppercase;margin-bottom:20px;display:flex;align-items:center;gap:8px}
.section-label::after{content:'';flex:1;height:1px;background:var(--border)}
.drop-zone{border:2px dashed rgba(59,130,246,0.25);border-radius:var(--radius-md);background:rgba(59,130,246,0.03);position:relative;height:300px;display:flex;align-items:center;justify-content:center;cursor:pointer;overflow:hidden;transition:var(--transition);margin-bottom:20px}
.drop-zone:hover,.drop-zone.dragover{border-color:var(--accent);background:rgba(59,130,246,0.06);box-shadow:0 0 0 4px var(--accent-glow)}
.drop-zone.has-image{border-style:solid;border-color:rgba(45,212,191,0.4);background:rgba(0,0,0,0.6)}
#preview{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);max-width:calc(100% - 24px);max-height:calc(100% - 24px);width:auto;height:auto;object-fit:contain;display:none;border-radius:8px}
#preview.visible{display:block}
#videoEl{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;display:none;border-radius:calc(var(--radius-md) - 2px)}
#videoEl.visible{display:block}
.upload-placeholder{display:flex;flex-direction:column;align-items:center;gap:14px;color:var(--text-muted);text-align:center;transition:opacity .3s;padding:20px}
.upload-icon{width:64px;height:64px;border-radius:18px;background:linear-gradient(135deg,rgba(59,130,246,0.15),rgba(45,212,191,0.1));border:1px solid rgba(59,130,246,0.2);display:flex;align-items:center;justify-content:center;font-size:26px;transition:var(--transition)}
.drop-zone:hover .upload-icon{transform:translateY(-3px);box-shadow:0 8px 24px rgba(59,130,246,0.2)}
.upload-placeholder h3{font-size:15px;font-weight:600;color:var(--text-dim)}
.upload-placeholder p{font-size:12px;color:var(--text-muted);line-height:1.5}
.btn-row{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:24px}
.btn{flex:1;min-width:110px;padding:12px 18px;border-radius:var(--radius-sm);border:1px solid var(--border);background:var(--bg-glass);backdrop-filter:var(--blur);color:var(--text-dim);font-family:'Playfair Display',serif;font-size:13px;font-weight:600;cursor:pointer;transition:var(--transition);display:flex;align-items:center;justify-content:center;gap:7px;position:relative;overflow:hidden}
.btn::after{content:'';position:absolute;top:0;left:-100%;width:60%;height:100%;background:linear-gradient(90deg,transparent,rgba(255,255,255,0.06),transparent);transition:left .4s ease}
.btn:hover::after{left:150%}
.btn:hover{border-color:var(--border-active);background:rgba(59,130,246,0.08);color:var(--text);transform:translateY(-1px)}
.btn:active{transform:translateY(0)}
.btn-primary{background:linear-gradient(135deg,#3b82f6,#2563eb);border-color:#3b82f6;color:#fff;font-weight:700;box-shadow:var(--shadow-btn)}
.btn-primary:hover{background:linear-gradient(135deg,#2563eb,#1d4ed8);border-color:#2563eb;color:#fff;box-shadow:0 6px 30px rgba(59,130,246,0.5);transform:translateY(-2px)}
.btn-primary:disabled{opacity:.35;cursor:not-allowed;transform:none;box-shadow:none}
.btn svg{width:15px;height:15px;flex-shrink:0}
.weight-row{display:grid;grid-template-columns:1fr auto;gap:12px;margin-bottom:20px;align-items:end}
.input-wrap label{display:block;font-size:11px;font-weight:600;color:var(--text-muted);letter-spacing:.1em;text-transform:uppercase;margin-bottom:8px}
input[type="number"]{width:100%;padding:12px 16px;background:rgba(255,255,255,0.04);border:1px solid var(--border);border-radius:var(--radius-sm);color:var(--text);font-family:'Playfair Display',serif;font-size:16px;font-weight:500;outline:none;transition:var(--transition);-moz-appearance:textfield}
input[type="number"]::-webkit-outer-spin-button,input[type="number"]::-webkit-inner-spin-button{-webkit-appearance:none}
input[type="number"]:focus{border-color:var(--accent);box-shadow:0 0 0 3px var(--accent-glow);background:rgba(59,130,246,0.04)}
.unit-toggle{display:flex;border:1px solid var(--border);border-radius:var(--radius-sm);overflow:hidden;background:rgba(255,255,255,0.02);height:46px}
.unit-btn{padding:0 20px;background:transparent;border:none;color:var(--text-muted);font-family:'Playfair Display',serif;font-size:13px;font-weight:700;cursor:pointer;transition:var(--transition)}
.unit-btn.active{background:linear-gradient(135deg,rgba(59,130,246,0.2),rgba(45,212,191,0.15));color:var(--accent)}
.loading-overlay{position:fixed;inset:0;background:rgba(8,13,20,0.85);backdrop-filter:blur(20px);z-index:1000;display:none;align-items:center;justify-content:center;flex-direction:column;gap:28px}
.loading-overlay.active{display:flex}
.spinner{width:56px;height:56px;position:relative}
.spinner::before,.spinner::after{content:'';position:absolute;inset:0;border-radius:50%;border:2px solid transparent}
.spinner::before{border-top-color:var(--accent);border-right-color:var(--accent);animation:spin .9s linear infinite}
.spinner::after{border-bottom-color:var(--teal);border-left-color:var(--teal);animation:spin .9s linear infinite reverse;inset:8px}
@keyframes spin{to{transform:rotate(360deg)}}
.loading-title{font-family:'Bebas Neue',sans-serif;font-size:22px;font-weight:400;letter-spacing:.1em;color:var(--text)}
.loading-sub{font-size:13px;color:var(--text-muted);animation:blink 1.8s infinite}
@keyframes blink{0%,100%{opacity:1}50%{opacity:.4}}
.msg{display:none;border-radius:var(--radius-md);padding:14px 18px;font-size:13px;font-weight:500;margin-bottom:20px;animation:slideIn .3s ease both;line-height:1.5}
.msg.visible{display:flex;align-items:flex-start;gap:10px}
.msg-error{background:rgba(251,113,133,0.08);border:1px solid rgba(251,113,133,0.25);color:#fca5a5}
.msg-success{background:rgba(163,230,53,0.07);border:1px solid rgba(163,230,53,0.2);color:#bef264}
.msg-icon{font-size:16px;flex-shrink:0;margin-top:1px}
@keyframes slideIn{from{opacity:0;transform:translateY(-8px)}to{opacity:1;transform:translateY(0)}}
#results{display:none}
#results.visible{display:block;animation:fadeUp .6s ease both}
.food-identity{display:flex;align-items:flex-start;justify-content:space-between;gap:20px;margin-bottom:28px;flex-wrap:wrap}
.food-name{font-family:'Bebas Neue',sans-serif;font-size:32px;font-weight:400;letter-spacing:.06em;line-height:1.1;margin-bottom:6px}
.food-desc{font-size:13px;color:var(--text-muted);max-width:420px;line-height:1.6}
.confidence-pill{background:linear-gradient(135deg,rgba(45,212,191,0.12),rgba(163,230,53,0.08));border:1px solid rgba(45,212,191,0.25);border-radius:12px;padding:10px 18px;text-align:center;flex-shrink:0}
.confidence-num{font-family:'Bebas Neue',sans-serif;font-size:30px;font-weight:400;color:var(--teal);line-height:1}
.confidence-label{font-size:10px;font-weight:600;color:var(--text-muted);letter-spacing:.1em;text-transform:uppercase;margin-top:3px}
.calories-hero{background:linear-gradient(135deg,rgba(59,130,246,0.1) 0%,rgba(45,212,191,0.06) 100%);border:1px solid rgba(59,130,246,0.2);border-radius:var(--radius-md);padding:28px;display:flex;align-items:center;justify-content:space-between;gap:20px;margin-bottom:20px;flex-wrap:wrap;position:relative;overflow:hidden}
.calories-hero::before{content:'';position:absolute;left:-40px;top:-40px;width:200px;height:200px;background:radial-gradient(circle,rgba(59,130,246,0.15),transparent);pointer-events:none}
.calories-num{font-family:'Bebas Neue',sans-serif;font-size:72px;font-weight:400;line-height:1;letter-spacing:.04em;background:linear-gradient(135deg,#fff,var(--accent));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.calories-meta{font-size:11px;font-weight:600;color:var(--text-muted);letter-spacing:.12em;text-transform:uppercase;margin-top:6px}
.health-ring-wrap{position:relative;width:90px;height:90px;flex-shrink:0}
.health-ring-wrap svg{transform:rotate(-90deg)}
.health-ring-inner{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center}
.health-score-num{font-family:'Bebas Neue',sans-serif;font-size:22px;font-weight:400;color:var(--lime);line-height:1}
.health-score-label{font-size:9px;font-weight:600;color:var(--text-muted);text-transform:uppercase;letter-spacing:.1em}
.macros-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:12px;margin-bottom:20px}
@media(min-width:600px){.macros-grid{grid-template-columns:repeat(4,1fr)}}
.macro-tile{background:var(--bg-glass);border:1px solid var(--border);border-radius:var(--radius-md);padding:18px;cursor:default;transition:var(--transition);position:relative;overflow:hidden}
.macro-tile::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:var(--tile-color,var(--accent));border-radius:2px 2px 0 0}
.macro-tile:hover{border-color:rgba(255,255,255,0.12);transform:translateY(-2px);box-shadow:0 8px 24px rgba(0,0,0,0.3)}
.macro-icon{font-size:20px;margin-bottom:10px}
.macro-val{font-family:'Bebas Neue',sans-serif;font-size:28px;font-weight:400;line-height:1;margin-bottom:4px;color:var(--tile-color,var(--text))}
.macro-unit{font-size:13px;font-weight:400;color:var(--text-muted)}
.macro-name{font-size:11px;font-weight:600;color:var(--text-muted);letter-spacing:.08em;text-transform:uppercase;font-family:'Playfair Display',serif}
.charts-row{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:20px}
@media(max-width:600px){.charts-row{grid-template-columns:1fr}}
.chart-card{background:var(--bg-glass);border:1px solid var(--border);border-radius:var(--radius-md);padding:20px;transition:var(--transition)}
.chart-card:hover{border-color:rgba(255,255,255,0.1)}
.chart-title{font-size:11px;font-weight:700;color:var(--text-muted);letter-spacing:.12em;text-transform:uppercase;margin-bottom:16px}
.stats-row{display:grid;grid-template-columns:repeat(2,1fr);gap:12px;margin-bottom:20px}
@media(min-width:480px){.stats-row{grid-template-columns:repeat(4,1fr)}}
.stat-tile{background:var(--bg-glass);border:1px solid var(--border);border-radius:var(--radius-sm);padding:16px;text-align:center}
.stat-num{font-family:'Bebas Neue',sans-serif;font-size:22px;font-weight:400;color:var(--text);margin-bottom:4px}
.stat-label{font-size:10px;font-weight:600;color:var(--text-muted);letter-spacing:.1em;text-transform:uppercase}
.micro-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:10px;margin-bottom:20px}
@media(min-width:600px){.micro-grid{grid-template-columns:repeat(3,1fr)}}
.micro-tile{background:var(--bg-glass);border:1px solid var(--border);border-radius:var(--radius-sm);padding:14px 16px;display:flex;align-items:center;justify-content:space-between;transition:var(--transition)}
.micro-tile:hover{border-color:rgba(167,139,250,0.2);background:rgba(167,139,250,0.04)}
.micro-name{font-size:11px;font-weight:600;color:var(--text-muted);letter-spacing:.06em;text-transform:uppercase}
.micro-val{font-size:13px;font-weight:700;color:var(--purple)}
.tags-wrap{display:flex;flex-wrap:wrap;gap:8px}
.tag{padding:5px 14px;border-radius:100px;background:rgba(255,255,255,0.04);border:1px solid var(--border);font-size:11px;font-weight:600;color:var(--text-muted);letter-spacing:.07em;text-transform:uppercase;transition:var(--transition)}
.tag:hover{background:var(--accent-glow);border-color:var(--border-active);color:var(--accent)}
#fileInput{display:none}
#captureBtn{display:none}
.footer{text-align:center;margin-top:60px;font-size:11px;color:var(--text-muted);letter-spacing:.06em;opacity:.5}
@keyframes fadeDown{from{opacity:0;transform:translateY(-24px)}to{opacity:1;transform:translateY(0)}}
@keyframes fadeUp{from{opacity:0;transform:translateY(24px)}to{opacity:1;transform:translateY(0)}}
::-webkit-scrollbar{width:6px}
::-webkit-scrollbar-track{background:var(--bg-deep)}
::-webkit-scrollbar-thumb{background:var(--border);border-radius:3px}
::selection{background:var(--accent-glow);color:var(--text)}
</style>
</head>
<body>

<div class="bg-orbs">
  <div class="orb orb-1"></div>
  <div class="orb orb-2"></div>
  <div class="orb orb-3"></div>
</div>
<div class="bg-grid"></div>

<div class="loading-overlay" id="loadingOverlay">
  <div class="spinner"></div>
  <div style="display:flex;flex-direction:column;align-items:center;gap:8px">
    <div class="loading-title">Analyzing your food</div>
    <div class="loading-sub" id="loadingMsg">Scanning image with AI vision...</div>
  </div>
</div>

<input type="file" id="fileInput" accept="image/*" capture="environment">

<div class="container">
  <button class="theme-toggle" id="themeToggle" title="Toggle theme">🌙</button>

  <header>
    <div class="header-top">
      <span class="badge"><span class="badge-dot"></span>AI Vision · Live Analysis</span>
    </div>
    <h1>NutriScan AI</h1>
    <p class="subtitle">Instant, precise nutritional intelligence from a single photo</p>
  </header>

  <div class="card">
    <div class="section-label">Step 01 — Capture Food</div>

    <div class="drop-zone" id="dropZone">
      <video id="videoEl" playsinline autoplay muted></video>
      <img id="preview" alt="Food preview">
      <div class="upload-placeholder" id="uploadPlaceholder">
        <div class="upload-icon">📸</div>
        <h3>Drop your food photo here</h3>
        <p>or use the buttons below to upload or take a photo<br>
           <span style="opacity:.6;font-size:11px;">JPG, PNG, WEBP supported</span>
        </p>
      </div>
    </div>

    <div class="btn-row">
      <button class="btn" onclick="openCamera()" id="cameraBtn">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/>
          <circle cx="12" cy="13" r="4"/>
        </svg>
        Camera
      </button>
      <button class="btn" id="captureBtn" onclick="captureFromCamera()">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="3" fill="currentColor"/>
        </svg>
        Snap
      </button>
      <button class="btn" onclick="document.getElementById('fileInput').click()">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
          <polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/>
        </svg>
        Upload
      </button>
    </div>

    <div class="section-label" style="margin-top:8px">Step 02 — Set Portion Weight</div>

    <div class="weight-row">
      <div class="input-wrap">
        <label for="massInput">Mass / Weight</label>
        <input type="number" id="massInput" value="100" min="1" max="10000" step="1" placeholder="100">
      </div>
      <div>
        <div style="font-size:11px;font-weight:600;color:var(--text-muted);letter-spacing:.1em;text-transform:uppercase;margin-bottom:8px;">Unit</div>
        <div class="unit-toggle">
          <button class="unit-btn active" id="btnG" onclick="setUnit('g')">g</button>
          <button class="unit-btn" id="btnKg" onclick="setUnit('kg')">kg</button>
        </div>
      </div>
    </div>

    <button class="btn btn-primary" id="analyzeBtn" onclick="analyzeFood()" disabled style="width:100%;margin-top:4px;">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
        <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
      </svg>
      Analyze Nutrition
    </button>
  </div>

  <div class="msg msg-error" id="errorMsg">
    <span class="msg-icon">⚠️</span><span id="errorText"></span>
  </div>
  <div class="msg msg-success" id="successMsg">
    <span class="msg-icon">✅</span><span id="successText"></span>
  </div>

  <div id="results">
    <div class="card">
      <div class="section-label">Analysis Results</div>
      <div class="food-identity">
        <div>
          <div class="food-name" id="foodName">—</div>
          <div class="food-desc" id="foodDesc">—</div>
        </div>
        <div class="confidence-pill">
          <div class="confidence-num" id="confidenceVal">—</div>
          <div class="confidence-label">Confidence</div>
        </div>
      </div>

      <div class="calories-hero">
        <div>
          <div class="calories-num" id="caloriesVal">0</div>
          <div class="calories-meta">KILOCALORIES · <span id="weightLabel">100g</span></div>
        </div>
        <div class="health-ring-wrap">
          <svg width="90" height="90" viewBox="0 0 90 90">
            <circle cx="45" cy="45" r="38" fill="none" stroke="rgba(255,255,255,0.05)" stroke-width="6"/>
            <circle cx="45" cy="45" r="38" fill="none" stroke="var(--lime)" stroke-width="6"
              stroke-linecap="round" stroke-dasharray="238.76" id="healthRing" stroke-dashoffset="238.76"/>
          </svg>
          <div class="health-ring-inner">
            <div class="health-score-num" id="healthScoreVal">0</div>
            <div class="health-score-label">Health</div>
          </div>
        </div>
      </div>

      <div class="section-label">Macronutrients</div>
      <div class="macros-grid">
        <div class="macro-tile" style="--tile-color:var(--rose)">
          <div class="macro-icon">🥩</div>
          <div class="macro-val"><span id="proteinVal">0</span><span class="macro-unit">g</span></div>
          <div class="macro-name">Protein</div>
        </div>
        <div class="macro-tile" style="--tile-color:var(--teal)">
          <div class="macro-icon">🌾</div>
          <div class="macro-val"><span id="carbsVal">0</span><span class="macro-unit">g</span></div>
          <div class="macro-name">Carbs</div>
        </div>
        <div class="macro-tile" style="--tile-color:var(--amber)">
          <div class="macro-icon">🧈</div>
          <div class="macro-val"><span id="fatVal">0</span><span class="macro-unit">g</span></div>
          <div class="macro-name">Total Fat</div>
        </div>
        <div class="macro-tile" style="--tile-color:var(--purple)">
          <div class="macro-icon">🌿</div>
          <div class="macro-val"><span id="fiberVal">0</span><span class="macro-unit">g</span></div>
          <div class="macro-name">Fiber</div>
        </div>
      </div>

      <div class="stats-row">
        <div class="stat-tile"><div class="stat-num" id="giVal">—</div><div class="stat-label">Glycemic Index</div></div>
        <div class="stat-tile"><div class="stat-num" id="waterVal2">—</div><div class="stat-label">Water (g)</div></div>
        <div class="stat-tile"><div class="stat-num" id="sugarVal2">—</div><div class="stat-label">Sugar (g)</div></div>
        <div class="stat-tile"><div class="stat-num" id="satFatVal2">—</div><div class="stat-label">Sat. Fat (g)</div></div>
      </div>
    </div>

    <div class="card">
      <div class="section-label">Visual Breakdown</div>
      <div class="charts-row">
        <div class="chart-card">
          <div class="chart-title">Macro Ratio</div>
          <canvas id="macroDonut" height="200"></canvas>
        </div>
        <div class="chart-card">
          <div class="chart-title">Detailed Breakdown</div>
          <canvas id="breakdownBar" height="200"></canvas>
        </div>
      </div>
    </div>

    <div class="card">
      <div class="section-label">Micronutrients</div>
      <div class="micro-grid">
        <div class="micro-tile"><span class="micro-name">Sodium</span><span class="micro-val" id="sodiumVal">—</span></div>
        <div class="micro-tile"><span class="micro-name">Potassium</span><span class="micro-val" id="potassiumVal">—</span></div>
        <div class="micro-tile"><span class="micro-name">Calcium</span><span class="micro-val" id="calciumVal">—</span></div>
        <div class="micro-tile"><span class="micro-name">Iron</span><span class="micro-val" id="ironVal">—</span></div>
        <div class="micro-tile"><span class="micro-name">Vitamin C</span><span class="micro-val" id="vitcVal">—</span></div>
        <div class="micro-tile"><span class="micro-name">Vitamin A</span><span class="micro-val" id="vitaVal">—</span></div>
      </div>
      <div class="section-label" style="margin-top:4px">Tags</div>
      <div class="tags-wrap" id="tagsContainer"></div>
    </div>
  </div>

  <div class="footer">NutriScan AI · Powered by Vision AI via OpenRouter · Estimates only — not medical advice</div>
</div>

<script>
let capturedImage = null;
let currentUnit = 'g';
let videoStream = null;
let isCameraActive = false;
let macroChart = null;
let barChart = null;

/* Theme toggle */
const themeToggle = document.getElementById('themeToggle');
let isDark = true;
themeToggle.addEventListener('click', () => {
  isDark = !isDark;
  document.documentElement.setAttribute('data-theme', isDark ? 'dark' : 'light');
  themeToggle.textContent = isDark ? '🌙' : '☀️';
});

/* Loading messages */
const loadingMessages = [
  'Scanning image with AI vision...',
  'Identifying food components...',
  'Calculating macronutrients...',
  'Cross-referencing nutritional data...',
  'Finalizing your results...'
];
let loadMsgInterval = null;

function startLoadingMessages() {
  let i = 0;
  document.getElementById('loadingMsg').textContent = loadingMessages[0];
  loadMsgInterval = setInterval(() => {
    i = (i + 1) % loadingMessages.length;
    document.getElementById('loadingMsg').textContent = loadingMessages[i];
  }, 1800);
}

function stopLoadingMessages() { clearInterval(loadMsgInterval); }

/* File input */
document.getElementById('fileInput').addEventListener('change', function(e) {
  const file = e.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = ev => setImage(ev.target.result);
  reader.readAsDataURL(file);
  this.value = '';
});

/* Drag & drop */
const dropZone = document.getElementById('dropZone');
dropZone.addEventListener('dragover', e => { e.preventDefault(); dropZone.classList.add('dragover'); });
dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
dropZone.addEventListener('drop', e => {
  e.preventDefault(); dropZone.classList.remove('dragover');
  const file = e.dataTransfer.files[0];
  if (file && file.type.startsWith('image/')) {
    const reader = new FileReader();
    reader.onload = ev => setImage(ev.target.result);
    reader.readAsDataURL(file);
  }
});
dropZone.addEventListener('click', () => {
  if (!isCameraActive && !capturedImage) document.getElementById('fileInput').click();
});

/* Camera */
async function openCamera() {
  if (isCameraActive) { stopCamera(); return; }
  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: { ideal: 'environment' }, width: { ideal: 1280 }, height: { ideal: 960 } }
    });
    videoStream = stream;
    const video = document.getElementById('videoEl');
    video.srcObject = stream;
    video.classList.add('visible');
    document.getElementById('preview').classList.remove('visible');
    document.getElementById('uploadPlaceholder').style.opacity = '0';
    document.getElementById('captureBtn').style.display = 'flex';
    document.getElementById('cameraBtn').innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg> Stop`;
    isCameraActive = true;
    capturedImage = null;
    document.getElementById('analyzeBtn').disabled = true;
    dropZone.classList.remove('has-image');
  } catch { showError('Camera access denied. Please upload a photo instead.'); }
}

function stopCamera() {
  if (videoStream) { videoStream.getTracks().forEach(t => t.stop()); videoStream = null; }
  document.getElementById('videoEl').classList.remove('visible');
  document.getElementById('videoEl').srcObject = null;
  isCameraActive = false;
  document.getElementById('captureBtn').style.display = 'none';
  document.getElementById('uploadPlaceholder').style.opacity = '1';
  document.getElementById('cameraBtn').innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/><circle cx="12" cy="13" r="4"/></svg> Camera`;
}

function captureFromCamera() {
  const video = document.getElementById('videoEl');
  const canvas = document.createElement('canvas');
  canvas.width = video.videoWidth; canvas.height = video.videoHeight;
  canvas.getContext('2d').drawImage(video, 0, 0);
  stopCamera();
  setImage(canvas.toDataURL('image/jpeg', 0.9));
}

function setImage(dataUrl) {
  capturedImage = dataUrl;
  const preview = document.getElementById('preview');
  preview.src = dataUrl;
  preview.classList.add('visible');
  document.getElementById('uploadPlaceholder').style.opacity = '0';
  dropZone.classList.add('has-image');
  document.getElementById('analyzeBtn').disabled = false;
  hideMessages();
  showSuccess('Image loaded! Set the weight and click Analyze.');
}

function setUnit(unit) {
  currentUnit = unit;
  document.getElementById('btnG').classList.toggle('active', unit === 'g');
  document.getElementById('btnKg').classList.toggle('active', unit === 'kg');
}

async function analyzeFood() {
  if (!capturedImage) return;
  const mass = parseFloat(document.getElementById('massInput').value);
  if (!mass || mass <= 0) { showError('Please enter a valid weight.'); return; }
  hideMessages();
  document.getElementById('results').classList.remove('visible');
  showLoading(true);
  try {
    const response = await fetch('/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ image: capturedImage, mass, unit: currentUnit })
    });
    const json = await response.json();
    showLoading(false);
    if (!response.ok || json.error) { showError(json.error || 'Analysis failed. Please try again.'); return; }
    renderResults(json.data, mass, currentUnit);
    showSuccess('Analysis complete! Scroll down to view results.');
  } catch {
    showLoading(false);
    showError('Network error. Make sure the server is running.');
  }
}

function renderResults(d, mass, unit) {
  const m = d.macros || {};
  const mi = d.micronutrients || {};

  document.getElementById('foodName').textContent = d.food_name || 'Unknown Food';
  document.getElementById('foodDesc').textContent = d.food_description || '';
  document.getElementById('confidenceVal').textContent = (d.confidence || 0) + '%';
  document.getElementById('weightLabel').textContent = mass + unit;

  animateCounter('caloriesVal', 0, Math.round(d.calories || 0), 1200);
  animateCounterFloat('proteinVal', 0, parseFloat(m.protein_g) || 0, 1000);
  animateCounterFloat('carbsVal',   0, parseFloat(m.carbohydrates_g) || 0, 1000);
  animateCounterFloat('fatVal',     0, parseFloat(m.fat_g) || 0, 1000);
  animateCounterFloat('fiberVal',   0, parseFloat(m.fiber_g) || 0, 1000);

  document.getElementById('giVal').textContent      = d.glycemic_index || '—';
  document.getElementById('waterVal2').textContent  = fmt(d.water_content_g);
  document.getElementById('sugarVal2').textContent  = fmt(m.sugar_g);
  document.getElementById('satFatVal2').textContent = fmt(m.saturated_fat_g);

  const hs = Math.min(100, Math.max(0, d.health_score || 0));
  document.getElementById('healthScoreVal').textContent = hs;
  setTimeout(() => {
    document.getElementById('healthRing').style.transition = 'stroke-dashoffset 1.4s cubic-bezier(0.16,1,0.3,1)';
    document.getElementById('healthRing').style.strokeDashoffset = 238.76 - (hs / 100) * 238.76;
  }, 300);

  document.getElementById('sodiumVal').textContent    = fmt(mi.sodium_mg)    + ' mg';
  document.getElementById('potassiumVal').textContent = fmt(mi.potassium_mg) + ' mg';
  document.getElementById('calciumVal').textContent   = fmt(mi.calcium_mg)   + ' mg';
  document.getElementById('ironVal').textContent      = fmt(mi.iron_mg)      + ' mg';
  document.getElementById('vitcVal').textContent      = fmt(mi.vitamin_c_mg) + ' mg';
  document.getElementById('vitaVal').textContent      = fmt(mi.vitamin_a_iu) + ' IU';

  const tc = document.getElementById('tagsContainer');
  tc.innerHTML = '';
  (d.tags || []).forEach(tag => {
    const el = document.createElement('span');
    el.className = 'tag'; el.textContent = tag; tc.appendChild(el);
  });

  renderMacroDonut(m);
  renderBreakdownBar(m, d);

  document.getElementById('results').classList.add('visible');
  setTimeout(() => document.getElementById('results').scrollIntoView({ behavior: 'smooth', block: 'start' }), 100);
}

function renderMacroDonut(m) {
  if (macroChart) macroChart.destroy();
  const ctx = document.getElementById('macroDonut').getContext('2d');
  macroChart = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['Protein', 'Carbs', 'Fat', 'Fiber'],
      datasets: [{ data: [parseFloat(m.protein_g)||0, parseFloat(m.carbohydrates_g)||0, parseFloat(m.fat_g)||0, parseFloat(m.fiber_g)||0], backgroundColor: ['#fb7185','#2dd4bf','#fbbf24','#a78bfa'], borderColor: 'transparent', hoverOffset: 8, borderRadius: 4 }]
    },
    options: {
      responsive: true, cutout: '68%',
      animation: { animateRotate: true, duration: 1200, easing: 'easeOutQuart' },
      plugins: {
        legend: { position: 'bottom', labels: { color: '#64748b', font: { family: 'DM Sans', size: 11, weight: '600' }, padding: 12, usePointStyle: true, pointStyleWidth: 8 } },
        tooltip: { backgroundColor: '#111c2e', borderColor: 'rgba(255,255,255,0.08)', borderWidth: 1, titleColor: '#e2e8f0', bodyColor: '#94a3b8', callbacks: { label: c => ` ${c.label}: ${c.parsed.toFixed(1)}g` } }
      }
    }
  });
}

function renderBreakdownBar(m, d) {
  if (barChart) barChart.destroy();
  const ctx = document.getElementById('breakdownBar').getContext('2d');
  barChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['Sugar', 'Sat. Fat', 'Unsat. Fat', 'Water'],
      datasets: [{ data: [parseFloat(m.sugar_g)||0, parseFloat(m.saturated_fat_g)||0, parseFloat(m.unsaturated_fat_g)||0, parseFloat(d.water_content_g)||0], backgroundColor: ['#fb923c','#fb7185','#38bdf8','#2dd4bf'], borderRadius: 6, borderSkipped: false }]
    },
    options: {
      responsive: true,
      animation: { duration: 1200, easing: 'easeOutQuart' },
      scales: {
        x: { ticks: { color: '#64748b', font: { family: 'DM Sans', size: 10 } }, grid: { color: 'rgba(255,255,255,0.04)' } },
        y: { ticks: { color: '#64748b', font: { family: 'DM Sans', size: 10 } }, grid: { color: 'rgba(255,255,255,0.04)' } }
      },
      plugins: {
        legend: { display: false },
        tooltip: { backgroundColor: '#111c2e', borderColor: 'rgba(255,255,255,0.08)', borderWidth: 1, titleColor: '#e2e8f0', bodyColor: '#94a3b8', callbacks: { label: c => ` ${c.parsed.y.toFixed(1)}g` } }
      }
    }
  });
}

/* Animated counters */
function animateCounter(id, from, to, duration) {
  const el = document.getElementById(id);
  const start = performance.now();
  function step(now) {
    const p = Math.min((now - start) / duration, 1);
    const ease = 1 - Math.pow(1 - p, 4);
    el.textContent = Math.round(from + (to - from) * ease);
    if (p < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}

function animateCounterFloat(id, from, to, duration) {
  const el = document.getElementById(id);
  const start = performance.now();
  function step(now) {
    const p = Math.min((now - start) / duration, 1);
    const ease = 1 - Math.pow(1 - p, 4);
    const val = from + (to - from) * ease;
    el.textContent = val % 1 === 0 ? val.toFixed(0) : val.toFixed(1);
    if (p < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}

function fmt(val) { const n = parseFloat(val)||0; return n%1===0 ? n.toString() : n.toFixed(1); }

function showLoading(show) {
  const overlay = document.getElementById('loadingOverlay');
  if (show) { overlay.classList.add('active'); startLoadingMessages(); }
  else { overlay.classList.remove('active'); stopLoadingMessages(); }
}

function showError(msg) {
  hideMessages();
  document.getElementById('errorText').textContent = msg;
  document.getElementById('errorMsg').classList.add('visible');
}

function showSuccess(msg) {
  document.getElementById('successText').textContent = msg;
  document.getElementById('successMsg').classList.add('visible');
  setTimeout(() => document.getElementById('successMsg').classList.remove('visible'), 4000);
}

function hideMessages() {
  document.getElementById('errorMsg').classList.remove('visible');
  document.getElementById('successMsg').classList.remove('visible');
}
</script>
</body>
</html>
'''

@app.route("/")
def index():
    return make_response(INDEX_HTML, 200, {"Content-Type": "text/html; charset=utf-8"})


@app.route("/analyze", methods=["POST"])
def analyze():
    if not OPENROUTER_API_KEY:
        return jsonify({"error": "OPENROUTER_API_KEY is not set. See README for setup instructions."}), 500

    try:
        data = request.get_json()
        image_data = data.get("image")
        mass = data.get("mass", 100)
        unit = data.get("unit", "g")

        if not image_data:
            return jsonify({"error": "No image provided"}), 400

        # Convert mass to grams
        mass_g = float(mass) * 1000 if unit == "kg" else float(mass)

        # Strip base64 prefix and detect MIME type
        mime_type = "image/jpeg"
        raw_b64 = image_data
        if "," in image_data:
            header, raw_b64 = image_data.split(",", 1)
            if "png" in header:
                mime_type = "image/png"
            elif "webp" in header:
                mime_type = "image/webp"

        prompt = f"""You are an expert nutritionist and food scientist. Analyze this food image and provide highly accurate nutritional information.

The food portion weighs exactly {mass_g}g ({mass}{unit}).

Identify the food(s) visible and calculate precise macros and nutrition facts for this exact weight.

Respond ONLY with a valid JSON object in this exact format (no markdown, no explanation, no backticks):
{{
  "food_name": "specific food name",
  "food_description": "brief description of what you see",
  "confidence": 95,
  "serving_weight_g": {mass_g},
  "calories": 0,
  "macros": {{
    "protein_g": 0.0,
    "carbohydrates_g": 0.0,
    "fat_g": 0.0,
    "fiber_g": 0.0,
    "sugar_g": 0.0,
    "saturated_fat_g": 0.0,
    "unsaturated_fat_g": 0.0
  }},
  "micronutrients": {{
    "sodium_mg": 0.0,
    "potassium_mg": 0.0,
    "calcium_mg": 0.0,
    "iron_mg": 0.0,
    "vitamin_c_mg": 0.0,
    "vitamin_a_iu": 0.0
  }},
  "glycemic_index": 0,
  "water_content_g": 0.0,
  "health_score": 0,
  "tags": ["tag1", "tag2"]
}}

Be as accurate as possible using standard nutritional databases. All values must be for the specified weight of {mass_g}g."""

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        }

        last_error = None
        for model in VISION_MODELS:
            try:
                payload = {
                    "model": model,
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "image_url",
                                    "image_url": {"url": f"data:{mime_type};base64,{raw_b64}"},
                                },
                                {"type": "text", "text": prompt},
                            ],
                        }
                    ],
                    "max_tokens": 1000,
                }

                api_response = requests.post(
                    OPENROUTER_URL, headers=headers, json=payload, timeout=60
                )
                api_response.raise_for_status()

                result = api_response.json()
                response_text = result["choices"][0]["message"]["content"].strip()

                # Strip any accidental markdown fences
                response_text = re.sub(r"```json\n?", "", response_text)
                response_text = re.sub(r"```\n?", "", response_text).strip()

                nutrition_data = json.loads(response_text)
                return jsonify({"success": True, "data": nutrition_data})

            except Exception as e:
                last_error = e
                continue

        return jsonify({"error": f"All vision models failed. Last error: {str(last_error)}"}), 500

    except json.JSONDecodeError as e:
        return jsonify({"error": f"Failed to parse nutrition data: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=debug, host="0.0.0.0", port=port)
