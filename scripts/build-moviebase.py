from pathlib import Path
import json
import xml.etree.ElementTree as ET

BASE = Path(__file__).resolve().parent.parent
MOVIES = BASE / "movies"
OUTPUT = BASE / "movies.json"

def xml_text(root, tag):
    element = root.find(tag)
    if element is None or element.text is None:
        return ""
    return element.text.strip()

def read_movie(folder: Path):
    nfo_files = list(folder.glob("*.nfo"))
    if len(nfo_files) == 0:
        print(f"❌ {folder.name}: keine NFO gefunden")
        return None
    if len(nfo_files) > 1:
        print(f"❌ {folder.name}: mehrere NFO-Dateien gefunden")
        return None
    nfo = nfo_files[0]
    poster_files = list(folder.glob("*-poster.jpg"))

    if len(poster_files) > 1:
        print(f"⚠ {folder.name}: mehrere Poster gefunden")
    poster = poster_files[0] if poster_files else None
    try:
        root = ET.parse(nfo).getroot()
    except ET.ParseError:
        text = nfo.read_text(encoding="utf-8", errors="ignore")
        text = text.replace("&", "&amp;")
        try:
            root = ET.fromstring(text)
            print(f"⚠ {folder.name}: '&' automatisch repariert")
        except Exception as e:
            print(f"❌ {folder.name}: XML-Fehler ({e})")
            return None
    movie = {
        "id": xml_text(root, "id"),
        "title": xml_text(root, "title"),
        "plot": xml_text(root, "plot"),
        "runtime": xml_text(root, "runtime"),
        "mpaa": xml_text(root, "mpaa"),
        "year": xml_text(root, "year"),
        "folder": folder.name,
        "filename": nfo.stem,
        "poster": (
            f"movies/{folder.name}/{poster.name}"
            if poster else ""
        ),
    }
    return movie

movies = []

folders = sorted(
    [folder for folder in MOVIES.iterdir() if folder.is_dir()],
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