# LBF Revit Rooms Bundle (Design Automation 2025)

Bundle qui sera publié sur Autodesk APS – Design Automation pour Revit 2025. Il ouvre un modèle, récupère toutes les pièces (`Rooms`) et exporte un fichier `rooms.json` contenant :

```json
{
  "generatedAt": "2025-01-05T11:12:13.000Z",
  "project": "Projet X",
  "rooms": [
    {
      "id": 12345,
      "name": "Salle de réunion",
      "number": "1.05",
      "areaM2": 32.4,
      "perimeterM": 24.1,
      "boundingBox": { "min": [0.0, 0.0, 0.0], "max": [5.7, 4.2, 3.0] }
    }
  ]
}
```

## Pré-requis

- **Revit Design Automation 2025** (engine `Autodesk.Revit+2025`)
- .NET Framework 4.8 SDK
- Paquet NuGet `Autodesk.Revit.DesignAutomationFramework`

## Structure

```
forge/revit-room-bundle/
├─ App.cs                  // IExternalDBApplication -> branche le handler DA
├─ RoomExporter.cs         // logique d'extraction + JSON
├─ LBF.Revit.Rooms.csproj  // projet net48
├─ PackageContents.xml     // manifest bundle
└─ README.md
```

## Compilation

1. Installe les dépendances NuGet :
   ```bash
   cd forge/revit-room-bundle
   dotnet restore
   ```
2. Défini la variable d'environnement `RevitApiPath` pointant vers les DLL Revit 2025 (ou modifie le `HintPath` dans le `.csproj`).
3. Compile :
   ```bash
   dotnet build -c Release
   ```
4. Crée la structure de bundle :
   ```
   LBF.Revit.Rooms.bundle/
     ├─ PackageContents.xml
     └─ Contents/Resources/LBF.Revit.Rooms.dll
   ```
5. Zip le dossier (`LBF.Revit.Rooms.bundle.zip`) pour l'uploader sur APS.

## Publication APS (scripts)

Utilise `forge/scripts/publish_revit_bundle.sh` (variables `APS_CLIENT_ID`, `APS_CLIENT_SECRET`, `APP_BUNDLE_ID`, `ACTIVITY_ID`, `ENGINE` configurables) :

```bash
cd aps-backend/forge/scripts
APP_BUNDLE_ID=LBF-Revit-Rooms-v1 \
ACTIVITY_ID=LBF-Revit-Rooms-v1 \
./publish_revit_bundle.sh ../revit-room-bundle/LBF.Revit.Rooms.bundle.zip
```

Cela publie l'AppBundle puis crée l'Activity avec les paramètres `inputRvt` (GET) et `outputJson` (PUT). Le backend consommera cette Activity lorsqu’il détecte un fichier `.rvt`.
