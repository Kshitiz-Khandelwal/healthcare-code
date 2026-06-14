import json, os

nb_dir = r"c:\Users\Admin\Desktop\Kshitiz\healthcare project\healthcare project\notebooks"

for f in sorted(os.listdir(nb_dir)):
    if not f.endswith(".ipynb"):
        continue
    path = os.path.join(nb_dir, f)
    size_kb = os.path.getsize(path) // 1024
    with open(path, encoding="utf-8") as fh:
        nb = json.load(fh)
    cells = nb.get("cells", [])
    total = len(cells)
    with_output = sum(1 for c in cells if c.get("outputs"))
    has_images = sum(1 for c in cells for o in c.get("outputs", []) if "image/png" in o.get("data", {}))
    print(f"{f:55s} {size_kb:>6} KB | cells={total:>3} | with_output={with_output:>3} | images={has_images:>3}")
