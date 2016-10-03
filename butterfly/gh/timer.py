# coding=utf-8
"""Grasshopper timer."""
try:
    import Grasshopper as gh
except ImportError:
    pass


def ghComponentTimer(ghComp, interval=600, pause=False):
    """
    Update the component at the interval like using a GH timer.

    Modified from ShapeOpGHPython.
    Github: github.com/AndersDeleuran/ShapeOpGHPython
    Authors: Anders Holden Deleuran (CITA/KADK), Mario Deuss (LGG/EPFL)

    Args:
        ghComp: Grasshopper component.
        interval: Interval in milliseconds (default: 600).
        pause: Pause timer if set to True
    """
    # return if pause
    if pause:
        return

    # Ensure interval is larger than zero
    interval = max((1, interval))

    # Get the Grasshopper document and component that owns this script
    ghDoc = ghComp.OnPingDocument()

    # Define the callback function
    def callBack(ghDoc):
        ghComp.ExpireSolution(False)

    # Update the solution
    ghDoc.ScheduleSolution(interval,
                           gh.Kernel.GH_Document.GH_ScheduleDelegate(callBack))
