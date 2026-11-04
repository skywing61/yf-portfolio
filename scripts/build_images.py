"""Build the site's WebP images from the PNG sources in images-src/.

Each images-src/<name>.png (or .jpg) is the finished image, already cropped to
the framing the page shows (16:10 for project images). The script never moves,
pads or crops it; it only converts it and makes the smaller srcset copies:

  assets/images/<name>.webp        full size, at most 1920 px wide
  assets/images/<name>-<w>.webp    one per width the HTML asks for in srcset
                                   (480 / 800 / 1200 when nothing asks yet)

images-src/.build-state.json remembers a fingerprint of each PNG that was built.
An image is rebuilt only when its PNG content changes (file dates are not used,
because copying a file on Windows keeps its old date), so re-running is cheap.

  python scripts/build_images.py           build what changed
  python scripts/build_images.py --force   rebuild everything
  python scripts/build_images.py --check   only report problems, write nothing
  python scripts/build_images.py NAME ...  build only these images
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "images-src"
OUT = ROOT / "assets" / "images"
SOURCE_EXTS = (".png", ".jpg", ".jpeg")
MAX_WIDTH = 1920
DEFAULT_WIDTHS = (480, 800, 1200)
QUALITY_FULL = 90
QUALITY_SMALL = 85
STATE = SRC / ".build-state.json"

REF = re.compile(r"assets/images/([A-Za-z0-9_.-]+)")
VARIANT = re.compile(r"^(.+)-(\d+)\.webp$")


def page_files():
    return [p for p in ROOT.rglob("*") if p.suffix in (".html", ".css", ".js")
            and "images-src" not in p.parts and "scripts" not in p.parts]


def referenced_names():
    names = set()
    for page in page_files():
        names.update(REF.findall(page.read_text(encoding="utf-8")))
    return names


def sources():
    return {p.stem: p for p in sorted(SRC.iterdir())
            if p.is_file() and p.suffix.lower() in SOURCE_EXTS}


def widths_for(name, refs):
    widths = sorted({int(m.group(2)) for r in refs
                     if (m := VARIANT.match(r)) and m.group(1) == name})
    return widths or list(DEFAULT_WIDTHS)


def fingerprint(path):
    return hashlib.sha1(path.read_bytes()).hexdigest()


def load_state():
    return json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else {}


def save_state(state):
    STATE.write_text(json.dumps(state, indent=1, sort_keys=True) + "\n", encoding="utf-8")


def is_stale(entry, sha, outputs):
    return (entry is None or entry["sha1"] != sha or entry["outputs"] != outputs
            or not all((OUT / o).exists() for o in outputs))


def save(im, width, path, quality):
    if im.width > width:
        im = im.resize((width, round(im.height * width / im.width)), Image.Resampling.LANCZOS)
    im.save(path, "WEBP", quality=quality, method=6)


def build(force, only=()):
    refs = referenced_names()
    state = load_state()
    built = 0
    for name, src in sources().items():
        if only and name not in only:
            continue
        targets = [(OUT / f"{name}.webp", MAX_WIDTH, QUALITY_FULL)]
        targets += [(OUT / f"{name}-{w}.webp", w, QUALITY_SMALL) for w in widths_for(name, refs)]
        outputs = [t[0].name for t in targets]
        sha = fingerprint(src)
        if not force and not is_stale(state.get(name), sha, outputs):
            continue
        with Image.open(src) as im:
            im.load()
            if im.mode not in ("RGB", "RGBA"):
                im = im.convert("RGBA" if "A" in im.getbands() else "RGB")
            for path, width, quality in targets:
                save(im, width, path, quality)
                print(f"  {path.name}  ({min(width, im.width)} px)")
                built += 1
        state[name] = {"sha1": sha, "outputs": outputs}
        save_state(state)
    print(f"Built {built} file(s).")


def check():
    problems = 0
    refs = referenced_names()
    srcs = sources()
    state = load_state()
    pending = []
    for name, src in srcs.items():
        outputs = [f"{name}.webp"] + [f"{name}-{w}.webp" for w in widths_for(name, refs)]
        if is_stale(state.get(name), fingerprint(src), outputs):
            pending.append(src.name)
    if pending:
        print("PNG changed since the last build (run the script without --check):")
        for n in pending:
            print(f"  {n}")
    existing = {p.name for p in OUT.iterdir() if p.is_file()}

    missing = sorted(r for r in refs if r not in existing)
    if missing:
        problems += len(missing)
        print("Used by a page but missing from assets/images:")
        for r in missing:
            stem = VARIANT.match(r).group(1) if VARIANT.match(r) else Path(r).stem
            hint = "" if stem in srcs else f"  (add images-src/{stem}.png)"
            print(f"  {r}{hint}")

    def base(n):
        m = VARIANT.match(n)
        return m.group(1) if m else Path(n).stem

    no_source = sorted(n for n in refs if n.endswith(".webp") and base(n) not in srcs)
    if no_source:
        problems += len(no_source)
        print("Used by a page but has no PNG in images-src (cannot be rebuilt):")
        for n in no_source:
            print(f"  {n}")

    unused = sorted(n for n in existing if n not in refs)
    if unused:
        print("In assets/images but not used by any page (safe to delete):")
        for n in unused:
            print(f"  {n}")

    unused_src = sorted(s for s in srcs if not any(base(r) == s for r in refs))
    if unused_src:
        print("PNG in images-src that no page uses yet:")
        for s in unused_src:
            print(f"  {srcs[s].name}")

    odd = []
    for name, src in srcs.items():
        with Image.open(src) as im:
            if abs(im.width / im.height - 1.6) > 0.01:
                odd.append(f"  {src.name}  {im.width} x {im.height}")
    if odd:
        print("Not 16:10 (fine only if the page is meant to show another ratio):")
        print("\n".join(odd))

    print("No problems." if not problems else f"{problems} problem(s).")
    return problems


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--force", action="store_true", help="rebuild every output")
    parser.add_argument("names", nargs="*", help="build only these images (file name without .png)")
    parser.add_argument("--check", action="store_true", help="report problems without writing")
    args = parser.parse_args()
    if not SRC.is_dir():
        sys.exit(f"Missing source folder: {SRC}")
    if args.check:
        sys.exit(1 if check() else 0)
    unknown = [n for n in args.names if n not in sources()]
    if unknown:
        sys.exit(f"No PNG in images-src for: {', '.join(unknown)}")
    build(args.force, set(args.names))
    check()


if __name__ == "__main__":
    main()
