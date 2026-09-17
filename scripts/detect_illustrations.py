#!/usr/bin/env python3
"""Détecte les régions d'illustration dans une vue (bandes d'encre dense).

Le texte imprimé produit des lignes d'encre alternées (dense/creux régulier),
tandis qu'un dessin produit une bande d'encre dense et continue sur une grande
hauteur. On exploite cette différence pour proposer des cadrages candidats.

Usage :
    python3 scripts/detect_illustrations.py <vue> [<vue> ...]
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
PAGES = ROOT / "Originaux" / "Pages"

MARGE = 150          # bord de scan ignoré
SEUIL_ENCRE = 140    # valeur de gris sous laquelle un pixel est de l'encre


def analyser(vue: int) -> None:
    src = PAGES / f"Page-{vue:03d}.png"
    if not src.exists():
        print(f"vue {vue} : absente")
        return
    with Image.open(src) as im:
        a = np.array(im.convert("L"))

    h, w = a.shape
    # zone utile : on retire les bords de scan
    zone = a[MARGE:h - MARGE, MARGE:w - MARGE]
    encre = (zone < SEUIL_ENCRE)

    # profil de densité par ligne
    densite = encre.mean(axis=1)
    lignes = encre.sum(axis=1)

    # une ligne d'illustration a une densité nettement supérieure à une ligne de texte
    seuil = 0.12
    mask = densite > seuil

    bandes: list[tuple[int, int]] = []
    debut = None
    for i, m in enumerate(mask):
        if m and debut is None:
            debut = i
        elif not m and debut is not None:
            if i - debut >= 60:          # hauteur minimale d'un dessin
                bandes.append((debut, i))
            debut = None
    if debut is not None and len(mask) - debut >= 60:
        bandes.append((debut, len(mask)))

    print(f"=== vue {vue} ({w}x{h}) : {len(bandes)} bande(s) candidate(s)")
    for y0, y1 in bandes:
        sous = encre[y0:y1]
        cols = sous.sum(axis=0)
        ci = [i for i, v in enumerate(cols) if v > 2]
        if not ci:
            continue
        x0, x1 = ci[0], ci[-1]
        print(f"    y {y0 + MARGE:5d} -> {y1 + MARGE:5d}  "
              f"x {x0 + MARGE:5d} -> {x1 + MARGE:5d}  "
              f"({x1 - x0}x{y1 - y0} px)  densite={densite[y0:y1].mean():.2f}")


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    for v in sys.argv[1:]:
        analyser(int(v))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
