from pathlib import Path
import json
import xml.etree.ElementTree as ET

BASE = Path(__file__).resolve().parent.parent
REZEPT = BASE / "rezepte"
OUTPUT = BASE / "rezepte.json"


def xml_text(root, tag):
    element = root.find(tag)
    if element is None:
        return ""
    parts = []
    if element.text:
        parts.append(element.text)
    for child in element:
        if child.tag.lower() == "br":
            parts.append("\n")
        else:
            parts.append("".join(child.itertext()))
        if child.tail:
            parts.append(child.tail)
    return "".join(parts).strip()


def format_html(text):
    return text.replace("\t", "&#9;").replace("\n", "<br>")

def read_movie(folder: Path):
    nfo_files = list(folder.glob("*.nfo"))
    if len(nfo_files) == 0:
        print(f"❌ {folder.name}: keine NFO gefunden")
        return None
    if len(nfo_files) > 1:
        print(f"❌ {folder.name}: mehrere NFO-Dateien gefunden")
        return None
    nfo = nfo_files[0]
    poster_files = list(folder.glob("poster.jpg"))

    if len(poster_files) > 1:
        print(f"⚠ {folder.name}: mehrere Poster gefunden")
    poster = poster_files[0] if poster_files else None
    
    try:
        root = ET.parse(nfo).getroot()
    except ET.ParseError:
        text = nfo.read_text(encoding="utf-8", errors="ignore")
    # HTML-Zeilenumbrüche in gültiges XML umwandeln
    text = text.replace("<br>", "<br />")
    try:
        root = ET.fromstring(text)
        print(f"⚠ {folder.name}: XML automatisch korrigiert")
    except ET.ParseError as e:
        print(f"❌ {folder.name}: XML-Fehler ({e})")
        return None

    movie = {
        "id": xml_text(root, "id"),
        "title": xml_text(root, "title"),
        "category": xml_text(root, "category"),
        "ingredients_1_header": xml_text(root, "ingredients_1_header"),
        "ingredients_1": format_html(xml_text(root, "ingredients_1")),
        "ingredients_2_header": xml_text(root, "ingredients_2_header"),
        "ingredients_2": format_html(xml_text(root, "ingredients_2")),
        "recipe_1_header": xml_text(root, "recipe_1_header"),
        "recipe_1": format_html(xml_text(root, "recipe_1")),
        "recipe_2_header": xml_text(root, "recipe_2_header"),
        "recipe_2": format_html(xml_text(root, "recipe_2")),
        "notes_header": xml_text(root, "notes_header"),
        "notes": format_html(xml_text(root, "notes")),
        "folder": folder.name,
        "filename": nfo.stem,
        "poster": (
            f"rezepte/{folder.name}/{poster.name}"
            if poster else ""
        ),
    }
    return movie

movies = []

folders = sorted(
    [folder for folder in REZEPT.iterdir() if folder.is_dir()],
    key=lambda folder: int(folder.name)
)

for folder in folders:
    movie = read_movie(folder)
    if not movie:
        continue
    if movie["id"] == "":
        print(f"❌ {folder.name}: keine ID gefunden")
        continue
    movies.append(movie)
movies.sort(key=lambda movie: int(movie["id"]))

json_text = json.dumps(
    movies,
    ensure_ascii=False,
    indent=4
)

if OUTPUT.exists():
    old_json = OUTPUT.read_text(encoding="utf-8")
    if old_json == json_text:
        print("✅ movies.json ist bereits aktuell.")
        raise SystemExit
OUTPUT.write_text(
    json_text,
    encoding="utf-8"
)

print()
print(f"✅ {len(movies)} Filme verarbeitet.")
print("💾 movies.json wurde aktualisiert.")