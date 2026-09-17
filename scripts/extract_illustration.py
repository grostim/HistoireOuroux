#!/usr/bin/env python3
"""Extrait une illustration du fac-similé à sa résolution native.

Le fac-similé contient une image CCITT par page : les illustrations imprimées
font partie de cette image de page et ne peuvent pas être isolées par pdfimages.
On les recadre depuis le rendu de la page à 280 ppp, ce qui conserve exactement
la résolution du document (aucun sur-échantillonnage).

Usage :
    python3 scripts/extract_illustration.py <vue> <x> <y> <w> <h> <nom>
Coordonnées en pixels du rendu à 280 ppp (origine en haut à gauche).
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
PAGES = ROOT / "Originaux" / "Pages"
OUT = ROOT / "Illustrations"


def main() -> int:
    if len(sys.argv) != 7:
        print(__doc__)
        return 1
    vue, x, y, w, h = (int(a) for a in sys.argv[1:6])
    nom = sys.argv[6]

    src = PAGES / f"Page-{vue:03d}.png"
    if not src.exists():
        print(f"vue {vue} : image absente ({src})")
        return 1

    OUT.mkdir(parents=True, exist_ok=True)
    dst = OUT / f"{nom}.png"

    with Image.open(src) as im:
        box = (x, y, x + w, y + h)
        if box[2] > im.width or box[3] > im.height:
            print(f"ERREUR: recadrage {box} hors de l'image ({im.width}x{im.height})")
            return 1
        crop = im.crop(box)
        # PNG en niveaux de gris 1 bit : conserve exactement les pixels du scan
        crop.save(dst, "PNG", optimize=True)

    with Image.open(dst) as v:
        print(f"ECRIT: {dst.name}  {v.width}x{v.height} px  {dst.stat().st_size} octets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
