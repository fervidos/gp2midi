# GP2MIDI

GP2MIDI is a powerful tool designed to convert Guitar Pro files (`.gp3`, `.gp4`, `.gp5`, `.gpx`, `.gp`) into standard MIDI files (`.mid`). It features a modern web interface for easy file uploads and conversion, as well as a robust backend API and command-line utilities for advanced usage.

## Features

- **Wide Format Support**: Handles legacy binary formats (`.gp3`, `.gp4`, `.gp5`) and modern XML-based formats (`.gpx`, `.gp`).
- **Web Interface**: User-friendly React-based frontend for drag-and-drop conversion.
- **High Fidelity**: Preserves track details, tempo changes, and time signatures during conversion.
- **REST API**: FastAPI-powered backend for integrating conversion capabilities into other applications.
- **CLI Utility**: Dedicated script for batch processing or manual conversions.
- **One-Click Startup**: convenient PowerShell launcher script.

## Project Structure

```
gp2midi/
├── backend/                # Python FastAPI backend
│   ├── converter/          # MIDI generation logic
│   ├── models/             # Data models
│   ├── parser/             # Guitar Pro file parsers (Binary & XML)
│   ├── convert_file.py     # CLI conversion script
│   └── main.py             # API entry point
├── frontend/               # React Vite frontend
│   ├── src/                # UI source code
│   └── package.json        # Frontend dependencies
├── start_app.ps1           # One-click startup script (Windows)
└── debug_*.py              # Debugging utilities
```

## Prerequisites

- **Python 3.8+**
- **Node.js 14+** (for Frontend)

## Installation

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd gp2midi
    ```

2.  **Backend Setup**:
    ```bash
    cd backend
    pip install -r requirements.txt
    ```

3.  **Frontend Setup**:
    ```bash
    cd frontend
    npm install
    ```

## Usage

### Quick Start (Windows)

Simply run the startup script:

```powershell
.\start_app.ps1
```

This will automatically:
1.  Start the Backend server (listening on port 8000).
2.  Start the Frontend development server.
3.  Open necessary terminal windows.

### Manual Start

**Backend:**
```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```
API Docs will be available at: `http://localhost:8000/docs`

**Frontend:**
```bash
cd frontend
npm run dev
```

### CLI Conversion

You can act as a standard CLI tool for direct file conversion:

```bash
cd backend
python convert_file.py
```
*Note: You may need to edit `convert_file.py` to specify input/output paths or pass them as arguments if implemented.*

## API Documentation

### `POST /convert`

Upload a Guitar Pro file to convert it to MIDI.

- **Parameters**: 
  - `file`: The Guitar Pro file (Multipart/Form-Data).
  - `high_fidelity`: `boolean` (default: `true`).
- **Response**: Returns the converted `.mid` file stream.

## Contributing

Contributions are welcome! Please submit a Pull Request or open an Issue to discuss improvements or bug fixes.

## License

[MIT](LICENSE)
