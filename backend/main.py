import io
import logging
import os
import tempfile
import traceback
from backend.parser.binary_parser import BinaryParser
from backend.parser.xml_parser import XmlParser

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from backend.converter.midi_writer import MidiWriter

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

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
    logger.info("Health check requested")
    return {"status": "ok", "message": "GP2MIDI Backend is running"}


@app.post("/convert")
async def convert_file(file: UploadFile = File(...), high_fidelity: bool = True):
    filename = file.filename.lower()
    logger.info(
        f"Received conversion request for file: {filename} "
        f"(High Fidelity: {high_fidelity})"
    )

    try:
        content = await file.read()
        logger.info(f"File size: {len(content)} bytes")

        # Identify parser
        parser = None
        if filename.endswith((".gp3", ".gp4", ".gp5")):
            logger.info("Using BinaryParser")
            parser = BinaryParser()
        elif filename.endswith((".gpx", ".gp")):
            logger.info("Using XmlParser")
            parser = XmlParser()
        else:
            logger.warning(f"Unsupported file format: {filename}")
            raise HTTPException(status_code=400, detail="Unsupported file format.")

        # Parse
        logger.info("Parsing file...")
        song = parser.parse_bytes(content)
        logger.info("Parsing complete.")

        # Convert
        logger.info("Converting to MIDI...")
        writer = MidiWriter(song, high_fidelity=high_fidelity)

        # Write to in-memory buffer
        midi_buffer = io.BytesIO()
        writer.write(file=midi_buffer)
        midi_buffer.seek(0)
        
        midi_content = midi_buffer.getvalue()
        logger.info(f"MIDI generated in memory. Size: {len(midi_content)} bytes")
        logger.info("MIDI file created and cleaned up. Returning response.")

        return StreamingResponse(
            io.BytesIO(midi_content),
            media_type="audio/midi",
            headers={
                "Content-Disposition": f"attachment; filename={file.filename}.mid"
            },
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        error_trace = traceback.format_exc()
        logger.error(f"Error during conversion: {e}")
        logger.error(error_trace)
        raise HTTPException(status_code=500, detail={"message": str(e), "trace": error_trace})
