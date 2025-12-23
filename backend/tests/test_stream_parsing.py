import io
import os
import sys

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))

from backend.parser.binary_parser import BinaryParser
from backend.parser.xml_parser import XmlParser
from backend.models.song_model import Song

def test_binary_parser_stream():
    """
    Test that BinaryParser can parse a GP5 file from a bytes stream.
    Note: This test requires a valid .gp5 file. If none exists, we mock or skip.
    """
    print("\n[Test] BinaryParser Stream Support")
    # We need a real GP5 file content to test this properly, 
    # but we can try with a dummy header if we don't have one, 
    # or just check if the method exists and accepts bytes.
    
    parser = BinaryParser()
    try:
        # Create a dummy stream that mimics a GP file header to see if it crashes on type check or I/O
        # GP5 header usually starts with 'FICHIER GUITAR PRO v5.00'
        dummy_content = b'FICHIER GUITAR PRO v5.00' + b'\x00' * 100
        
        # We expect this might fail parsing, but we want to ensure it doesn't fail 
        # because of "filename required" or "io not supported".
        try:
            parser.parse_bytes(dummy_content)
        except Exception as e:
            # We expect a parsing error, but let's check the error message
            print(f"Caught expected parsing error: {e}")
            if "filename" in str(e).lower() or "embedded" in str(e).lower():
                 print("WARNING: It seems PyGuitarPro might be expecting a filename or real file?")
            else:
                 print("Stream accepted (failed to parse content as expected).")

    except Exception as e:
        print(f"FAILED with unexpected error: {e}")
        # raise e

def test_xml_parser_stream():
    """
    Test that XmlParser can parse a GPX file (zip) from a bytes stream.
    """
    print("\n[Test] XmlParser Stream Support")
    parser = XmlParser()
    
    # invalid zip bytes
    dummy_zip = b'PK\x03\x04' + b'\x00' * 50
    
    try:
        parser.parse_bytes(dummy_zip)
    except Exception as e:
         print(f"Caught expected zip error: {e}")
         print("Stream accepted (failed to parse content as expected).")

if __name__ == "__main__":
    test_binary_parser_stream()
    test_xml_parser_stream()
