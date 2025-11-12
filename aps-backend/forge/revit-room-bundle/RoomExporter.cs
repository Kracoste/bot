using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;
using Autodesk.Revit.DB;
using Autodesk.Revit.DesignAutomation.Framework;

namespace LBF.Revit.Rooms;

public static class RoomExporter
{
    private const string OutputFileName = "rooms.json";

    public static void Execute(DesignAutomationData data)
    {
        if (data.RevitDoc is not Document doc)
        {
            throw new InvalidOperationException("No Revit document was provided to the design automation activity.");
        }

        var rooms = CollectRooms(doc);
        var outputFolder = data.OutputDirectory ?? Directory.GetCurrentDirectory();
        Directory.CreateDirectory(outputFolder);
        var outputPath = Path.Combine(outputFolder, OutputFileName);

        var payload = new
        {
            generatedAt = DateTime.UtcNow.ToString("o"),
            project = doc.ProjectInformation?.Name ?? "Unknown Project",
            rooms,
        };

        var json = JsonSerializer.Serialize(payload, new JsonSerializerOptions
        {
            PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
            WriteIndented = true,
        });

        File.WriteAllText(outputPath, json);
    }

    private static IReadOnlyList<RoomInfo> CollectRooms(Document doc)
    {
        var collector = new FilteredElementCollector(doc)
            .OfCategory(BuiltInCategory.OST_Rooms)
            .WhereElementIsNotElementType();

        var rooms = new List<RoomInfo>();
        foreach (var element in collector)
        {
            if (element is not SpatialElement room)
            {
                continue;
            }

            var area = ConvertToSquareMeters(room.Area);
            var perimeter = ComputePerimeter(room);
            var bbox = room.get_BoundingBox(null);

            rooms.Add(new RoomInfo
            {
                Id = room.Id.IntegerValue,
                Name = room.get_Parameter(BuiltInParameter.ROOM_NAME)?.AsString() ?? "Room",
                Number = room.get_Parameter(BuiltInParameter.ROOM_NUMBER)?.AsString() ?? string.Empty,
                AreaM2 = area,
                PerimeterM = perimeter,
                BoundingBox = bbox is null
                    ? null
                    : new BoundingBox
                    {
                        Min = ConvertPoint(bbox.Min),
                        Max = ConvertPoint(bbox.Max),
                    },
            });
        }

        return rooms;
    }

    private static double ConvertToSquareMeters(double internalValue)
    {
        return Math.Round(UnitUtils.ConvertFromInternalUnits(internalValue, UnitTypeId.SquareMeters), 3);
    }

    private static double ConvertToMeters(double internalValue)
    {
        return Math.Round(UnitUtils.ConvertFromInternalUnits(internalValue, UnitTypeId.Meters), 3);
    }

    private static double ComputePerimeter(SpatialElement room)
    {
        double perimeter = 0;
        var options = new SpatialElementBoundaryOptions
        {
            SpatialElementBoundaryLocation = SpatialElementBoundaryLocation.Finish,
        };

        foreach (var loop in room.GetBoundarySegments(options) ?? Enumerable.Empty<IList<BoundarySegment>>())
        {
            foreach (var segment in loop)
            {
                if (segment?.GetCurve() is Curve curve)
                {
                    perimeter += curve.Length;
                }
            }
        }

        return Math.Round(UnitUtils.ConvertFromInternalUnits(perimeter, UnitTypeId.Meters), 3);
    }

    private static double[] ConvertPoint(XYZ xyz)
    {
        return new[]
        {
            ConvertToMeters(xyz.X),
            ConvertToMeters(xyz.Y),
            ConvertToMeters(xyz.Z),
        };
    }

    private class RoomInfo
    {
        public int Id { get; set; }
        public string Name { get; set; } = string.Empty;
        public string Number { get; set; } = string.Empty;
        public double AreaM2 { get; set; }
        public double PerimeterM { get; set; }
        public BoundingBox? BoundingBox { get; set; }
    }

    private class BoundingBox
    {
        public double[] Min { get; set; } = Array.Empty<double>();
        public double[] Max { get; set; } = Array.Empty<double>();
    }
}
