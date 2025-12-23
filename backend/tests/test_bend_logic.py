import unittest
import sys
import os
import io
import xml.etree.ElementTree as ET
import zipfile
import mido

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))

from backend.core.parser.xml_parser import XmlParser
from backend.core.converter.midi_writer import MidiWriter
from backend.models.song_model import EffectType

class TestBendLogic(unittest.TestCase):
    def test_bend_parsing_and_writing(self):
        # 1. Construct Mock XML
        NS = "http://www.guitar-pro.com/GPIF/1.0"
        ET.register_namespace("", NS)
        
        root = ET.Element(f"{{{NS}}}GPIF")
        
        # Skeleton structure
        rhythms = ET.SubElement(root, f"{{{NS}}}Rhythms")
        r_q = ET.SubElement(rhythms, f"{{{NS}}}Rhythm", id="0")
        ET.SubElement(r_q, f"{{{NS}}}NoteValue").text = "Quarter"
        
        mt = ET.SubElement(root, f"{{{NS}}}MasterTrack")
        ET.SubElement(mt, f"{{{NS}}}Tracks").text = "0"
        
        tracks = ET.SubElement(root, f"{{{NS}}}Tracks")
        t0 = ET.SubElement(tracks, f"{{{NS}}}Track", id="0")
        ET.SubElement(t0, f"{{{NS}}}Name").text = "Guitar"
        
        mbs = ET.SubElement(root, f"{{{NS}}}MasterBars")
        mb0 = ET.SubElement(mbs, f"{{{NS}}}MasterBar")
        ET.SubElement(mb0, f"{{{NS}}}Time").text = "4/4"
        ET.SubElement(mb0, f"{{{NS}}}Bars").text = "1"
        
        bars = ET.SubElement(root, f"{{{NS}}}Bars")
        b1 = ET.SubElement(bars, f"{{{NS}}}Bar", id="1")
        ET.SubElement(b1, f"{{{NS}}}Voices").text = "1"
        
        voices = ET.SubElement(root, f"{{{NS}}}Voices")
        v1 = ET.SubElement(voices, f"{{{NS}}}Voice", id="1")
        ET.SubElement(v1, f"{{{NS}}}Beats").text = "1"
        
        beats = ET.SubElement(root, f"{{{NS}}}Beats")
        bt1 = ET.SubElement(beats, f"{{{NS}}}Beat", id="1")
        ET.SubElement(bt1, f"{{{NS}}}Rhythm", ref="0") # Quarter note = 960 ticks
        ET.SubElement(bt1, f"{{{NS}}}Notes").text = "1"
        
        # Note with Bend
        notes = ET.SubElement(root, f"{{{NS}}}Notes")
        n1 = ET.SubElement(notes, f"{{{NS}}}Note", id="1")
        props = ET.SubElement(n1, f"{{{NS}}}Properties")
        
        # MIDI Number
        p_midi = ET.SubElement(props, f"{{{NS}}}Property", name="Midi")
        ET.SubElement(p_midi, f"{{{NS}}}Number").text = "60"
        
        # BEND Property
        p_bends = ET.SubElement(props, f"{{{NS}}}Property", name="Bends")
        pt1 = ET.SubElement(p_bends, f"{{{NS}}}Point")
        ET.SubElement(pt1, f"{{{NS}}}Position").text = "0"
        ET.SubElement(pt1, f"{{{NS}}}Value").text = "0"
        
        pt2 = ET.SubElement(p_bends, f"{{{NS}}}Point")
        ET.SubElement(pt2, f"{{{NS}}}Position").text = "50"
        ET.SubElement(pt2, f"{{{NS}}}Value").text = "50" # 1/2 tone = 1 semitone
        
        pt3 = ET.SubElement(p_bends, f"{{{NS}}}Point")
        ET.SubElement(pt3, f"{{{NS}}}Position").text = "100"
        ET.SubElement(pt3, f"{{{NS}}}Value").text = "100" # 1 tone = 2 semitones
        
        # Create Zip
        bio = io.BytesIO()
        with zipfile.ZipFile(bio, "w") as z:
            xml_str = ET.tostring(root, encoding="utf-8")
            z.writestr("score.gpif", xml_str)
            
        # 2. Parse
        parser = XmlParser()
        song = parser.parse_bytes(bio.getvalue())
        
        # Verify Model
        self.assertEqual(len(song.tracks[0].measures[0].beats[0].notes), 1)
        note = song.tracks[0].measures[0].beats[0].notes[0]
        self.assertTrue(any(e.type == EffectType.BEND for e in note.effects))
        bend_effect = next(e for e in note.effects if e.type == EffectType.BEND)
        self.assertEqual(len(bend_effect.bend_points), 3)
        self.assertEqual(bend_effect.bend_points[2].value, 100)
        
        # 3. Write MIDI
        writer = MidiWriter(song)
        # We need check output. Writer doesn't return object easily unless we check internal midi_file
        # but the `write` method populates `self.midi_file`
        
        # We can simulate write by calling _process_track directly or just writer method that saves to bio
        # But `midi_writer.py` implementation of `write` populates `self.midi_file`
        
        track = song.tracks[0]
        midi_track = writer._process_track(track)
        
        # Check Events
        # Filter pitchwheel
        pw_events = [e for e in midi_track if e.type == "pitchwheel"]
        
        self.assertTrue(len(pw_events) > 3) # Should have interpolated points
        
        # Start (Time 0) -> Val 0 -> Pitch 0 (Center)
        start_ev = pw_events[0]
        self.assertEqual(start_ev.time, 0)
        self.assertEqual(start_ev.pitch, 0)
        
        # Middle (Time ~480 ticks) -> Val 50 -> 1 Semitone
        # 1 Semitone = (1/12) * 8192 = 682. Pitch = 0 + 682 = 682
        # We should find an event around 480 ticks
        
        # Since we use delta times in final track, we need to inspect them carefully.
        # But `_process_track` returns a track with DELTA times.
        # So we need to sum deltas to get absolute time.
        
        abs_time = 0
        found_target = False
        for e in midi_track:
            abs_time += e.time
            if e.type == "pitchwheel":
                # Check near middle (480)
                if 470 <= abs_time <= 490:
                    # Should be around 682
                    if 600 <= e.pitch <= 750:
                        found_target = True
        
        self.assertTrue(found_target, "Did not find expected pitch bend at middle of note")
        
        # End (Time 960) -> Val 100 -> 2 Semitones
        # 2 Semitones = (2/12) * 8192 = 1365. Pitch = 0 + 1365 = 1365
         
        abs_time = 0
        found_end = False
        found_reset = False
        
        for e in midi_track:
            abs_time += e.time
            if e.type == "pitchwheel":
                if 950 <= abs_time <= 970:
                    if 1300 <= e.pitch <= 1400:
                        found_end = True
                    if e.pitch == 0 and abs_time >= 960: # Reset
                        found_reset = True
                        
        self.assertTrue(found_end, "Did not find expected max pitch bend")
        self.assertTrue(found_reset, "Did not find pitch bend reset")

if __name__ == "__main__":
    unittest.main()
