## APS Backend (Next.js + Node)

Ce projet expose les premiers endpoints nécessaires au pipeline Autodesk Platform Services (APS) pour analyser des plans (RVT/DWG/IFC/PDF vectoriel) puis renvoyer un JSON unifié (`rooms.json`). Il est découpé pour rester maintenable et accueillir les futures intégrations (Design Automation, Model Derivative, vision/calibration).

### Arborescence clé

```
src/
 ├─ app/api/
 │   ├─ aps/token          → OAuth serveur → APS
 │   ├─ aps/viewer-urn     → URN OSS pour le viewer
 │   ├─ plan/upload        → upload + stockage local
 │   ├─ plan/process       → routage pipeline (stub APS)
 │   └─ plan/result        → lecture d'un job simulé
 ├─ lib/
 │   ├─ env.ts             → validation des variables APS
 │   ├─ detectors/         → détection du type de fichier
 │   ├─ processors/        → orchestration pipeline (stub)
 │   ├─ repository/        → persistance fichier JSON
 │   └─ storage/           → sauvegarde locale des uploads
 └─ types/rooms.ts         → schéma de sortie unifié
```

### Pré-requis

1. Installer les dépendances
   ```bash
   cd aps-backend
   npm install
   ```
2. Copier `.env.example` vers `.env.local` (ou `.env`) et renseigner vos identifiants APS :
   ```bash
   APS_CLIENT_ID="xxx"
   APS_CLIENT_SECRET="xxx"
   APS_BUCKET="votre-bucket-oss"
   ```
3. Lancer le serveur en mode dev :
   ```bash
   npm run dev
   ```
   Les routes API sont disponibles sur `http://localhost:3000/api/...`.

### Endpoints disponibles (MVP)

| Méthode | Route                       | Description |
| ------- | --------------------------- | ----------- |
| POST    | `/api/aps/token`            | Récupère un token APS via client credentials (scopes data:read/write + bucket). |
| POST    | `/api/plan/upload`          | Upload multipart (`file`) → sauvegarde locale + métadonnées (JSON). Retourne `fileId`. |
| POST    | `/api/plan/process`         | Body `{ fileId }` → détecte RVT/DWG/IFC/PDF/IMG et route vers le pipeline APS (stub). Retourne `jobId`. |
| GET     | `/api/plan/result?jobId=`   | Récupère le résultat (simulé) du job. En attendant l’intégration APS réelle, un `rooms.json` fictif est généré. |
| GET     | `/api/aps/viewer-urn`       | Fournit le `urn` (OSS) stocké pour un fichier, utile au Viewer APS (actuellement `null`). |

> ⚠️ Les pipelines APS (Design Automation + Model Derivative) ne sont pas encore branchés. `routeToPipeline` crée aujourd’hui un `rooms.json` simulé et marque le job comme `processed`. Il suffit ensuite de remplacer cette fonction par les appels réels (upload OSS, WorkItem, polling, etc.).

### Stockage local

- Fichiers uploadés : `uploads/<fileId>.<ext>`
- Métadonnées : `data/files.json`
- Résultats simulés : `data/jobs/<jobId>.json`

Cette structure facilite le remplacement futur par une base de données ou un stockage cloud (S3/OSS).

### Étapes suivantes

1. **Bundles Autodesk** : développer/publier les bundles Revit & AutoCAD (`LBF-Revit-Rooms-v1`, `LBF-Acad-Rooms-v1`, etc.) puis remplacer `routeToPipeline`.
2. **OSS intégration** : uploader les fichiers dans le bucket APS (`APS_BUCKET`) et stocker le `objectId`/`urn`.
3. **Model Derivative IFC** : implémenter la requête `POST /modelderivative/v2/designdata/job` pour les fichiers IFC puis parser `properties`.
4. **Vision + calibration** : ajouter un pipeline pour les plans raster (JPG/PNG/PDF image) lorsque les spécifications seront finalisées.

### Scripts / maintenance

- `npm run lint` pour ESLint.
- `npm run dev` pour lancer le serveur Next.js avec hot reload.

Ajoutez vos scripts Forge (publication d’AppBundle/Activity, WorkItem) dans un dossier `forge/scripts/` lorsque vous serez prêts à connecter les pipelines réels.
