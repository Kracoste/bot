# IA plans + prix bricolage

Ce projet combine deux IA collaboratives :

- **plan_ai** : lit des plans (PDF ou images), extrait du texte via OCR, repère les mesures et calcule des surfaces estimatives.
- **price_ai** : interroge l'API Google Custom Search pour identifier les prix visibles chez Point.P, Brico Dépôt et Castorama, avec un parsing HTML ciblé.

L'entrée principale `main.py` orchestre l'analyse d'un plan puis interroge automatiquement l'IA prix en fonction des surfaces détectées.

> ⚠️ Respectez les conditions d'utilisation de Google et des enseignes ciblées. Les prix retournés proviennent des extraits des résultats de recherche et peuvent être incomplets ou obsolètes. Vérifiez toujours sur le site officiel avant toute décision.

## Structure

```
project-root/
├── main.py                 # Orchestrateur plan + prix
├── price_ai/               # Modules de recherche de prix
├── plan_ai/                # Lecture de plans, OCR, calculs géométriques
└── shared/                 # Utilitaires communs
```

## Prérequis

- Python 3.10 ou supérieur
- Packages listés dans `requirements.txt` (`pandas`, `opencv-python`, `pytesseract`, `pdfplumber`, etc.)
- Clé API Google + identifiant Custom Search Engine (CSE) configuré pour `pointp.fr`, `bricodepot.fr`, `castorama.fr`
- Tesseract installé sur votre OS si vous utilisez l'OCR (macOS : `brew install tesseract`)

## Installation rapide

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Créez ensuite `.env` :

```bash
GOOGLE_API_KEY="votre_cle_api_google"
GOOGLE_CSE_ID="votre_identifiant_cse"
```

## Utilisation

### 1. Analyse complète (plan + prix)

```bash
python main.py plans/maison.pdf --show-table --coverage 1.4
```

- Affiche les surfaces détectées (tableau `pandas`) si `--show-table`
- Calcule une estimation de matériaux via `--coverage`
- Déduit automatiquement une requête produit d'après la plus grande zone repérée (ou utilisez `--price-query "sac de ciment 25kg"`)

### 2. IA prix uniquement

- Script ponctuel :
  ```bash
  python price_checker.py "perceuse sans fil makita"
  ```
- Mode conversationnel :
  ```bash
  python price_chat.py
  ```
  Commandes disponibles : `set results N`, `quit` / `exit` / `Ctrl+D`

Exemple de retour IA prix :

```
Résultats pour: sac de ciment 25kg
==============================
- Point.P: prix non détecté
  Sac ciment 25 kg - Point.P
  https://www.pointp.fr/...
- Brico Dépôt: 4,50 € (page magasin)
  Ciment universel pour béton - sac de 25 kg - Brico Dépôt
  https://www.bricodepot.fr/...
- Castorama: 7,19 € (page magasin)
  Ciment Multi usage CIM II 32,5R CE 25 kg
  https://www.castorama.fr/...
```

## Limitations connues

- Certaines pages (ex. sites protégés par CAPTCHA) restent inaccessibles automatiquement.
- L'extraction de mesures dépend fortement de la qualité du plan. En cas de résultats vides, ajustez la résolution ou fournissez des annotations textuelles plus claires.
- La requête produit déduite automatiquement peut être approximative. Utilisez `--price-query` pour préciser le besoin.

## Pistes d'amélioration

- Ajouter un entraînement ML dédié à la détection de pièces/objets sur plan.
- Alimenter un cache de résultats Google + prix magasins pour accélérer les requêtes.
- Générer des BOM (Bill of Materials) détaillées à partir des surfaces détectées et relier chaque poste à une requête prix dédiée.
