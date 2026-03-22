<div align="center">

# 🥗 NutriScan AI

**Instant AI-powered food nutrition analysis from a single photo**

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=flat-square&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![OpenRouter](https://img.shields.io/badge/OpenRouter-Vision%20AI-6366f1?style=flat-square)](https://openrouter.ai)
[![License: MIT](https://img.shields.io/badge/License-MIT-22c55e?style=flat-square)](LICENSE)

Upload a photo of any food → get instant macros, micros, calories, and a health score.

</div>

---

## ✨ Features

| | |
|---|---|
| 📷 **Camera & Upload** | Live camera capture or photo upload with drag-and-drop |
| ⚖️ **Custom Portions** | Enter exact weight in grams or kilograms |
| 🤖 **Vision AI** | Powered by Gemini 2.0 Flash via OpenRouter |
| 📊 **Full Macros** | Protein, carbs, fat, fiber, sugar, saturated/unsaturated fat |
| 🔬 **Micronutrients** | Sodium, potassium, calcium, iron, Vitamin C & A |
| 📈 **Animated Charts** | Macro ratio donut + breakdown bar chart (Chart.js) |
| 💧 **Extra Data** | Water content, glycemic index, health score |
| 🌙 **Dark / Light Mode** | Toggle with one click |
| 📱 **Mobile-first** | Fully responsive, works on any device |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- A free [OpenRouter API key](https://openrouter.ai/keys)

### 1 — Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/nutriscan-ai.git
cd nutriscan-ai
```

### 2 — Create a virtual environment
```bash
python -m venv .venv

# macOS / Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

### 3 — Install dependencies
```bash
pip install -r requirements.txt
```

### 4 — Configure your API key
```bash
cp .env.example .env
```
Open `.env` and paste your OpenRouter key:
```env
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxx
```

### 5 — Run
```bash
python app.py
```

Open **http://localhost:5000** in your browser. 🎉

---

## 📱 Mobile Access

To use NutriScan on your phone (same WiFi network):

```bash
# Find your local IP
ipconfig getifaddr en0   # macOS
hostname -I              # Linux
ipconfig                 # Windows → look for IPv4
```

Then open `http://YOUR_IP:5000` on your phone.

---

## 🏗️ Project Structure

```
nutriscan-ai/
├── app.py                 # Flask backend — API calls & routing
├── requirements.txt       # Python dependencies
├── .env.example           # Environment variable template
├── .gitignore
├── LICENSE
├── README.md
└── templates/
    └── index.html         # Full frontend (HTML + CSS + JS)
```

---

## 🔧 Configuration

All configuration is done via environment variables (`.env` file):

| Variable | Default | Description |
|---|---|---|
| `OPENROUTER_API_KEY` | *(required)* | Your OpenRouter API key |
| `FLASK_DEBUG` | `false` | Enable hot-reload for development |
| `PORT` | `5000` | Port to run the server on |

---

## 🤖 AI Models

NutriScan uses vision-capable models via [OpenRouter](https://openrouter.ai), tried in this order:

1. `google/gemini-2.0-flash-001` — primary (best quality)
2. `google/gemini-flash-1.5` — fallback
3. `meta-llama/llama-4-maverick` — secondary fallback

> **Note:** DeepSeek V3 is a text-only model and cannot analyze images. Only vision-capable models are used.

---

## 🚢 Deployment

### Railway / Render / Fly.io
Set `OPENROUTER_API_KEY` as an environment variable in your platform dashboard. The app reads `PORT` automatically.

### Docker
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```

```bash
docker build -t nutriscan-ai .
docker run -p 5000:5000 -e OPENROUTER_API_KEY=your_key nutriscan-ai
```

---

## ⚠️ Disclaimer

Nutritional values are **AI estimates** based on visual analysis and standard food databases. They are not a substitute for professional dietary or medical advice. Accuracy depends on image quality and portion estimation.

---

## 📄 License

[MIT](LICENSE) — free to use, modify, and distribute.

---

<div align="center">
Made with ❤️ and AI · <a href="https://openrouter.ai">Powered by OpenRouter</a>
</div>
