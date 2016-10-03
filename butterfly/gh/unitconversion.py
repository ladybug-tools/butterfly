# coding=utf-8
"""Unit conversion to meters for Grasshopper."""
try:
    import scriptcontext as sc
    import Rhino.UnitSystem as us
except ImportError:
    pass


def convertDocumentUnitsToMeters():
    """Calculate converToMeters value for this document."""
    docUnit = sc.doc.ModelUnitSystem

    if docUnit == us.Meters:
        return 1.0000
    elif docUnit == us.Centimeters:
        return 0.010
    elif docUnit == us.Millimeters:
        return 0.0010
    elif docUnit == us.Feet:
        return 0.3050
    elif docUnit == us.Inches:
        return 0.0254
    elif docUnit == us.Kilometers:
        return 1000.0000
    else:
        print "Unknown unit. Meters will be used instead."
        return 1.0000
