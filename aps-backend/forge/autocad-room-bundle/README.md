# LBF AutoCAD Rooms Bundle

Bundle Design Automation AutoCAD (2024/2025) pour extraire les pièces dessinées via des polylignes fermées situées sur le calque `ROOM`. Résultat exporté dans `rooms.json` (identique au bundle Revit).

## Structure

```
forge/autocad-room-bundle/
├─ RoomExtractor.cs            # Commande LBF_EXPORT_ROOMS
├─ LBF.Acad.Rooms.csproj
├─ PackageContents.xml
└─ README.md
```

## Pré-requis

- AutoCAD Managed .NET (AcMgd, AcDbMgd, AcCoreMgd) — version alignée avec l’engine Design Automation (AutoCAD+24_2 ou supérieur).
- .NET Framework 4.8 SDK.

## Compilation

1. Définis la variable `AutoCADApiPath` (chemin vers les DLL AutoCAD).
2. Compile :
   ```bash
   cd forge/autocad-room-bundle
   dotnet restore
   dotnet build -c Release
   ```
3. Crée le `.bundle` :
   ```
   LBF.Acad.Rooms.bundle/
     ├─ PackageContents.xml
     └─ Contents/Resources/LBF.Acad.Rooms.dll
   ```
4. Zip le dossier (`LBF.Acad.Rooms.bundle.zip`) pour l’envoyer sur APS.

## Publication APS

Utilise `forge/scripts/publish_autocad_bundle.sh` :

```bash
cd aps-backend/forge/scripts
APP_BUNDLE_ID=LBF-Acad-Rooms-v1 \
ACTIVITY_ID=LBF-Acad-Rooms-v1 \
./publish_autocad_bundle.sh ../autocad-room-bundle/LBF.Acad.Rooms.bundle.zip
```

Le script upload l'AppBundle et crée l'Activity avec `inputDwg` (GET) / `outputJson` (PUT). `routeToPipeline` déclenchera cette Activity pour les fichiers DWG ou PDF vectoriel converti.
