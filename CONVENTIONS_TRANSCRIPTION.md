# Conventions de transcription de l'Histoire d'Ouroux

Ce document consigne l'ensemble des règles éditoriales, typographiques, techniques et organisationnelles pour la transcription en LaTeX de la monographie <u>« Histoire d'Ouroux »</u> de **Germain Odouard** et **Jh. Aubonnet**, imprimée à Ouroux en 1952. Le fac-similé numérisé compte **286 vues** (bibliothèque généalogique de Geneanet, notice du livre `19016`), conservées à **280 ppp**.

---

## 1. Organisation du projet & Gestion de version (Git)

### 1.1 Dépôt Git
- Le projet est versionné sous Git dans le répertoire racine.
- Les scans originaux sont conservés dans `Originaux/` : le PDF source intégral (`Histoire d'Ouroux.pdf`) et les vues extraites `Originaux/Pages/Page-001.png` à `Page-286.png`.
- Le document principal est `Histoire d'Ouroux.tex`.
- Les fichiers auxiliaires LaTeX (`*.aux`, `*.log`, `*.toc`, etc.) sont exclus via `.gitignore`.

### 1.2 Conventional Commits (en français uniquement)
Tous les messages de commit doivent strictement suivre la norme des *Conventional Commits* rédigés en français, avec la structure suivante :

```
<type>[portée optionnelle]: <description en français au présent de l'indicatif/infinitif>

[corps optionnel explicatif]
```

#### Types autorisés :
- `feat:` : Ajout d'une nouvelle transcription de chapitre ou de contenu textuel majeur (ex. `feat: transcription du chapitre Nagu`).
- `fix:` : Correction de transcription, de coquille, de ponctuation ou d'erreur LaTeX (ex. `fix: correction d'une coquille dans la période féodale`).
- `docs:` : Mise à jour de la documentation, du fichier de conventions ou de métadonnées (ex. `docs: ajout des règles de transcription`).
- `style:` : Ajustements de mise en page, d'espacement, de formatage LaTeX sans modification du texte (ex. `style: harmonisation des tirets d'incise`).
- `refactor:` : Réorganisation structurelle du code LaTeX (ex. `refactor: normalisation des titres de sections`).
- `chore:` : Tâches de maintenance, mise à jour du `.gitignore` ou scripts de travail.

---

## 2. Structure et Préambule LaTeX

### 2.1 Configuration globale
Le document utilise la classe `report` avec les packages suivants :
```latex
\documentclass[11pt,a4paper]{report}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage[french]{babel}
\usepackage{amsmath}
\usepackage{graphicx}
\usepackage{geometry}
\usepackage{pdflscape}
\usepackage{pdfpages}
\geometry{margin=2.5cm, headheight=14pt}
\usepackage{parskip}
\usepackage{setspace}
\usepackage{fancyhdr}
\usepackage{hyperref}
\usepackage{qrcode}
```

### 2.2 Titre et métadonnées
```latex
\title{\Huge \textbf{Histoire d'Ouroux}}
\author{\textbf{Germain Odouard et Jh. Aubonnet}}
\date{}
```

Le workflow CI injecte le numéro de release via `\releaseversion` (défini par `\providecommand` dans le préambule, remplacé par la CI sur une copie `*.release.tex`).

### 2.3 En-têtes de page
L'ouvrage imprimé porte un en-tête avec le titre courant et le folio. La transcription reproduit cette logique via `fancyhdr` :
```latex
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\small\textit{Histoire d'Ouroux}}
\fancyhead[R]{\small\textit{Chapitre \thechapter}}
\fancyfoot[C]{\thepage}
```
Les en-têtes répétés mécaniquement dans l'original ne sont **pas** transcrits dans le corps du texte.

---

## 3. Règles de Transcription et Mise en Page

### 3.1 Double pagination — règle fondamentale
L'ouvrage numérisé comporte **deux numérotations qu'il ne faut jamais confondre** :

| Référence | Plage | Usage |
| :--- | :--- | :--- |
| **Vue** (numérisation) | 1 à 286 | Repérage dans `Originaux/Pages/Page-NNN.jpg` |
| **Page imprimée** | 3 à 283 | Numérotation portée sur le livre, seule citée dans le texte |

**Relation vérifiée sur l'ensemble du volume : `page imprimée = vue − 3`** (ex. la vue 15 porte le folio « - 12 - », qui est la page imprimée 12).

- Dans les commentaires LaTeX, les deux références sont toujours données : `% Page imprimée 12 — vue 15`.
- Dans le corps du texte et dans les citations, **seule la page imprimée est utilisée** (c'est celle que voit un lecteur de l'édition papier).
- Dans la table d'avancement (§ 5), les deux colonnes figurent.

### 3.2 Préservation de la structure et du séquençage
- L'ouvrage est découpé en **29 unités** correspondant aux rubriques de la table des matières de l'édition originale (voir § 5).
- Chaque grande rubrique correspond à un `\chapter{...}`, avec un bloc de commentaires standardisé :
  ```latex
  % ===================================================
  % TITRE DE LA RUBRIQUE
  % Page imprimée NN — vue NN
  % ===================================================
  \chapter{Titre normalisé de la rubrique}
  ```
- Les sous-rubriques de la table des matières d'origine (École de filles, École de garçons, Notes sur la laïcisation) sont transcrites en sections non numérotées : `\section*{...}`.
- Un paragraphe interrompu par le saut de page de l'original est **réuni en un seul paragraphe** : jamais deux blocs séparés au milieu d'une phrase. Le commentaire de page devient alors `% --- Page imprimée X (fin) + Page Y (début) — phrase continue`.

### 3.3 Les illustrations
- L'édition originale comporte **123 illustrations** numérotées, recensées par sa propre « Table des illustrations » (pages imprimées 282-283).
- Chaque illustration est intégrée à l'endroit où elle apparaît dans l'original, avec sa légende telle qu'imprimée.
- Les dessins ont été gravés sur stencils par **M. Mondon de Guillin** (château du Sauzey à Avenas), comme le rappelle l'avertissement.
- **Cadrage des illustrations** : chaque illustration est recadrée depuis le rendu de la vue à 280 ppp par `scripts/extract_illustration.py` (résolution native du fac-similé, aucun ré-échantillonnage, pixels conservés à l'identique). Le cadrage doit contenir **la totalité du motif**, de la tête aux pieds s'il s'agit d'un personnage, ainsi que le cadre et la légende quand ils font partie de l'illustration. Aucun trait ne doit être tronqué. Les marges imprimées de l'original sont inégales autour d'un dessin — un cadrage « à l'œil » ou aligné sur un bord coupe le motif.
- **Position relative** : l'emplacement de l'image par rapport au texte fait partie de la mise en page transcrite. Relever si l'image est à gauche, à droite, centrée, au-dessus ou au-dessous du texte, et quel paragraphe l'introduit. Quand le texte original entoure une image, utiliser `wrapfigure` du côté correspondant (`{l}` ou `{r}`), placé immédiatement avant le paragraphe qui commence l'habillage ; ne pas remplacer cette composition par une figure flottante isolée. Régler largeur et éventuel `\vspace` en comparant le nombre de lignes habillées au scan.
- **Contrôle obligatoire** avant de référencer une illustration dans le source : `scripts/check_illustration.py <vue> <x> <y> <w> <h> <nom> --cercle` (ajouter `--bord` quand le sujet ne touche pas les bords dans l'original). Le script vérifie la fidélité au scan, l'absence d'encre sur les bords, et la couverture complète de l'arc pour les vignettes circulaires.
- **Contrôle après compilation** : une extraction correcte ne suffit pas. Rasteriser chaque page PDF qui contient l'illustration et vérifier visuellement les quatre bords, le cadre, la légende, l'échelle, le ratio, le découpage éventuel par LaTeX et le flux du texte à droite, à gauche et sous l'image. Les numéros de vues source ne prédisent pas les numéros des pages du PDF compilé, car les figures et les pages liminaires déplacent la pagination.

### 3.4 Notes de bas de page (`\footnote`)
- Toutes les notes imprimées de l'ouvrage sont scrupuleusement préservées via `\footnote{...}`.
- Les notes ajoutées par le transcripteur (lecture incertaine, clarification, référence à une source) doivent porter la mention explicite `(Note du transcripteur)`.

### 3.5 Fidélité au texte et corrections
- Transcription réalisée par **lecture visuelle directe** des vues à haute résolution (280 ppp), avec l'OCR comme aide de localisation et agy/vision comme seconde lecture contrôlée.
- **Contrôle croisé obligatoire** : comparer la sortie agy à l'OCR, exécuter le triage des mots douteux, puis vérifier visuellement les suspects et les passages à faible recouvrement. Une page essentiellement illustrée peut avoir un faible recouvrement sans être incomplète ; elle doit alors être contrôlée par vision.
- **Citations et documents** : toute traduction de charte, tout extrait documentaire ou tout passage explicitement présenté comme une citation est encadré par les guillemets visibles dans la source, y compris lorsqu'il s'étend sur plusieurs paragraphes. Ne jamais transformer silencieusement une citation en prose ordinaire.
- **Corrections systématiques des erreurs mécaniques** de la composition :
  - confusion `I` majuscule / chiffre `1` dans les nombres et les dates (`I952` → `1952`, `I886` → `1886`) ;
  - espacements anormaux : `collaboré,d'une` → `collaboré, d'une` ;
  - césures de fin de ligne réunies : `néces-\nsitée` → `nécessité`.
- **Corrections des erreurs de syntaxe et d'orthographe manifestes** : accords grammaticaux évidents, accents manquants évidents (`Aout` → `Août`), fautes banales (`plustôt` → `plutôt`, `pos?ble` → `possible`).
- **Conservation stricte** : vocabulaire et tournures d'époque, abréviations (`St`, `Ste`, `Mr`, `Mgr`, `5me`), appellations et graphies d'époque.
- Les passages illisibles sont signalés `[ILLISIBLE: hypothèse]` avec note de bas de page si un contexte aide à la lecture.
- Les citations latines ou étrangères reçoivent une note de bas de page avec source et traduction, mention `(Note du transcripteur)`.

### 3.6 Casse des noms propres
- Dans la composition d'origine, les noms propres apparaissent souvent en capitales d'imprimerie intégrales (ex. `TROUILLOUX`, `GUILLIN`, `MORÉTAIN`, `TESTENOIRE`).
- **Règle de normalisation :** tous les noms propres de personnes, de lieux ou d'institutions sont uniformisés en bas de casse avec initiale majuscule (Title Case) : `Trouilloux`, `Guillin`, `Morétain`, `Testenoire`, `Nagu`, `Arcis`, `Montaulieu`.
- Seuls les chiffres romains (ex. `Louis XI`, `Pie VII`) et les sigles d'époque conservent des majuscules multiples.
- Les noms de lieux-dits et de châteaux suivent la graphie de l'original en casse normalisée (`château du Sauzey`, `La Carelle`, `Grosbois`).

---

## 4. Règles Typographiques et Orthotypographiques

### 4.1 Dialogues et incises
- Les répliques de dialogue sont introduites par un tiret demi-cadratin (`--`) si l'original le fait ; les incises suivent la ponctuation de l'original.

### 4.2 Intervalles de dates et nombres
- Utiliser le double tiret pour les plages temporelles : `(1879--1892)`, `(1939--1945)`.

### 4.3 Abréviations et exposants
- Utiliser la commande `\up{...}` de `babel[french]` pour les exposants : `4\up{e} étage`, `1\up{er}`.
- Conserver les abréviations d'époque : `St Antoine`, `Ste Marie`, `Mr`, `Mgr`, `5me`.
- Les mois révolutionnaires du calendrier républicain sont conservés tels qu'imprimés, avec conversion en note si utile à la compréhension.

### 4.4 Ligatures et caractères spéciaux
- Utiliser les ligatures françaises : `cœur`, `sœur`, `œuvre`, `vœu`.
- Conserver les majuscules accentuées (`À`, `É`, `È`) selon l'usage moderne.
- Les termes latins ou en langue étrangère sont mis en italique (`\textit{Oratorium}`, `\textit{villa}`).

### 4.5 Espacements et paragraphes
- Les changements de paragraphe sont marqués par une ligne vide (géré via `parskip`).
- La ponctuation haute (`;`, `:`, `!`, `?`) bénéficie de l'espacement automatique géré par `babel[french]`.

---

## 5. État d'avancement de la transcription

Découpage repris de la **table des matières de l'édition originale** (pages imprimées 282-283). La colonne « Page imprimée » est la page du livre ; la colonne « Vue » est la vue numérisée correspondante (`Originaux/Pages/Page-NNN.jpg`).

| # | Rubrique | Page impr. | Vue | Statut |
| :---: | :--- | :---: | :---: | :---: |
| — | Page de titre, avertissement, liste des souscripteurs, préface | 3–6 | 6–9 | Transcrites et vérifiées |
| 1 | Étymologie du nom d'Ouroux | 7–8 | 10–11 | Transcrite et vérifiée |
| 2 | Topographie | 9–11 | 12–14 | Transcrite et vérifiée |
| 3 | Période romaine | 12–19 | 15–22 | Transcrite, illustrée et vérifiée |
| 4 | Période burgonde | 20–28 | 23–31 | Transcrite, illustrée et vérifiée |
| 5 | Période féodale | 29–34 | 32–37 | Transcrite, illustrée et vérifiée |
| 6 | Nagu | 35–46 | 38–49 | Transcrit, illustré et compilé |
| 7 | Arcis | 47–50 | 50–53 | Transcrit, compilé |
| 8 | La Carelle | 51–60 | 54–63 | Transcrit, compilé |
| 9 | Montaulieu | 57–61 | 60–64 | Transcrit, illustré, compilé |
| 10 | Grosbois | 62–66 | 65–69 | Transcrit, illustré, compilé |
| 11 | Autres familles anciennes | 67–71 | 70–74 | Transcrit, compilé |
| 12 | Alloignet | 72–74 | 75–77 | Transcrit, compilé |
| 13 | Bourg, population, industries, etc. | 75–95 | 78–98 | Transcrit, compilé |
| 14 | Curés d'Ouroux | 96–140 | 99–143 | Transcrit, compilé |
| 15 | La Grande Révolution | 141–166 | 144–169 | Transcrit, compilé |
| 16 | Vicaires d'Ouroux | 167–175 | 170–178 | Transcrit, compilé |
| 17 | Prêtres nés à Ouroux | 176–180 | 179–183 | Transcrit, compilé |
| 18 | L'église d'Ouroux | 181–230 | 184–233 | Transcrit, compilé |
| 19 | Les écoles d'Ouroux | 231–259 | 234–262 | Transcrit, compilé |
| 19a | École de filles | 233–244 | 236–247 | Transcrit, compilé |
| 19b | École de garçons | 245–256 | 248–259 | Transcrit, compilé |
| 19c | Notes sur la laïcisation et les secours accordés aux écoles libres | 257–260 | 260–263 | Transcrit, compilé |
| 20 | Période contemporaine | 261–274 | 264–277 | Transcrit, compilé |
| 20a | Un maire chrétien | 262–263 | 265–266 | Transcrit, compilé |
| 20b | Guerre 1914–1918 | 264–267 | 267–270 | Transcrit, compilé |
| 20c | Catastrophes aériennes | 267 | 270 | Transcrit, compilé |
| 20d | Guerre 1939–1945, bombardement | 268–269 | 271–272 | Transcrit, compilé |
| 20e | Vieilles maisons | 270 | 273 | Transcrit, compilé |
| 20f | Progrès social et matériel | 271–274 | 274–277 | Transcrit, compilé |
| 21 | Conclusion | 275 | 278 | Transcrit, compilé |
| 22 | Avenas et son église | 276–281 | 279–284 | Transcrit, compilé |
| — | Table des matières et table des illustrations | 283–284 | 285–286 | Transcrites, compilées |

**État : transcription complète du document, y compris les tables finales.** La couverture, les chapitres liminaires, les chapitres historiques, les rubriques finales, la table des matières et la table des illustrations sont intégrés, illustrés lorsque nécessaire et compilés.

---

## 6. Provenance documentaire

- **Ouvrage** : *Histoire d'Ouroux*, par l'abbé Germain Odouard (vicaire à Ouroux de 1879 à 1892) et l'abbé Jh. Aubonnet (curé d'Ouroux), préface de l'abbé Marcel Sivignon. Imprimé à Ouroux en 1952. 286 pages, tirage à 200 exemplaires.
- **Fac-similé** : bibliothèque généalogique de Geneanet, notice du livre [`19016`](https://www.geneanet.org/bibliotheque-genealogie/doc/19016/) — accès gratuit après inscription.
- **Caractéristiques techniques du fac-similé** : PDF de 19 849 665 octets, 286 pages, scans CCITT G4 à **280 ppp** (2 307 × 3 074 px environ par page), couche OCR présente. Empreinte SHA-256 : `924d80b50ff612c4cafa1c31fe01fd18687de9ee615fce43d31c772b148ee1be`.
- **Avertissement d'origine** : les frais d'édition s'élevaient à plus de 100 000 francs ; la plupart des dessins ont été gravés sur stencils par M. Mondon. Le livre était promis pour l'hiver 1952-1953.
