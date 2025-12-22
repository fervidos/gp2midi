import unittest
import xml.etree.ElementTree as ET
import zipfile
import io
from parser.xml_parser import XmlParser

class TestXmlParserNamespaces(unittest.TestCase):
    def test_parse_namespaced_xml(self):
        # Create XML with default namespace
        NS = "http://www.guitar-pro.com/GPIF/1.0"
        ET.register_namespace('', NS)
        
        root = ET.Element(f'{{{NS}}}GPIF')
        
        # Rhythms
        rhythms = ET.SubElement(root, f'{{{NS}}}Rhythms')
        r_q = ET.SubElement(rhythms, f'{{{NS}}}Rhythm', id='0')
        n_val = ET.SubElement(r_q, f'{{{NS}}}NoteValue')
        n_val.text = 'Quarter'
        
        # MasterTrack
        mt = ET.SubElement(root, f'{{{NS}}}MasterTrack')
        trks = ET.SubElement(mt, f'{{{NS}}}Tracks')
        trks.text = '0'
        
        # Tracks
        tracks_elem = ET.SubElement(root, f'{{{NS}}}Tracks')
        t0 = ET.SubElement(tracks_elem, f'{{{NS}}}Track', id='0')
        nam = ET.SubElement(t0, f'{{{NS}}}Name')
        nam.text = 'NS Guitar'
        
        # MasterBars
        mbs = ET.SubElement(root, f'{{{NS}}}MasterBars')
        mb0 = ET.SubElement(mbs, f'{{{NS}}}MasterBar')
        time = ET.SubElement(mb0, f'{{{NS}}}Time')
        time.text = '4/4'
        bars_node = ET.SubElement(mb0, f'{{{NS}}}Bars')
        bars_node.text = '100'
        
        # Bars
        bars = ET.SubElement(root, f'{{{NS}}}Bars')
        b100 = ET.SubElement(bars, f'{{{NS}}}Bar', id='100')
        voices_node = ET.SubElement(b100, f'{{{NS}}}Voices')
        voices_node.text = '200'
        
        # Voices
        voices = ET.SubElement(root, f'{{{NS}}}Voices')
        v200 = ET.SubElement(voices, f'{{{NS}}}Voice', id='200')
        beats_node = ET.SubElement(v200, f'{{{NS}}}Beats')
        beats_node.text = '300'
        
        # Beats
        beats = ET.SubElement(root, f'{{{NS}}}Beats')
        bt300 = ET.SubElement(beats, f'{{{NS}}}Beat', id='300')
        rh_ref = ET.SubElement(bt300, f'{{{NS}}}Rhythm', ref='0')
        notes_node = ET.SubElement(bt300, f'{{{NS}}}Notes')
        notes_node.text = '400'
        
        # Notes
        notes = ET.SubElement(root, f'{{{NS}}}Notes')
        n400 = ET.SubElement(notes, f'{{{NS}}}Note', id='400')
        props = ET.SubElement(n400, f'{{{NS}}}Properties')
        p_midi = ET.SubElement(props, f'{{{NS}}}Property', name='Midi')
        midi_num = ET.SubElement(p_midi, f'{{{NS}}}Number')
        midi_num.text = '60'
        
        # Parse
        bio = io.BytesIO()
        with zipfile.ZipFile(bio, 'w') as z:
            xml_str = ET.tostring(root, encoding='utf-8')
            z.writestr('score.gpif', xml_str)
            
        parser = XmlParser()
        song = parser.parse_bytes(bio.getvalue())
        
        self.assertEqual(len(song.tracks), 1)
        self.assertEqual(song.tracks[0].name, 'NS Guitar')
        self.assertEqual(len(song.tracks[0].measures), 1)
        beat = song.tracks[0].measures[0].beats[0]
        self.assertEqual(len(beat.notes), 1)
        self.assertEqual(beat.notes[0].midi_number, 60)

if __name__ == '__main__':
    unittest.main()
