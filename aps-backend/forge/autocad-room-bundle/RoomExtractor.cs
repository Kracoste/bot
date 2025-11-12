using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;
using Autodesk.AutoCAD.ApplicationServices;
using Autodesk.AutoCAD.DatabaseServices;
using Autodesk.AutoCAD.Runtime;

namespace LBF.Acad.Rooms;

public class RoomExtractor : IExtensionApplication
{
    private static readonly string TargetLayer = "ROOM";

    public void Initialize()
    {
        Application.DocumentManager.MdiActiveDocument.CommandEnded += (_, _) => { };
    }

    public void Terminate()
    {
    }

    [CommandMethod("LBF_EXPORT_ROOMS")]
    public void ExportRoomsCommand()
    {
        var doc = Application.DocumentManager.MdiActiveDocument;
        var db = doc.Database;

        var rooms = new List<RoomInfo>();

        using (var tr = db.TransactionManager.StartTransaction())
        {
            var bt = (BlockTable)tr.GetObject(db.BlockTableId, OpenMode.ForRead);
            var btr = (BlockTableRecord)tr.GetObject(bt[BlockTableRecord.ModelSpace], OpenMode.ForRead);

            foreach (var id in btr)
            {
                var entity = tr.GetObject(id, OpenMode.ForRead, false, true) as Entity;
                if (entity is not Polyline polyline)
                {
                    continue;
                }

                if (!string.Equals(polyline.Layer, TargetLayer, StringComparison.OrdinalIgnoreCase))
                {
                    continue;
                }

                if (!polyline.Closed)
                {
                    continue;
                }

                rooms.Add(new RoomInfo
                {
                    Id = id.Handle.ToString(),
                    Name = polyline.GetXData(NameApplication) ?? $"ROOM-{rooms.Count + 1}",
                    AreaM2 = Math.Round(polyline.Area, 3),
                    PerimeterM = Math.Round(polyline.Length, 3),
                    BoundingBox = ToBoundingBox(polyline.GeometricExtents),
                });
            }

            tr.Commit();
        }

        var output = new
        {
            generatedAt = DateTime.UtcNow.ToString("o"),
            rooms,
        };

        var json = JsonSerializer.Serialize(output, new JsonSerializerOptions
        {
            PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
            WriteIndented = true,
        });

        var outPath = Path.Combine(Environment.GetEnvironmentVariable("ACAD_OUTPUT_DIRECTORY") ?? Directory.GetCurrentDirectory(), "rooms.json");
        Directory.CreateDirectory(Path.GetDirectoryName(outPath)!);
        File.WriteAllText(outPath, json);
        Application.ShowAlertDialog($"Export terminé : {rooms.Count} pièces.");
    }

    private const string NameApplication = "LBF_ROOM_NAME";

    private static BoundingBox ToBoundingBox(Extents3d extents)
    {
        return new BoundingBox
        {
            Min = new[] { Math.Round(extents.MinPoint.X, 3), Math.Round(extents.MinPoint.Y, 3), Math.Round(extents.MinPoint.Z, 3) },
            Max = new[] { Math.Round(extents.MaxPoint.X, 3), Math.Round(extents.MaxPoint.Y, 3), Math.Round(extents.MaxPoint.Z, 3) },
        };
    }

    private class RoomInfo
    {
        public string Id { get; set; } = string.Empty;
        public string Name { get; set; } = string.Empty;
        public double AreaM2 { get; set; }
        public double PerimeterM { get; set; }
        public BoundingBox BoundingBox { get; set; } = new();
    }

    private class BoundingBox
    {
        public double[] Min { get; set; } = Array.Empty<double>();
        public double[] Max { get; set; } = Array.Empty<double>();
    }
}
