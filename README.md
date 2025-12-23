# gp2midi V2.1

A professional, studio-grade tool to convert Guitar Pro files (`.gp3`, `.gp4`, `.gp5`, `.gpx`, `.gp`) into high-fidelity MIDI.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Version](https://img.shields.io/badge/version-2.1-green.svg)

## 🌟 New in V2.1: Instrument Expansion

The engine now supports advanced MIDI features to unlock thousands of sounds:
- **Bank Select Support**: Automatically parses and emits `CC0` (Bank MSB) and `CC32` (Bank LSB) messages, allowing access to GM2, GS, and XG instrument banks.
- **Smart Channel Allocation**: 
  - **High Fidelity Mode**: Uses 6 MIDI channels per guitar track for independent string bending (MPE-style).
  - **Safe Fallback**: If the 16-channel limit is reached, it gracefully degrades to "Standard Mode" (1 channel per track) to prevent errors.

## ✨ Features

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

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Node.js 16+
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/gp2midi.git
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

## 🛠 Usage

1. Open the web interface.
2. Toggle **High Fidelity Mode** if you want independent string control (requires a compatible synth/DAW).
3. Drag & Drop your Guitar Pro file.
4. Download the generated MIDI file immediately.

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
