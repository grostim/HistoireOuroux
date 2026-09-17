#!/usr/bin/env python3
"""Localise un texte dans une vue du fac-similé et retourne ses coordonnées en pixels.

Utilise la couche OCR du PDF (pdftotext -bbox), dont les coordonnées sont en
points PDF, et les convertit en pixels du rendu PNG à 280 ppp. Cela évite de
deviner les cadrages à l'œil pour extraire les illustrations.

Usage :
    python3 scripts/find_text.py <vue> "phrase recherchée" [contexte]
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PDF = ROOT / "Originaux" / "Histoire d'Ouroux.pdf"
PAGES = ROOT / "Originaux" / "Pages"

# Le rendu PNG est fait à 280 ppp ; les points PDF sont à 72 ppp.
SCALE = 280 / 72


def bbox_page(vue: int) -> tuple[list[dict], float]:
    """Retourne (mots avec coordonnées, hauteur de page en points)."""
    html = subprocess.run(
        ["pdftotext", "-bbox", "-f", str(vue), "-l", str(vue), str(PDF), "-"],
        capture_output=True, text=True,
    ).stdout
    mots = []
    for m in re.finditer(
        r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">([^<]*)</word>',
        html,
    ):
        x0, y0, x1, y1, txt = m.groups()
        mots.append({
            "x0": float(x0), "y0": float(y0),
            "x1": float(x1), "y1": float(y1),
            "t": txt,
        })
    hauteur = 0.0
    mh = re.search(r'<page width="[\d.]+" height="([\d.]+)"', html)
    if mh:
        hauteur = float(mh.group(1))
    return mots, hauteur


def normalise(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^a-z0-9à-ÿ]+", "", s)
    return s


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 1
    vue = int(sys.argv[1])
    cible = normalise(" ".join(sys.argv[2:]))

    mots, _ = bbox_page(vue)
    if not mots:
        print(f"vue {vue} : aucune couche OCR exploitable")
        return 1

    # recherche de la suite de mots correspondant à la cible
    for i in range(len(mots)):
        acc, j = "", i
        while j < len(mots) and len(acc) < len(cible):
            acc += normalise(mots[j]["t"])
            j += 1
        if acc.startswith(cible):
            bloc = mots[i:j]
            x0 = min(w["x0"] for w in bloc) * SCALE
            y0 = min(w["y0"] for w in bloc) * SCALE
            x1 = max(w["x1"] for w in bloc) * SCALE
            y1 = max(w["y1"] for w in bloc) * SCALE
            print(f"vue {vue} : localisé ligne {i}")
            print(f"  pixels  : x {int(x0)} -> {int(x1)} | y {int(y0)} -> {int(y1)}")
            print(f"  largeur {int(x1-x0)} | hauteur {int(y1-y0)}")
            return 0

    print(f"vue {vue} : texte non trouvé dans la couche OCR")
    # lister les lignes pour aider
    lignes: dict[float, list[str]] = {}
    for w in mots:
        lignes.setdefault(round(w["y0"]), []).append(w["t"])
    print("  début de la page :")
    for y in sorted(lignes)[:6]:
        print(f"    y={int(y*SCALE):5d} : {' '.join(lignes[y])[:70]}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
