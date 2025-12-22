from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import io
import os
import tempfile

from parser.binary_parser import BinaryParser
from parser.xml_parser import XmlParser
from converter.midi_writer import MidiWriter

app = FastAPI(title="GP2MIDI Converter", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "GP2MIDI Backend is running"}

@app.post("/convert")
async def convert_file(file: UploadFile = File(...), high_fidelity: bool = True):
    filename = file.filename.lower()
    content = await file.read()
    
    # Identify parser
    parser = None
    if filename.endswith(('.gp3', '.gp4', '.gp5')):
        parser = BinaryParser()
    elif filename.endswith(('.gpx', '.gp')):
         parser = XmlParser()
    else:
        raise HTTPException(status_code=400, detail="Unsupported file format.")

    try:
        # Parse
        song = parser.parse_bytes(content)
        
        # Convert
        writer = MidiWriter(song, high_fidelity=high_fidelity)
        
        # Write to memory buffer
        # MidiWriter saves to file path usually. We can adapt it or use a temp file.
        # Let's use a temp file for safety with mido
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mid") as tmp:
            tmp_path = tmp.name
        
        writer.write(tmp_path)
        
        # Read back
        with open(tmp_path, "rb") as f:
            midi_content = f.read()
            
        os.unlink(tmp_path)
        
        return StreamingResponse(io.BytesIO(midi_content), media_type="audio/midi", headers={"Content-Disposition": f"attachment; filename={file.filename}.mid"})

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
