<div align="center">

  <img src="frontend/public/logo.svg" alt="GP2MIDI Logo" width="120" height="120" />

  # GP2MIDI V2.1

  **Studio-Grade Guitar Pro to MIDI Converter**
  
  Converts `.gp3`, `.gp4`, `.gp5`, `.gpx`, and `.gp` files into high-fidelity MIDI.

  [![License](https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square)](LICENSE)
  [![Version](https://img.shields.io/badge/version-2.1-green.svg?style=flat-square)](https://github.com/fervidos/gp2midi)
  [![Build Status](https://img.shields.io/badge/build-passing-success.svg?style=flat-square)](https://github.com/fervidos/gp2midi/actions)
  [![Issues](https://img.shields.io/github/issues/fervidos/gp2midi?style=flat-square)](https://github.com/fervidos/gp2midi/issues)
  [![Pull Requests](https://img.shields.io/github/issues-pr/fervidos/gp2midi?style=flat-square)](https://github.com/fervidos/gp2midi/pulls)
  [![Deploy with Vercel](https://img.shields.io/badge/deploy-vercel-black?style=flat-square&logo=vercel)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2Ffervidos%2Fgp2midi)

  [**View Live Demo**](https://gp2midi.vercel.app/) • [**Report Bug**](https://github.com/fervidos/gp2midi/issues) • [**Request Feature**](https://github.com/fervidos/gp2midi/issues)

</div>

<br />

## 🚀 Overview

**gp2midi** is a powerful engine designed for musicians and producers who need to extract performance data from Guitar Pro files with precision. Unlike simple converters, gp2midi preserves the nuance of guitar performance using advanced MIDI features.

## 🌟 New in V2.1: Instrument Expansion

The engine now supports advanced MIDI features to unlock thousands of sounds:

| Feature | Description |
|:---|:---|
| **Bank Select Support** | Automatically parses and emits `CC0` (Bank MSB) and `CC32` (Bank LSB) messages, unlocking access to GM2, GS, and XG instrument banks. |
| **Smart Channel Allocation** | Intelligently manages MIDI channels. In **High Fidelity** mode, it uses 6 channels per track for MPE-style bends. If channels run low, it gracefully degrades to Standard mode. |
| **Advanced Pitch Bends** | Parses pitch bends from GP files and generates smooth, linearly interpolated MIDI pitch wheel events. Supports semitone-level precision. |

## ✨ Key Features

- **Format Support**: Handles legacy (GP3-GP5) and modern (GPX, GP) files.
- **High Fidelity Conversion**:
  - Independent pitch bends per string.
  - Accurate timing and durations.
  - Percussion track handling (automatically mapped to Channel 10).
- **Premium UI**:
  - "Midnight/Aurora" dark mode design.
  - Drag-and-drop interface.
  - Real-time conversion feedback.
- **Modular Backend**: Built with FastAPI and a layered architecture for easy extension.

## 🛠 Usage

1. **Open the App**: Navigate to the web interface.
2. **Select Mode**: Toggle **High Fidelity Mode** if you want independent string control (requires a compatible synth/DAW like Omnisphere or Kontakt).
3. **Drag & Drop**: Drop your Guitar Pro file onto the zone.
4. **Download**: The MIDI file is generated instantly.

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Node.js 16+

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/fervidos/gp2midi.git
   cd gp2midi
   ```

2. **Backend Setup**
   ```bash
   cd backend
   pip install -r requirements.txt
   python main.py
   ```
   The API will start at `http://localhost:8000`.

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   Access the app at `http://localhost:5173`.

## 🧩 Architecture

- **Backend**: Python (FastAPI)
  - `core/parser`: Modular XML and Binary parsers.
  - `core/converter`: MIDI generation with Smart Channel Management.
  - `api`: REST endpoints.
- **Frontend**: React (Vite)
  - Custom `useConversion` hook.
  - Component-based architecture.

## 🤝 Contributing

Contributions are welcome! Please fork the repository and submit a pull request.
