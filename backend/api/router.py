import io
import logging
import traceback
from urllib.parse import quote

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from backend.core.parser.binary_parser import BinaryParser
from backend.core.parser.xml_parser import XmlParser
from backend.core.converter.midi_writer import MidiWriter

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/analyze")
async def analyze_file(file: UploadFile = File(...)):
    filename = file.filename.lower()
    logger.info(f"Received analysis request for file: {filename}")

    try:
        content = await file.read()
        song = _parse_file_content(filename, content)
        
        tracks = []
        for track in song.tracks:
            tracks.append({
                "id": track.number, # utilizing the 1-based index as ID
                "name": track.name,
                "program": track.program,
                "is_percussion": track.is_percussion,
                "channel": track.channel
            })
            
        return {"tracks": tracks}

    except HTTPException as he:
        raise he
    except Exception as e:
        error_trace = traceback.format_exc()
        logger.error(f"Error during analysis: {e}")
        logger.error(error_trace)
        raise HTTPException(status_code=500, detail={"message": str(e), "trace": error_trace})


@router.post("/convert")
async def convert_file(
    file: UploadFile = File(...), 
    high_fidelity: bool = True,
    selected_tracks: str = None # Comma-separated list of track IDs
):
    filename = file.filename.lower()
    logger.info(
        f"Received conversion request for file: {filename} "
        f"(High Fidelity: {high_fidelity}, Selected Tracks: {selected_tracks})"
    )

    try:
        content = await file.read()
        song = _parse_file_content(filename, content)

        # Filter tracks if selection is provided
        if selected_tracks:
            try:
                # expecting "1,2,3"
                selected_ids = [int(tid.strip()) for tid in selected_tracks.split(",") if tid.strip()]
                if selected_ids:
                    # Filter existing tracks. Keep order.
                    # Note: Track.number is 1-based index assigned during parse
                    song.tracks = [t for t in song.tracks if t.number in selected_ids]
                    logger.info(f"Filtered to {len(song.tracks)} tracks.")
            except Exception as e:
                logger.warning(f"Failed to parse selected_tracks: {e}")
                # Fallback to all tracks or raise error? 
                # Let's log and proceed with all tracks to be safe, or maybe just ignore the filter.

        # Convert
        logger.info("Converting to MIDI...")
        writer = MidiWriter(song, high_fidelity=high_fidelity)

        # Write to in-memory buffer
        midi_buffer = io.BytesIO()
        writer.write(file=midi_buffer)
        midi_buffer.seek(0)
        
        midi_content = midi_buffer.getvalue()
        logger.info(f"MIDI generated in memory. Size: {len(midi_content)} bytes")

        # RFC 5987 compliant encoding
        encoded_filename = quote(f"{file.filename}.mid")

        return StreamingResponse(
            io.BytesIO(midi_content),
            media_type="audio/midi",
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
            },
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        error_trace = traceback.format_exc()
        logger.error(f"Error during conversion: {e}")
        logger.error(error_trace)
        raise HTTPException(status_code=500, detail={"message": str(e), "trace": error_trace})


def _parse_file_content(filename: str, content: bytes):
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
    return song
