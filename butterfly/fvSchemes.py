# coding=utf-8
"""Finite Volume Schemes class."""
from version import Version
from foamfile import FoamFile, foamFileFromFile
from collections import OrderedDict


class FvSchemes(FoamFile):
    """Finite Volume Schemes class."""

    # set default valus for this class
    __defaultValues = OrderedDict()
    __defaultValues['ddtSchemes'] = {'default': 'steadyState'}
    __defaultValues['gradSchemes'] = {'default': 'cellLimited leastSquares 1'}
    __defaultValues['divSchemes'] = {
        'default': 'none',
        'div(phi,U)': 'bounded Gauss linearUpwindV grad(U)',
        'div(phi,epsilon)': 'bounded Gauss linearUpwind grad(epsilon)',
        'div(phi,k)': 'bounded Gauss linearUpwind grad(k)'
    }

    if float(Version.OFVer) < 3:
        __defaultValues['divSchemes']['div((nuEff*dev(T(grad(U)))))'] = 'Gauss linear'
    else:
        __defaultValues['divSchemes']['div((nuEff*dev2(T(grad(U)))))'] = 'Gauss linear'

    __defaultValues['laplacianSchemes'] = {'default': 'Gauss linear limited corrected 0.333'}
    __defaultValues['interpolationSchemes'] = {'default': 'linear'}
    __defaultValues['snGradSchemes'] = {'default': 'limited corrected 0.333'}
    __defaultValues['fluxRequired'] = {'default': 'no', 'p': ''}

    # first and second order of divSchemes
    divSchemesCollector = {
        0: '// first order\n'
           'divSchemes\n'
           '{\n'
           '    default     none;\n'
           '    div(phi,epsilon)       bounded Gauss upwind default;\n'
           '    div(phi,U)      bounded Gauss upwind grad(U);\n'
           '    div((nuEff*dev2(T(grad(U)))))   Gauss linear;\n'
           '    div(phi,k)      bounded Gauss upwind grad(k);\n'
           '}\n',
        1: '// second order\n'
           'divSchemes\n'
           '{\n'
           '    default     none;\n'
           '    div(phi,epsilon)    bounded Gauss linearUpwind grad(epsilon);\n'
           '    div(phi,U)      bounded Gauss linearUpwind grad(U);\n'
           '    div((nuEff*dev2(T(grad(U)))))       Gauss linear;\n'
           '    div(phi,k)      bounded Gauss linearUpwind grad(k);\n'
           '}'
    }

    def __init__(self, values=None):
        """Init class."""
        FoamFile.__init__(self, name='fvSchemes', cls='dictionary',
                          location='system', defaultValues=self.__defaultValues,
                          values=values)

    @classmethod
    def fromFile(cls, filepath):
        """Create a FoamFile from a file.

        Args:
            filepath: Full file path to dictionary.
        """
        return cls(values=foamFileFromFile(filepath, cls.__name__))

    @classmethod
    def fromRecipe(cls, recipe=0):
        """Create an fvSchemes from recipe id.

        0 > SteadyIncompressible
        1 > HeatTransfer
        """
        _cls = cls()
        if recipe == 0:
            return _cls
        elif recipe == 1:
            # update divSchemes
            _cls.values['divSchemes']['div(phi,T)'] = \
                'bounded Gauss linearUpwind default'
            return _cls

    @classmethod
    def fromMeshOrthogonality(cls, averageOrthogonality=45):
        """Init fvSchemes based on mesh orthogonality.

        Check pp. 45-50 of this document:
        http://www.dicat.unige.it/guerrero/oftraining/9tipsandtricks.pdf
        """
        return cls(values=cls.getValuesFromMeshOrthogonality(
            averageOrthogonality))

    # TODO: Add changes OpenFOAM version check for dev values.
    @staticmethod
    def getValuesFromMeshOrthogonality(averageOrthogonality=45):
        """Get scheme values from orthogonality."""
        if averageOrthogonality > 80:
            _values = {
                'gradSchemes': {
                    'default': 'faceLimited leastSquares 1.0',
                    'grad(U)': 'faceLimited leastSquares 1.0'
                },

                'divSchemes': {
                    'div(phi,U)': 'bounded Gauss linearUpwind grad(U)',
                    'div(phi,omega)': 'bounded Gauss upwind',
                    'div(phi,k)': 'bounded Gauss upwind',
                    'div((nuEff*dev2(T(grad(U)))))': 'Gauss linear',
                    'div(phi,epsilon)': 'bounded Gauss linearUpwind grad(epsilon)'
                },

                'laplacianSchemes': {
                    'default': 'Gauss linear limited 0.333'
                },

                'snGradSchemes': {
                    'default': 'limited 0.333'
                }
            }
        elif 70 <= averageOrthogonality <= 80:
            _values = {
                'gradSchemes': {
                    'default': 'cellLimited leastSquares 1.0',
                    'grad(U)': 'cellLimited leastSquares 1.0'
                },

                'divSchemes': {
                    'div(phi,U)': 'bounded Gauss linearUpwind grad(U)',
                    'div(phi,omega)': 'bounded Gauss upwind',
                    'div(phi,k)': 'bounded Gauss upwind',
                    'div((nuEff*dev2(T(grad(U)))))': 'Gauss linear',
                    'div(phi,epsilon)': 'bounded Gauss linearUpwind grad(epsilon)'
                },

                'laplacianSchemes': {
                    'default': 'Gauss linear limited 0.5'
                },

                'snGradSchemes': {
                    'default': 'limited 0.5'
                }
            }

        elif 60 <= averageOrthogonality < 70:
            _values = {
                'gradSchemes': {
                    'default': 'cellMDLimited Gauss linear 0.5',
                    'grad(U)': 'cellMDLimited Gauss linear 0.5'
                },

                'divSchemes': {
                    'div(phi,U)': 'bounded Gauss linearUpwind grad(U)',
                    'div(phi,omega)': 'bounded Gauss linearUpwind default',
                    'div(phi,k)': 'bounded Gauss linearUpwind default',
                    'div((nuEff*dev2(T(grad(U)))))': 'Gauss linear',
                    'div(phi,epsilon)': 'bounded Gauss linearUpwind grad(epsilon)'
                },

                'laplacianSchemes': {
                    'default': 'Gauss linear limited 0.777'
                },

                'snGradSchemes': {
                    'default': 'limited 0.777'
                }
            }
        elif 40 <= averageOrthogonality < 60:
            _values = {
                'gradSchemes': {
                    'default': 'cellMDLimited Gauss linear 0.5',
                    'grad(U)': 'cellMDLimited Gauss linear 0.5'
                },

                'divSchemes': {
                    'div(phi,U)': 'bounded Gauss linearUpwind grad(U)',
                    'div(phi,omega)': 'bounded Gauss linearUpwind default',
                    'div(phi,k)': 'bounded Gauss linearUpwind default',
                    'div((nuEff*dev2(T(grad(U)))))': 'Gauss linear',
                    'div(phi,epsilon)': 'bounded Gauss linearUpwind grad(epsilon)'
                },

                'laplacianSchemes': {
                    'default': 'Gauss linear limited 1.0'
                },

                'snGradSchemes': {
                    'default': 'limited 1.0'
                }
            }
        else:
            # smaller than 40
            _values = {
                'gradSchemes': {
                    'default': 'cellMDLimited Gauss linear 0.333',
                    'grad(U)': 'cellMDLimited Gauss linear 0.333'
                },

                'divSchemes': {
                    'div(phi,U)': 'bounded Gauss linearUpwind grad(U)',
                    'div(phi,omega)': 'bounded Gauss linearUpwind default',
                    'div(phi,k)': 'bounded Gauss linearUpwind default',
                    'div((nuEff*dev2(T(grad(U)))))': 'Gauss linear',
                    'div(phi,epsilon)': 'bounded Gauss linearUpwind grad(epsilon)'
                },

                'laplacianSchemes': {
                    'default': 'Gauss linear orthogonal'
                },

                'snGradSchemes': {
                    'default': 'orthogonal'
                }
            }

        return _values
