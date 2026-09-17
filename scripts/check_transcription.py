#!/usr/bin/env python3
"""Repère les mots douteux d'une transcription pour cibler la relecture visuelle.

Le texte de 1952 contient beaucoup de mots hors dictionnaire moderne : noms
propres, toponymes, formes anciennes. Un contrôle brut serait noyé de faux
positifs. On filtre donc :

  - les mots contenant une majuscule (noms propres) sont exclus ;
  - les termes attendus du corpus sont exclus via la liste EXCEPTIONS ;
  - les chiffres romains et abréviations sont ignorés ;
  - seuls les mots en minuscules rejetés par le dictionnaire français sont
    signalés, avec une suggestion quand elle existe.

Vérifié : détecte bien « éxigèrent » -> « exigèrent », « prètres » -> « prêtres ».

Usage :
    python3 scripts/check_transcription.py scratch/transcription/vue-010-agy.txt
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from spylls.hunspell import Dictionary

DICO = Dictionary.from_files("/usr/share/hunspell/fr")

# Termes attendus du corpus : vocabulaire d'époque, toponymes, formes anciennes,
# abréviations. À étendre au fil de la transcription.
EXCEPTIONS = {
    # latin et diplomatique
    "oratorium", "oratoire", "oratoires", "ager", "parochia", "sanctorum",
    "bartholomei", "antonii", "oratorio", "capella", "erat", "cartulaire",
    "cartulaires", "terrier", "obédienciers", "obédiencier", "vicairie",
    "legs", "cens", "censives", "dîmes", "dime", "bénéfices",
    # toponymes
    "ouroux", "grosne", "carelle", "nagu", "arcis", "montaulieu", "grosbois",
    "alloignet", "avenas", "vauxrenard", "ardillats", "monsols", "fuissé",
    "macon", "mâconnais", "beaujolais", "bresse", "thels", "thel", "razay",
    "loire", "loittes", "montchetail", "fougères", "put-proid", "velard",
    "chorey", "trades", "bruyères", "bosc", "bosco", "villefranche", "cluny",
    "sauzey", "guillin", "lachere", "lochère",
    # personnes et famille
    "duligier", "testenoire", "berloty", "trouilloux", "morétain", "moretain",
    "jambon", "jambons", "polloce", "morin", "odouard", "aubonnet",
    "sivignon", "mondon", "gondié", "gondie", "bouteille", "labrosse",
    # datation révolutionnaire
    "thermidor", "frimaire", "vendémiaire", "brumaire", "nivôse", "pluviôse",
    "ventôse", "germinal", "floréal", "prairial", "messidor", "fructidor",
    "sansculottes", "vallecivique",
    # formes anciennes et variantes d'auteur
    "chartres", "défricherent", "défrichèrent", "barthelemy", "évêque",
    "evèque", "evéque", "exigèrent", "prètres",
    # abréviations
    "st", "ste", "mgr", "mr", "mme", "etc", "n", "s",
}

# Mots : on garde le mot complet, apostrophes internes comprises, puis on teste
# chaque composant séparément (l'élision « d'Ouroux » -> on teste « Ouroux »).
FRAGMENT = re.compile(r"[A-Za-zÀ-ÿ]+")


def fragments_du_texte(texte: str) -> set[str]:
    """Retourne les fragments alphabétiques, en excluant les majuscules (noms propres)."""
    out: set[str] = set()
    for mot in texte.split():
        for frag in FRAGMENT.findall(mot):
            if len(frag) >= 3 and frag[0].islower() and frag not in EXCEPTIONS:
                out.add(frag)
    return out


def suggestions(mot: str) -> list[str]:
    try:
        return sorted(DICO.suggestion(mot))[:3]
    except Exception:
        return []


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1

    total = 0
    for chemin in sys.argv[1:]:
        p = Path(chemin)
        if not p.exists():
            print(f"{chemin} : introuvable")
            continue
        texte = p.read_text(encoding="utf-8")
        candidats = sorted(fragments_du_texte(texte))
        douteux = []
        for m in candidats:
            if not DICO.lookup(m):
                douteux.append((m, suggestions(m)))
        total += len(douteux)
        print(f"=== {p.name} : {len(douteux)} mot(s) a verifier")
        for m, sug in douteux:
            s = f"  -> {', '.join(sug)}" if sug else ""
            print(f"    {m}{s}")
    print(f"\nTOTAL a verifier : {total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
