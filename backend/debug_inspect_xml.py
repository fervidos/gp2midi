import zipfile
import io
import xml.etree.ElementTree as ET

def inspect_xml(file_path):
    with zipfile.ZipFile(file_path) as z:
        print(f"Files in zip: {z.namelist()}")
        score_file = 'score.gpif'
        if 'Content/score.gpif' in z.namelist():
             score_file = 'Content/score.gpif'
             
        if score_file in z.namelist():
            with z.open(score_file) as f:
                tree = ET.parse(f)
                root = tree.getroot()
                
                # Check Namespace
                print(f"Root tag: {root.tag}")
                ns_match = root.tag.split('}')
                ns = ''
                if len(ns_match) > 1:
                    ns = ns_match[0] + '}'
                print(f"Detected Namespace: {ns}")

                # List all Track IDs
                tracks = root.findall(f".//{ns}Track")
                print(f"Total Track elements: {len(tracks)}")
                for t in tracks:
                    print(f"Track Element ID: {t.get('id')}, Name: {t.findtext(f'{ns}Name')}")

if __name__ == "__main__":
    inspect_xml(r"c:\Users\sales\Downloads\Code Stuff\gp2midi\My Bloody Valentine-When You Sleep-11-06-2025.gp")
