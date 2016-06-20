"BlockMeshDict class."
from foamfile import FoamFile
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
       'div(phi,k)': 'bounded Gauss linearUpwind grad(k)',
       'div((nuEff*dev(T(grad(U)))))': 'Gauss linear'
        }
    __defaultValues['laplacianSchemes'] = {'default': 'Gauss linear limited corrected 0.333'}
    __defaultValues['interpolationSchemes'] = {'default': 'linear'}
    __defaultValues['snGradSchemes'] = {'default': 'limited corrected 0.333'}
    __defaultValues['fluxRequired'] = {'default': 'no', 'p': ''}

    def __init__(self, values=None):
        """Init class."""
        FoamFile.__init__(self, name='fvSchemes', cls='dictionary',
                          location='system', defaultValues=self.__defaultValues,
                          values=values)


# fv = FvSchemes()
# fv.save(r'C:\Users\Administrator\butterfly\innerflow_3')
