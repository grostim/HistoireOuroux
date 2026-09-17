#!/usr/bin/env python3
"""Contrôle un cadrage d'illustration extrait du fac-similé.

Trois vérifications, dans cet ordre :

1. **Fidélité** : le fichier de ``Illustrations/`` doit être exactement le
   rectangle annoncé du rendu de la vue à 280 ppp (aucun ré-échantillonnage,
   aucune recompression).
2. **Bord** (option ``--bord``) : aucun pixel d'encre ne doit toucher un bord
   de l'image — un sujet qui touche le bord est un sujet rogné. Les marges de
   l'original sont inégales : ne pas activer sans avoir vérifié le cadrage.
3. **Vignette circulaire** (option ``--cercle``) : lorsqu'un motif circulaire
   encadre le dessin, l'arc doit être couvert sur 360°. Couverture partielle =
   motif coupé. Le contour extérieur est relevé par balayage radial au degré
   depuis le centroïde de l'encre, puis le cercle est ajusté sur ces points :
   un ajustement sur les seules transitions ligne à ligne se laisse biaiser
   par le dessin intérieur et déclare des secteurs manquants qui n'existent pas.

Usage :
    python3 scripts/check_illustration.py <vue> <x> <y> <w> <h> <nom> [--bord] [--cercle]
Exemple (vignette de couverture) :
    python3 scripts/check_illustration.py 5 830 1727 698 698 illus-00-couverture-clocher --cercle
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
PAGES = ROOT / "Originaux" / "Pages"
ILLUS = ROOT / "Illustrations"

SEUIL_ENCRE = 128
TOLERANCE_ARC = 6   # px : distance au rayon dans laquelle un pixel compte sur l'arc
PAS_SECTEUR = 5     # degrés par secteur


def _ajuster_cercle(points: np.ndarray) -> tuple[float, float, float]:
    """Ajustement algébrique (Kåsa) du cercle au plus près des points."""
    x, y = points[:, 0], points[:, 1]
    a = np.column_stack([x, y, np.ones(len(x))])
    d, e, f = np.linalg.lstsq(a, -(x**2 + y**2), rcond=None)[0]
    cx, cy = -d / 2, -e / 2
    return cx, cy, float(np.sqrt(cx**2 + cy**2 - f))


def _arc(encre: np.ndarray) -> tuple[np.ndarray, float, float, float, int]:
    """Secteurs couverts par le contour circulaire extérieur, et le cercle ajusté.

    Le contour extérieur est le pixel d'encre le plus éloigné du centroïde dans
    chaque direction (1°). L'ajustement écarte ensuite les points aberrants
    (antennes, texte débordant) par passes successives.
    """
    ys, xs = np.nonzero(encre)
    cxm, cym = xs.mean(), ys.mean()
    rad = np.hypot(xs - cxm, ys - cym)
    ang = (np.degrees(np.arctan2(ys - cym, xs - cxm)).astype(int)) % 360

    extremes: dict[int, tuple[float, float, float]] = {}
    for a, r, x, y in zip(ang, rad, xs, ys):
        if r > extremes.get(a, (-1.0, 0, 0))[0]:
            extremes[a] = (r, float(x), float(y))
    points = np.array([(v[1], v[2]) for v in extremes.values()], dtype=float)
    directions = len(extremes)

    residu_max = float("nan")
    cx = cy = r = 0.0
    for passe in range(8):
        cx, cy, r = _ajuster_cercle(points)
        residu = np.abs(np.hypot(points[:, 0] - cx, points[:, 1] - cy) - r)
        keep = residu < max(2.0, 10.0 - passe)
        points = points[keep]
        residu_max = float(residu[keep].max()) if keep.any() else float("nan")

    angs = np.degrees(np.arctan2(ys - cy, xs - cx)) % 360
    rads = np.hypot(xs - cx, ys - cy)
    sur_arc = (angs[np.abs(rads - r) < TOLERANCE_ARC] // PAS_SECTEUR).astype(int)
    secteurs = np.zeros(360 // PAS_SECTEUR, dtype=bool)
    secteurs[sur_arc % len(secteurs)] = True
    return secteurs, cx, cy, r, directions


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    options = {a for a in sys.argv[1:] if a.startswith("--")}
    if len(args) != 6:
        print(__doc__)
        return 2

    vue, x, y, w, h = (int(v) for v in args[:5])
    nom = args[5]

    src = PAGES / f"Page-{vue:03d}.png"
    dst = ILLUS / f"{nom}.png"
    for chemin, quoi in ((src, "vue"), (dst, "illustration")):
        if not chemin.exists():
            print(f"ECHEC: {quoi} introuvable ({chemin})")
            return 1

    with Image.open(src) as im:
        page = np.array(im.convert("L"))
    with Image.open(dst) as im:
        illus = np.array(im.convert("L"))

    echecs: list[str] = []

    # 1. Fidélité au scan
    if (w, h) != (illus.shape[1], illus.shape[0]):
        echecs.append(
            f"taille annoncée {w}x{h} != fichier {illus.shape[1]}x{illus.shape[0]}"
        )
    attendu = page[y:y + illus.shape[0], x:x + illus.shape[1]]
    if attendu.shape != illus.shape:
        echecs.append("cadrage hors de la vue")
    elif not np.array_equal(attendu, illus):
        diff = int((attendu != illus).sum())
        echecs.append(f"{diff} pixel(s) différent(s) du scan (re-échantillonnage ?)")
    else:
        print(f"OK  fidélité : {dst.name} = vue {vue:03d} "
              f"[x {x}..{x+w-1}, y {y}..{y+h-1}]")

    encre = illus < SEUIL_ENCRE

    # 2. Encre au bord = sujet rogné
    if "--bord" in options:
        bords = {
            "haut": int(encre[0].sum()),
            "bas": int(encre[-1].sum()),
            "gauche": int(encre[:, 0].sum()),
            "droite": int(encre[:, -1].sum()),
        }
        touches = {k: v for k, v in bords.items() if v}
        if touches:
            echecs.append(f"encre sur le bord ({touches}) : sujet rogné")
        else:
            print("OK  bord : aucun pixel d'encre sur les bords")

    # 3. Vignette circulaire complète
    if "--cercle" in options:
        secteurs, cx, cy, r, directions = _arc(encre)
        degres = int(secteurs.sum()) * PAS_SECTEUR
        print(f"    cercle du contour extérieur : centre ({cx:.1f}, {cy:.1f}), "
              f"rayon {r:.1f} px sur {directions} directions")
        print(f"    bbox : x {cx-r:.0f}..{cx+r:.0f}  y {cy-r:.0f}..{cy+r:.0f}  "
              f"(image {illus.shape[1]}x{illus.shape[0]})")
        if degres < 360:
            manquants = [int(i) * PAS_SECTEUR for i in np.nonzero(~secteurs)[0]]
            echecs.append(
                f"arc circulaire couvert sur {degres}°/360° "
                f"(secteurs manquants : {manquants[:8]}...) : le motif est coupé"
            )
        else:
            print("OK  cercle : arc complet 360°/360°")

    for e in echecs:
        print(f"ECHEC: {e}")
    return 1 if echecs else 0


if __name__ == "__main__":
    raise SystemExit(main())
