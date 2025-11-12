using System;
using Autodesk.Revit.ApplicationServices;
using Autodesk.Revit.DB;
using Autodesk.Revit.DesignAutomation;
using Autodesk.Revit.DesignAutomation.Framework;

namespace LBF.Revit.Rooms;

public class RoomExporterApp : IExternalDBApplication
{
    public ExternalDBApplicationResult OnStartup(ControlledApplication application)
    {
        DesignAutomationBridge.DesignAutomationReadyEvent += HandleDesignAutomationReady;
        return ExternalDBApplicationResult.Succeeded;
    }

    public ExternalDBApplicationResult OnShutdown(ControlledApplication application)
    {
        DesignAutomationBridge.DesignAutomationReadyEvent -= HandleDesignAutomationReady;
        return ExternalDBApplicationResult.Succeeded;
    }

    private static void HandleDesignAutomationReady(object sender, DesignAutomationReadyEventArgs e)
    {
        e.Succeeded = true;
        RoomExporter.Execute(e.DesignAutomationData);
    }
}
