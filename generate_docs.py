"""Generate HTML documentation using pydoc."""

from importlib import import_module
import os
import pydoc

MODULES = [
    "app",
    "app.models",
    "app.routes.restaurants",
    "app.routes.reservations",
    "app.schemas",
    "app.extensions",
    "app.error_handlers",
    "config",
    "manage",
]

def main() -> None:
    os.makedirs("docs", exist_ok=True)
    doc = pydoc.HTMLDoc()
    for mod_name in MODULES:
        module = import_module(mod_name)
        html = doc.page(pydoc.describe(module), doc.document(module))
        fname = os.path.join("docs", f"{mod_name.replace('.', '_')}.html")
        with open(fname, "w", encoding="utf-8") as fh:
            fh.write(html)
        print(f"Generated {fname}")

if __name__ == "__main__":
    main()