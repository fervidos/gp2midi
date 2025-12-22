import os
import sys

# Adjust path to find modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from parser.xml_parser import XmlParser

from converter.midi_writer import MidiWriter


def convert(input_path, output_path):
    print(f"Converting '{input_path}' to '{output_path}'...")

    with open(input_path, "rb") as f:
        content = f.read()

    parser = XmlParser()
    try:
        song = parser.parse_bytes(content)
        print(f"Parsed Song: {song.title} by {song.artist}")
        print(f"Tracks: {len(song.tracks)}")

        # Use Standard Fidelity to ensure all tracks fit
        writer = MidiWriter(song, high_fidelity=False)
        writer.write(output_path)
        print("Conversion successful.")

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    input_file = (
        r"c:\Users\sales\Downloads\Code Stuff\gp2midi"
        r"\My Bloody Valentine-When You Sleep-11-06-2025.gp"
    )
    output_file = (
        r"c:\Users\sales\Downloads\Code Stuff\gp2midi"
        r"\My Bloody Valentine-When You Sleep-11-06-2025(Standard).mid"
    )
    convert(input_file, output_file)
