import sys
import xml.etree.ElementTree as ET
import zipfile


def inspect_gp(file_path):
    print(f"Inspecting {file_path}")
    try:
        with zipfile.ZipFile(file_path, "r") as z:
            print("Files in archive:", z.namelist())

            score_file = None
            if "score.gpif" in z.namelist():
                score_file = "score.gpif"
            elif "Content/score.gpif" in z.namelist():
                score_file = "Content/score.gpif"

            if not score_file:
                print("score.gpif not found!")
                return

            with z.open(score_file) as f:
                content = f.read()
                # Parse XML
                root = ET.fromstring(content)

                # Write formatted XML snippet to file
                with open("debug_xml_structure.txt", "w", encoding="utf-8") as out:
                    # Generic dump of structure (tags and attributes)
                    # not full content to avoid huge files
                    dump_structure(root, out)

    except Exception as e:
        print(f"Error: {e}")


def dump_structure(elem, f, level=0):
    indent = "  " * level
    # Print tag and attributes
    attrs = " ".join(f'{k}="{v}"' for k, v in elem.attrib.items())
    text = (elem.text or "").strip()
    short_text = text[:50] + "..." if len(text) > 50 else text

    f.write(f"{indent}<{elem.tag} {attrs}")
    if short_text:
        f.write(f"> {short_text}\n")
    else:
        f.write(">\n")

    # Recurse children (limit depth or count if needed)
    for child in elem:
        dump_structure(child, f, level + 1)


if __name__ == "__main__":
    target = (
        r"c:\Users\sales\Downloads\Code Stuff\gp2midi"
        r"\My Bloody Valentine-When You Sleep-11-06-2025.gp"
    )
    if len(sys.argv) > 1:
        target = sys.argv[1]
    inspect_gp(target)
