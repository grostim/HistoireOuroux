# Histoire d'Ouroux — Germain Odouard et Jh. Aubonnet

[![Validation LaTeX & Publication](https://github.com/grostim/HistoireOuroux/actions/workflows/ci-release.yml/badge.svg)](https://github.com/grostim/HistoireOuroux/actions/workflows/ci-release.yml)
[![Dernière version](https://img.shields.io/github/v/release/grostim/HistoireOuroux?label=Version&color=blue)](https://github.com/grostim/HistoireOuroux/releases/latest)

Projet de transcription intégrale et de mise en page sous **LaTeX** de la monographie <u>« Histoire d'Ouroux »</u> de **Germain Odouard** et **Jh. Aubonnet**, imprimée à Ouroux en 1952.

L'ouvrage retrace l'histoire de la commune d'Ouroux (aujourd'hui Ouroux-sur-Saône, Saône-et-Loire) : étymologie du nom, topographie, périodes romaine, burgonde et féodale, les fiefs et familles anciennes, l'église et les chapelles, les curés et vicaires, la Révolution, les écoles, et la période contemporaine, jusqu'à Avenas et son église.

> **Projet jumeau** de [grostim/BenoitCoste](https://github.com/grostim/BenoitCoste) et [grostim/FelixBerloty](https://github.com/grostim/FelixBerloty) — mêmes principes éditoriaux, même pipeline de publication.

---

## 📥 Téléchargements (Dernière version à jour)

Les documents sont automatiquement compilés et mis à disposition dans les trois formats suivants à chaque mise à jour :

| Format | Description | Lien de téléchargement |
| :--- | :--- | :---: |
| 📕 **PDF** | Version paginée officielle (mise en page typographique LaTeX) | [**Télécharger le PDF**](https://github.com/grostim/HistoireOuroux/releases/latest/download/Histoire_d_Ouroux.pdf) |
| 📱 **EPUB** | Version numérique adaptée aux liseuses, tablettes et smartphones | [**Télécharger l'EPUB**](https://github.com/grostim/HistoireOuroux/releases/latest/download/Histoire_d_Ouroux.epub) |
| 📄 **Markdown** | Version texte structurée pour consultation et traitement textuel | [**Télécharger le Markdown**](https://github.com/grostim/HistoireOuroux/releases/latest/download/Histoire_d_Ouroux.md) |

*(Vous pouvez également retrouver l'historique complet des versions sur la page des [Releases GitHub](https://github.com/grostim/HistoireOuroux/releases)).*

---

## 📖 Présentation de l'ouvrage

**« Histoire d'Ouroux »** a été rédigée par l'abbé **Germain Odouard**, vicaire à Ouroux de 1879 à 1892, puis curé de Trades, de Saint-Bonnet-les-Bruyères et de Monsols, où il mourut en septembre 1929. Le livre a été **préfacé par l'abbé Marcel Sivignon**, ancien séminariste de M. Odouard, puis **complété et imprimé par l'abbé Jh. Aubonnet**, curé d'Ouroux, en 1952.

- **Étymologie et topographie** : le nom d'Ouroux vient du latin *Oratorium*, « oratoire » ; limites de la paroisse Saint-Antoine, relief et voies de communication.
- **Périodes romaine, burgonde et féodale** : vestiges gallo-romains, le testament de Gondié, l'établissement de la féodalité et le régime des fiefs.
- **Les fiefs et familles anciennes** : Nagu, Arcis, La Carelle, Montaulieu, Grosbois, Alloignet, et les grandes familles locales (Trouilloux, Guillin, Morin, Polloce, Testenoire, Morétain, Berloty, Jambon…).
- **Le bourg** : population, quartiers, métiers et industries.
- **Le clergé local** : curés, vicaires et prêtres nés à Ouroux.
- **L'église d'Ouroux** : architecture, mobilier, tableaux et vitraux ; les chapelles de la Croix et de Saint-Claude.
- **La Grande Révolution**, les écoles, et la période contemporaine (jusqu'à la Seconde Guerre mondiale).
- **Avenas et son église**, en complément.

Le tirage original fut limité à **200 exemplaires** ; le livre est aujourd'hui consultable dans la bibliothèque généalogique de Geneanet (notice du livre `19016`).

---

## 📊 État d'avancement de la transcription

- **Chapitres structurés** : **29** — découpage repris de la table des matières de l'édition originale (voir § 5 des conventions).
- **Pages vues** : **286** (numérisation Geneanet, une vue par page).
- **Statut** : 🔄 **Transcription en cours** — chapitres 1 à 16 intégrés, illustrés lorsque nécessaire et compilés ; poursuite chapitre par chapitre.

Consultez le tableau détaillé dans [`CONVENTIONS_TRANSCRIPTION.md`](./CONVENTIONS_TRANSCRIPTION.md#5-état-davancement-de-la-transcription).

---

## 🗂 Structure du Dépôt

```
HistoireOuroux/
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   ├── config.yml               # Désactivation des issues vierges
│   │   └── erreur-transcription.yml # Template de signalement d'erreur
│   └── workflows/
│       └── ci-release.yml           # Pipeline CI/CD (compilation LaTeX, génération multi-format & release)
├── Originaux/                       # Copie de travail du fac-similé
│   ├── Histoire d'Ouroux.pdf        # PDF source intégral (286 vues)
│   └── Pages/                       # Vues extraites en JPG (une par page, 280 ppp)
│       ├── Page-001.jpg
│       ├── ...
│       └── Page-286.jpg
├── Illustrations/                   # Images éditoriales du livre
├── Histoire d'Ouroux.tex            # Source LaTeX principal du document
├── CONVENTIONS_TRANSCRIPTION.md     # Guide des conventions éditoriales et typographiques
├── README.md                        # Présentation du projet et liens de téléchargement
└── .gitignore                       # Exclusion des fichiers temporaires LaTeX
```

---

## 🛠 Conventions et Principes d'Édition

1. **Lecture visuelle directe** des vues à haute résolution (280 ppp), sans OCR parallèle : erreurs mécaniques et fautes manifestes corrigées ; vocabulaire, tournures et graphies d'époque conservés.
2. **Fidélité au texte** : les particularités typographiques de l'édition de 1952 (composition au stencil, dessins gravés par M. Mondon) sont restituées sans modernisation abusive.
3. **Notes de bas de page** : Notes de l'auteur conservées via `\footnote{...}` ; notes du transcripteur explicitement marquées `(Note du transcripteur)`.
4. **Commits conventionnels en français** : Chaque tranche de transcription ou correction fait l'objet d'un commit unitaire (`feat: ...`, `fix: ...`, `docs: ...`).
5. **Gestion automatisée des releases** :
   - Ajout d'une nouvelle tranche de transcription $\rightarrow$ **Release majeure** (`v2.0.0`, etc.).
   - Correction de coquille ou ajustement de mise en page $\rightarrow$ **Release mineure** (`v1.1.0`, etc.).

Pour le détail complet des règles typographiques et éditoriales, consultez le fichier [`CONVENTIONS_TRANSCRIPTION.md`](./CONVENTIONS_TRANSCRIPTION.md).

---

## 🔗 Provenance documentaire

- **Ouvrage** : *Histoire d'Ouroux*, par l'abbé Germain Odouard et l'abbé Jh. Aubonnet, imprimé à Ouroux en 1952, 286 pages, tirage à 200 exemplaires.
- **Fac-similé** : bibliothèque généalogique de Geneanet, [notice du livre 19016](https://www.geneanet.org/bibliotheque-genealogie/doc/19016/) — accès gratuit après inscription.
- **Résolution du fac-similé** : 280 ppp (scans CCITT G4 d'origine), conservée à l'identique.
