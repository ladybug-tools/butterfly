"BlockMeshDict class."
from foamfile import FoamFile
from collections import OrderedDict


class U(FoamFile):
    """U (Speed) class."""

    # set default valus for this class
    __defaultValues = OrderedDict()
    __defaultValues['dimensions'] = 'nu [0 2 -1 0 0 0 0] 1e-05'
    __defaultValues['internalField'] = 'beta [0 0 0 -1 0 0 0] 3e-03'
    __defaultValues['boundaryField'] = {}

    def __init__(self, values=None):
        """Init class."""
        FoamFile.__init__(self, name='U', cls='volVectorField',
                          location='0', defaultValues=self.__defaultValues,
                          values=values)

fv = U()
fv.save(r'C:\Users\Administrator\butterfly\innerflow_3')

# boundary field structure
# boundaryField
# {
#     room
#     {
#         type            fixedValue;
#         value           uniform (0 0 0);
#     }
#     west_window
#     {
#       type            fixedValue;
#       value           uniform (2 0 0);
#     }
#     east_window
#     {
#       type        zeroGradient;
#     }
# }
