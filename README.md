# GP2MIDI Pro

<div align="center">
  <img src="frontend/public/logo.svg" width="120" height="120" alt="GP2MIDI Pro Logo" />
  <h1>GP2MIDI Pro</h1>
  <p><strong>Studio-Grade Guitar Pro to MIDI Converter</strong></p>
  
  <a href="https://gp2midi.vercel.app/">
    <img src="https://img.shields.io/badge/Live_Demo-Visit_Site-38bdf8?style=for-the-badge&logo=vercel" alt="Live Demo" />
  </a>
  
  <p>
    <a href="#-key-features">Key Features</a> •
    <a href="#-getting-started">Getting Started</a> •
    <a href="#-api-reference">API Reference</a> •
    <a href="#-contributing">Contributing</a>
  </p>
  
  ![License](https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square)
  ![Python](https://img.shields.io/badge/python-3.9+-blue.svg?style=flat-square)
  ![React](https://img.shields.io/badge/frontend-React-61dafb.svg?style=flat-square)
  ![Status](https://img.shields.io/badge/status-stable-green.svg?style=flat-square)
</div>

<br />

> **GP2MIDI Pro** is a modern, full-stack application designed to bridge the gap between tablature and production. Unlike basic converters, it preserves the nuance of your guitar tracks—handling bends, slides, and multiple voices with a proprietary "High Fidelity" mode that maps strings to separate MIDI channels for maximum expressiveness (MPE-ready).

---

## ✨ Key Features

- **🚀 Universal Format Support**
  Reads everything from legacy **Guitar Pro 3/4/5** (`.gp3`, `.gp4`, `.gp5`) to modern XML-based formats (`.gpx`, `.gp`).

- **🎛️ High Fidelity Mode (MPE Style)**
  Intelligent channel allocation separates guitar strings onto distinct MIDI channels (1-6). This allows for **independent pitch bends** on each string, essentially turning your MIDI output into an MPE (MIDI Polyphonic Expression) controller. Perfect for unison bends and complex articulations.

- **🌌 Immersive UI**
  A stunning, dark-mode Interface built with **React** & **Glassmorphism**. Features a dynamic starry background with parallax depth and shooting stars.

- **⚡ Real-Time Processing**
  Drag-and-Drop files for instant conversion using our high-performance Python parser.

- **🔌 REST API**
  Robust **FastAPI** backend for integrating conversion logic into larger pipelines or automation scripts.

- **🛠️ Developer Ready**
  Fully typed codebase with linting (Ruff/ESLint), tests (Pytest), and modular architecture.

---

## 🏗️ Architecture

The project follows a modern monorepo structure:

- **Backend (`/backend`)**: A **Python FastAPI** application that handles the complex parsing (Binary & XML) and MIDI generation.
- **Frontend (`/frontend`)**: A **React (Vite)** application providing the user interface.

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.9+**
- **Node.js 16+** (for Frontend)

### 📥 Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/fervidos/gp2midi.git
    cd gp2midi
    ```

2.  **Backend Setup**:
    ```bash
    cd backend
    pip install -r requirements.txt
    ```

3.  **Frontend Setup**:
    ```bash
    cd ../frontend
    npm install
    ```

### ⚡ Quick Start (Windows)

We provide a one-click PowerShell script to launch both services instantly:

```powershell
.\scripts\start_app.ps1
```

*This will open two terminal windows (one for Backend, one for Frontend) and launch the app.*

### 🛠️ Manual Start

If you prefer to run services manually:

**1. Start Backend:**
```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```
*API Docs available at: [http://localhost:8000/docs](http://localhost:8000/docs)*

**2. Start Frontend:**
```bash
cd frontend
npm run dev
```
*Access UI at: `http://localhost:5173`*

---

## 🧪 Development & Testing

We maintain high code quality standards. Run the following commands to verify your environment.

### Backend
- **Linting**: `cd backend && python -m ruff check .`
- **Testing**: `cd backend && python -m pytest tests/`

### Frontend
- **Linting**: `cd frontend && npm run lint`
- **Formatting**: `cd frontend && npm run format`

---

## 📚 API Reference

### `POST /convert`

Uploads a file for conversion.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `file` | `File` | Required | The Guitar Pro file (`.gp*`) |
| `high_fidelity` | `bool` | `true` | Enable MPE-style channel separation |

**Example w/ cURL:**
```bash
curl -X POST "http://localhost:8000/convert?high_fidelity=true" \
  -F "file=@mysong.gp" \
  --output mysong.mid
```

---

## ☁️ Deployment (Vercel)

The project is pre-configured for **Vercel** deployment (Serverless Python + React).

1.  Push your code to GitHub.
2.  Import project in Vercel.
3.  **Important**: In "Build & Development Settings", set **Output Directory** to: `frontend/dist`.
4.  Deploy! 🚀

The included `vercel.json` handles the routing between the Python backend (serverless) and the React frontend.

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:
1. Fork the repo.
2. Create a feature branch (`git checkout -b feature/amazing-feature`).
3. Commit your changes.
4. Push to the branch.
5. Open a Pull Request.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

<div align="center">
  <p><i>Made with ❤️ by the GP2MIDI Team</i></p>
</div>
