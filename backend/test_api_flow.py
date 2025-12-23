import requests
import os
import io
import zipfile
import xml.etree.ElementTree as ET

# Assuming server is running on localhost:8000
BASE_URL = "http://localhost:8000"

def create_test_gpx(filename="temp_test.gpx"):
    NS = "http://www.guitar-pro.com/GPIF/1.0"
    ET.register_namespace("", NS)

    root = ET.Element(f"{{{NS}}}GPIF")

    # Rhythms
    rhythms = ET.SubElement(root, f"{{{NS}}}Rhythms")
    r_q = ET.SubElement(rhythms, f"{{{NS}}}Rhythm", id="0")
    ET.SubElement(r_q, f"{{{NS}}}NoteValue").text = "Quarter"

    # MasterTrack
    mt = ET.SubElement(root, f"{{{NS}}}MasterTrack")
    ET.SubElement(mt, f"{{{NS}}}Tracks").text = "0 1"

    # Tracks
    tracks_elem = ET.SubElement(root, f"{{{NS}}}Tracks")
    
    # Track 1 (ID 0)
    t0 = ET.SubElement(tracks_elem, f"{{{NS}}}Track", id="0")
    ET.SubElement(t0, f"{{{NS}}}Name").text = "Guitar"
    sounds0 = ET.SubElement(t0, f"{{{NS}}}Sounds")
    sound0 = ET.SubElement(sounds0, f"{{{NS}}}Sound")
    midi0 = ET.SubElement(sound0, f"{{{NS}}}MIDI")
    ET.SubElement(midi0, f"{{{NS}}}Program").text = "29" # Overdriven Guitar

    # Track 2 (ID 1)
    t1 = ET.SubElement(tracks_elem, f"{{{NS}}}Track", id="1")
    ET.SubElement(t1, f"{{{NS}}}Name").text = "Drums"
    ET.SubElement(t1, f"{{{NS}}}Properties") # Percussion logic relies on InstrumentSet Type usually, keeping simple for now
    sounds1 = ET.SubElement(t1, f"{{{NS}}}Sounds")
    sound1 = ET.SubElement(sounds1, f"{{{NS}}}Sound")
    midi1 = ET.SubElement(sound1, f"{{{NS}}}MIDI")
    ET.SubElement(midi1, f"{{{NS}}}Program").text = "0"

    # MasterBars
    mbs = ET.SubElement(root, f"{{{NS}}}MasterBars")
    mb0 = ET.SubElement(mbs, f"{{{NS}}}MasterBar")
    ET.SubElement(mb0, f"{{{NS}}}Time").text = "4/4"
    ET.SubElement(mb0, f"{{{NS}}}Bars").text = "100 101"

    # Bars
    bars = ET.SubElement(root, f"{{{NS}}}Bars")
    b100 = ET.SubElement(bars, f"{{{NS}}}Bar", id="100")
    ET.SubElement(b100, f"{{{NS}}}Voices").text = "200"
    b101 = ET.SubElement(bars, f"{{{NS}}}Bar", id="101")
    ET.SubElement(b101, f"{{{NS}}}Voices").text = "201"

    # Voices
    voices = ET.SubElement(root, f"{{{NS}}}Voices")
    v200 = ET.SubElement(voices, f"{{{NS}}}Voice", id="200")
    ET.SubElement(v200, f"{{{NS}}}Beats").text = "300"
    v201 = ET.SubElement(voices, f"{{{NS}}}Voice", id="201")
    ET.SubElement(v201, f"{{{NS}}}Beats").text = "301"

    # Beats
    beats = ET.SubElement(root, f"{{{NS}}}Beats")
    bt300 = ET.SubElement(beats, f"{{{NS}}}Beat", id="300")
    ET.SubElement(bt300, f"{{{NS}}}Rhythm", ref="0")
    ET.SubElement(bt300, f"{{{NS}}}Notes").text = "400"
    
    bt301 = ET.SubElement(beats, f"{{{NS}}}Beat", id="301")
    ET.SubElement(bt301, f"{{{NS}}}Rhythm", ref="0")
    ET.SubElement(bt301, f"{{{NS}}}Notes").text = "401"

    # Notes
    notes = ET.SubElement(root, f"{{{NS}}}Notes")
    n400 = ET.SubElement(notes, f"{{{NS}}}Note", id="400")
    props = ET.SubElement(n400, f"{{{NS}}}Properties")
    p_midi = ET.SubElement(props, f"{{{NS}}}Property", name="Midi")
    ET.SubElement(p_midi, f"{{{NS}}}Number").text = "60"

    n401 = ET.SubElement(notes, f"{{{NS}}}Note", id="401")
    props2 = ET.SubElement(n401, f"{{{NS}}}Properties")
    p_midi2 = ET.SubElement(props2, f"{{{NS}}}Property", name="Midi")
    ET.SubElement(p_midi2, f"{{{NS}}}Number").text = "36"

    # Create Zip
    with zipfile.ZipFile(filename, "w") as z:
        xml_str = ET.tostring(root, encoding="utf-8")
        z.writestr("score.gpif", xml_str)
    
    return filename

def test_api():
    file_path = create_test_gpx()
    print(f"Created test file: {file_path}")
    
    try:
        # 1. Test /api/analyze
        print("\n--- Testing /api/analyze ---")
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{BASE_URL}/api/analyze", files=files)
        
        if response.status_code != 200:
            print(f"Analyze failed: {response.text}")
            return

        data = response.json()
        print("Analysis Response:", data)
        tracks = data.get("tracks", [])
        if not tracks:
            print("No tracks found.")
            return

        # 2. Test /api/convert with subset of tracks
        # Select first track only
        selected_track_id = tracks[0]['id']
        print(f"\n--- Testing /api/convert with track {selected_track_id} ---")
        
        with open(file_path, 'rb') as f:
            files = {'file': f}
            params = {'selected_tracks': str(selected_track_id), 'high_fidelity': 'true'}
            response = requests.post(f"{BASE_URL}/api/convert", files=files, params=params)

        if response.status_code == 200:
            print("Conversion successful. Output size:", len(response.content))
            with open("test_output_filtered.mid", "wb") as f_out:
                f_out.write(response.content)
            print("Saved to test_output_filtered.mid")
        else:
            print(f"Conversion failed: {response.text}")

    finally:
        # Cleanup
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Removed {file_path}")

if __name__ == "__main__":
    try:
        test_api()
    except Exception as e:
        print(f"Test execution failed: {e}")
