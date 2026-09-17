#!/usr/bin/env python3
"""Transcrit une vue du fac-similé « Histoire d'Ouroux » via agy (lecture visuelle Gemini).

Deux sources sont produites pour chaque vue :
  1. l'OCR présent dans le PDF source (pdftotext), qui sert de garde-fou ;
  2. la lecture visuelle directe de la vue PNG en haute résolution par agy.

La transcription retenue est la lecture visuelle ; l'OCR sert à détecter les
omissions et les divergences (repérées par comparaison de longueur et de mots).

Usage :
    python3 scripts/transcribe_page.py 10 11 12
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PDF = ROOT / "Originaux" / "Histoire d'Ouroux.pdf"
PAGES = ROOT / "Originaux" / "Pages"
WORK = ROOT / "scratch" / "transcription"
AGY = "/home/sorg/.local/bin/agy"
MODEL = "gemini-3.1-pro-high"

PROMPT = """Tu es transcriveur de documents historiques imprimés.

Lis la vue : {image}

Contexte : « Histoire d'Ouroux », monographie de l'abbé Germain Odouard et de
l'abbé Jh. Aubonnet, imprimée à Ouroux en 1952. C'est la vue {vue} du fac-similé
(page imprimée {imprime}). Le livre est composé en caractères espacés (procédé
stencil), le texte est en français et porte sur l'histoire locale d'Ouroux
(Saône-et-Loire, région du Beaujolais/Mâconnais). L'image est en haute
résolution (environ 2310 x 3075 px) : zoome pour lire chaque mot avec certitude.

CONSIGNE : transcris l'INTÉGRALITÉ du texte de cette vue, dans l'ordre de lecture.

RÈGLES DE TRANSCRIPTION :
1. IGNORE le folio en haut de page (« - 7 - », « - 181 - ») : il n'est pas transcrit.
2. IGNORE les marques de scan (bords noirs de reliure, taches, traits parasites).
3. Rétablis la casse normale des titres et des noms propres : un titre imprimé en
   capitales espacées devient un titre en casse normale ; un nom propre en
   capitales devient Title Case (ex. « DULIGIER » -> « Duligier », « TESTENOIRE »
   -> « Testenoire », « St-ANTOINE d'OUROUX » -> « St-Antoine d'Ouroux »).
4. CORRIGE uniquement les erreurs MÉCANIQUES de composition :
   - lettre I ou l mise pour le chiffre 1 dans les dates et les nombres
     (I952 -> 1952, I064 -> 1064, XVème -> XVe siècle) ;
   - espacements anormaux dus à la composition au stencil :
     « l ' â g e r » -> « l'âger », « p r i e » -> « prie » ;
   - mots collés par l'absence d'espace : « ORATORIUM,ora toire » ->
     « ORATORIUM, oratoire », « chapelles.Nous » -> « chapelles. Nous » ;
   - césures de fin de ligne réunies, mots coupés recomposés.
5. ORTHOGRAPHE — règle du projet (identique à BenoitCoste et FelixBerloty) : les
   fautes d'orthographe ÉVIDENTES de l'édition originale sont corrigées dans
   notre transcription. Cela couvre :
   - les accents omis, faux ou déplacés (l'édition de 1952, composée au stencil
     sur du matériel bon marché, en omet systématiquement) :
     « chateau » -> « château », « disparaitre » -> « disparaître »,
     « dégats » -> « dégâts », « aprés » -> « après », « gite » -> « gîte »,
     « oeil » -> « œil », « paiens » -> « païens », « hierarchie » -> « hiérarchie »,
     « évéques » -> « évêques », « s'arrétant » -> « s'arrêtant » ;
   - les coquilles et fautes banales : « donaer » -> « donner », « deftinées » ou
     « dfinées » -> « destinées », « prénons » -> « prénoms », « plustôt » ->
     « plutôt », « n'evant » -> « n'ayant », « ecclésiatique » ->
     « ecclésiastique », « Chartres » (au sens de chartes) -> « Chartes » ;
   - les accords grammaticaux manifestement fautifs.
6. NE MODIFIE PAS en revanche : le vocabulaire et les tournures d'époque, les
   abréviations (St, Ste, Mr, Mgr, XVème/IX°), les noms propres et toponymes
   (même d'aspect ancien : « Loittes », « Razay »), et les CITATIONS LATINES,
   qui sont reproduites littéralement telles qu'imprimées (« amnid », « Graonna,
   fluvius », « Crahonnae »). Une citation n'est jamais corrigée.
7. Casse des noms propres : les noms imprimés en capitales espacées sont rendus
   en casse normale (Title Case) — « DULIGIER » -> « Duligier », « St-ANTOINE
   d'OUROUX » -> « St-Antoine d'Ouroux ». Seuls les chiffres romains et les
   sigles d'époque gardent des majuscules.
8. Les citations latines sont conservées en latin, entre guillemets, sans les traduire.
9. Respecte les paragraphes : commence un nouveau paragraphe là où l'original en
   commence un (alinéa visible par un retrait).
10. ILLUSTRATIONS : si la vue contient un ou plusieurs dessins, gravures ou
   photographies, insère à l'endroit exact où ils apparaissent une ligne de la forme :
   [[ILLUSTRATION: légende exacte telle qu'imprimée|position]]
   où position vaut haut, milieu ou bas selon l'emplacement dans la page.
   Si le dessin n'a pas de légende, écris [[ILLUSTRATION: sans légende|position]].
   Ne décris pas les illustrations, transcris seulement leur légende.
11. Si un mot reste illisible malgré le zoom, écris [ILLISIBLE: ton hypothèse] :
    ne devine jamais silencieusement.

SORTIE ATTENDUE : uniquement le texte transcrit, sans commentaire ni préambule."""


def ocr(vue: int) -> str:
    """OCR présent dans le PDF source (garde-fou de comparaison)."""
    out = subprocess.run(
        ["pdftotext", "-layout", "-f", str(vue), "-l", str(vue), str(PDF), "-"],
        capture_output=True, text=True,
    ).stdout
    return out


def mots(texte: str) -> list[str]:
    return re.findall(r"[A-Za-zÀ-ÿ]{4,}", texte.lower())


def visuel(vue: int) -> tuple[str, int, str]:
    """Lecture visuelle par agy. Retourne (texte, code_retour, stderr)."""
    prompt = PROMPT.format(image=PAGES / f"Page-{vue:03d}.png", vue=vue, imprime=vue - 3)
    r = subprocess.run(
        [AGY, "--print", prompt, "--model", MODEL, "--print-timeout", "600s"],
        capture_output=True, text=True, cwd=str(WORK), timeout=700,
    )
    return r.stdout, r.returncode, r.stderr


def main() -> int:
    WORK.mkdir(parents=True, exist_ok=True)
    vues = [int(a) for a in sys.argv[1:]]
    if not vues:
        print(__doc__)
        return 1
    for vue in vues:
        img = PAGES / f"Page-{vue:03d}.png"
        if not img.exists():
            print(f"vue {vue} : image absente ({img})")
            continue

        (WORK / f"vue-{vue:03d}-ocr.txt").write_text(ocr(vue), encoding="utf-8")
        print(f"--- vue {vue} (imprimée {vue - 3}) : agy en cours…", flush=True)
        texte, code, err = visuel(vue)
        (WORK / f"vue-{vue:03d}-agy.txt").write_text(texte, encoding="utf-8")

        # contrôle croisé OCR <-> lecture visuelle
        a, b = set(mots(ocr(vue))), set(mots(texte))
        commun = len(a & b) / max(1, len(a))
        print(f"    exit={code} octets={len(texte)} recouvrement_OCR={commun:.0%}")
        if code != 0:
            print(f"    STDERR: {err[:400]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
