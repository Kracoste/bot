# Agrégateur de prix bricolage

Cet outil interroge l'API Google Custom Search afin de repérer rapidement les prix visibles dans les résultats Leroy Merlin, Brico Dépôt et Castorama pour un produit donné. Lorsque la fiche magasin est accessible, le script récupère le HTML et extrait le prix structuré (JSON-LD, meta tags) afin d'éviter les faux positifs.

> ⚠️ Respectez les conditions d'utilisation de Google et des enseignes ciblées. Les prix retournés proviennent des extraits des résultats de recherche et peuvent être incomplets ou obsolètes. Vérifiez toujours sur le site officiel avant toute décision.

## Prérequis

- Python 3.10 ou supérieur
- Une clé API Google valide et **un identifiant de moteur de recherche (CX)** configuré pour interroger les domaines `leroymerlin.fr`, `bricodepot.fr` et `castorama.fr`.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuration

Créez un fichier `.env` à la racine du projet ou exportez les variables d'environnement suivantes :

```bash
export GOOGLE_API_KEY="votre_cle_api_google"
export GOOGLE_CSE_ID="votre_identifiant_cse"
```

> Ne partagez jamais votre clé API. Le fichier `.env` ne doit pas être commité.

Pour configurer le moteur de recherche personnalisé :
1. Rendez-vous sur <https://programmablesearchengine.google.com/>.
2. Créez un nouveau moteur en ajoutant les sites `leroymerlin.fr`, `bricodepot.fr`, `castorama.fr`.
3. Activez l'API Custom Search dans Google Cloud Console et récupérez la clé API.
4. Renseignez `GOOGLE_CSE_ID` avec l'identifiant du moteur.

## Utilisation

- Mode ponctuel :
  ```bash
  python price_checker.py "perceuse sans fil makita"
  ```
  Options utiles :
  - `--per-store-results N` : nombre de résultats Google analysés par magasin (1 à 10, défaut 3).

- Mode conversationnel :
  ```bash
  python price_chat.py
  ```
  Tapez ensuite le nom du produit directement dans le terminal (ex. `sac de ciment 25kg`).  
  Commandes disponibles pendant la session :
  - `set results N` : change le nombre de résultats Google analysés par magasin (1 à 10).
  - `quit`, `exit` ou `Ctrl+D` : quitte le chat.

Exemple de sortie (mode script ou chat) :

```
Résultats pour: perceuse sans fil makita
=======================================
- Leroy Merlin: prix non détecté
  Perceuse visseuse makita 18v au meilleur prix | Leroy Merlin
  https://www.leroymerlin.fr/...
- Brico Dépôt: 129,00 € (page magasin)
  Perceuse visseuse à percussion + 74 accessoires - Makita
  https://www.bricodepot.fr/...
- Castorama: 119,90 € (page magasin)
  Perceuse | Castorama
  https://www.castorama.fr/...
```

## Limitations et améliorations possibles

- Certaines enseignes protègent leur site (ex. Leroy Merlin) et empêchent la récupération automatisée du HTML : dans ce cas, aucun prix ne peut être retourné.
- Les extraits Google ne contiennent pas toujours un prix exact et la première valeur structurée trouvée peut correspondre à un autre article si la page présente plusieurs produits. Implémenter un scraping ciblé par magasin reste la solution la plus fiable, sous réserve de conformité avec leurs CGU.
- Ajouter un cache ou une base de données pour conserver l'historique des prix.
- Intégrer un service de notifications (mail, Slack, etc.) lorsque des seuils sont atteints.
