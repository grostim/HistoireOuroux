#!/usr/bin/env python3
"""Contrôle les invariants de base du PDF produit par la compilation LaTeX.

Ce contrôle ne remplace pas une relecture visuelle du fac-similé. Il évite en
revanche qu'une régression technique passe inaperçue dans la CI : illustration
référencée mais absente, PDF non A4, pagination manifestement anormale, page
entièrement vide, repère éditorial manquant ou débordement LaTeX.

Usage :
    python3 scripts/check_pdf_layout.py \
        --source "Histoire d'Ouroux.tex" \
        --pdf Histoire_d_Ouroux.pdf \
        --log "Histoire d'Ouroux.release.log" \
        --min-pages 190 --max-pages 220
"""
from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path


GRAPHIC_RE = re.compile(
    r"\\includegraphics(?:\[[^\]]*\])?\{([^{}]+)\}"
)
INPUT_RE = re.compile(r"\\(?:input|include)\{([^{}]+)\}")
OVERFULL_RE = re.compile(r"Overfull \\[hv]box")
UNDERFULL_RE = re.compile(r"Underfull \\[hv]box")

REQUIRED_MARKERS = (
    "Table des matières",
    "Table des illustrations",
    "Population totale",
)


def run(command: list[str]) -> str:
    """Exécute une commande et retourne sa sortie standard."""
    try:
        result = subprocess.run(
            command,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except FileNotFoundError as exc:
        raise RuntimeError(f"commande introuvable : {command[0]}") from exc
    except subprocess.CalledProcessError as exc:
        detail = exc.stderr.strip() or exc.stdout.strip()
        raise RuntimeError(f"échec de {' '.join(command)} : {detail}") from exc
    return result.stdout


def tex_sources(root: Path, entry: Path) -> list[Path]:
    """Retourne le source principal et les fichiers LaTeX qu'il inclut."""
    pending = [entry]
    visited: set[Path] = set()
    sources: list[Path] = []

    while pending:
        source = pending.pop()
        source = source.resolve()
        if source in visited or not source.is_file():
            continue
        visited.add(source)
        sources.append(source)
        content = source.read_text(encoding="utf-8")
        for reference in INPUT_RE.findall(content):
            included = root / reference
            if not included.suffix:
                included = included.with_suffix(".tex")
            pending.append(included)
    return sources


def referenced_images(root: Path, source: Path) -> list[str]:
    """Retourne les chemins d'images déclarés dans l'arbre LaTeX."""
    references: list[str] = []
    for tex in tex_sources(root, source):
        references.extend(GRAPHIC_RE.findall(tex.read_text(encoding="utf-8")))
    return list(dict.fromkeys(references))


def image_candidates(root: Path, reference: str) -> list[Path]:
    """Construit les candidats acceptés par graphicx avec ou sans extension."""
    path = root / reference
    if path.suffix:
        return [path]
    return [path.with_suffix(extension) for extension in (".png", ".jpg", ".jpeg", ".pdf")]


def check_images(root: Path, source: Path) -> list[str]:
    """Vérifie chaque référence d'image et retourne les chemins manquants."""
    missing: list[str] = []
    references = referenced_images(root, source)
    for reference in references:
        if not any(candidate.is_file() for candidate in image_candidates(root, reference)):
            missing.append(reference)
    print(f"OK  images : {len(references)} référence(s), {len(missing)} manquante(s)")
    return missing


def check_pdf(pdf: Path, min_pages: int, max_pages: int) -> list[str]:
    """Contrôle le format, la pagination, le texte et les repères éditoriaux."""
    info = run(["pdfinfo", str(pdf)])
    page_match = re.search(r"^Pages:\s+(\d+)$", info, re.MULTILINE)
    size_match = re.search(r"^Page size:\s+(.+)$", info, re.MULTILINE)
    if page_match is None or size_match is None:
        return ["pdfinfo ne fournit pas les métadonnées attendues"]

    pages = int(page_match.group(1))
    page_size = size_match.group(1).strip()
    failures: list[str] = []
    if not (min_pages <= pages <= max_pages):
        failures.append(
            f"nombre de pages inattendu : {pages} (plage acceptée {min_pages}–{max_pages})"
        )
    if not page_size.startswith("595.276 x 841.89"):
        failures.append(f"format de page inattendu : {page_size}")

    text = run(["pdftotext", "-layout", str(pdf), "-"])
    extracted_pages = text.split("\f")
    if extracted_pages and not extracted_pages[-1].strip():
        extracted_pages.pop()
    if len(extracted_pages) != pages:
        failures.append(
            f"pdftotext extrait {len(extracted_pages)} page(s) sur {pages}"
        )

    empty_pages = [index + 1 for index, page in enumerate(extracted_pages) if not page.strip()]
    if empty_pages:
        failures.append(f"page(s) sans texte détectée(s) : {empty_pages}")

    missing_markers = [marker for marker in REQUIRED_MARKERS if marker not in text]
    if missing_markers:
        failures.append(f"repère(s) absent(s) du PDF : {missing_markers}")

    print(f"OK  PDF : {pages} page(s), format {page_size}")
    print(f"OK  texte : {len(extracted_pages)} page(s) extractible(s)")
    if not missing_markers:
        print(f"OK  repères : {len(REQUIRED_MARKERS)} repère(s) présents")
    return failures


def check_log(log: Path | None) -> list[str]:
    """Signale les débordements LaTeX et affiche les avertissements de densité."""
    if log is None:
        return []
    if not log.is_file():
        return [f"journal LaTeX introuvable : {log}"]

    content = log.read_text(encoding="utf-8", errors="replace")
    overfull = len(OVERFULL_RE.findall(content))
    underfull = len(UNDERFULL_RE.findall(content))
    if overfull:
        print(f"ECHEC: {overfull} débordement(s) LaTeX Overfull détecté(s)")
        return ["débordement(s) LaTeX Overfull détecté(s)"]
    print("OK  débordements : aucun Overfull détecté")
    if underfull:
        print(f"AVERTISSEMENT: {underfull} avertissement(s) Underfull (non bloquant)")
    return []


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--pdf", type=Path, required=True)
    parser.add_argument("--log", type=Path)
    parser.add_argument("--min-pages", type=int, default=190)
    parser.add_argument("--max-pages", type=int, default=220)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(__file__).resolve().parent.parent
    failures: list[str] = []

    for path, label in ((args.source, "source"), (args.pdf, "PDF")):
        if not path.is_file():
            failures.append(f"{label} introuvable : {path}")
    if failures:
        for failure in failures:
            print(f"ECHEC: {failure}")
        return 1

    failures.extend(f"image manquante : {reference}" for reference in check_images(root, args.source))
    failures.extend(check_pdf(args.pdf, args.min_pages, args.max_pages))
    failures.extend(check_log(args.log))

    if failures:
        for failure in failures:
            print(f"ECHEC: {failure}")
        return 1
    print("SUCCÈS : contrôles PDF terminés")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
