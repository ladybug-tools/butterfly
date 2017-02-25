# assign inputs
_velocityVec, temperature_ = IN
inletBoundary = None

try:
    from butterfly import boundarycondition as bc
    from butterfly.fields import FixedValue
except ImportError as e:
    msg = '\nFailed to import butterfly. Did you install butterfly on your machine?' + \
            '\nYou can download butterfly from package manager.' + \
            '\nOpen an issue on github if you think this is a bug:' + \
            ' https://github.com/ladybug-analysis-tools/butterfly/issues'
        
    raise ImportError('{}\n{}'.format(msg, e))

if _velocityVec:
    _velocityVec = FixedValue(str((_velocityVec.X, _velocityVec.Y, _velocityVec.Z)).replace(',', '')) \
                   if _velocityVec \
                   else None

    temperature_ = FixedValue(str(temperature_ + 273.15)) \
                   if temperature_ \
                   else None
                   
    inletBoundary = bc.FixedInletBoundaryCondition(U=_velocityVec,
                                                   T = temperature_)


# assign outputs to OUT
OUT = (inletBoundary,)