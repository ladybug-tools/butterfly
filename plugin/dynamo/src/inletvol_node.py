# assign inputs
_volFlowRate, temperature_ = IN
inletBoundary = None

try:
    from butterfly import boundarycondition as bc
    from butterfly.fields import FixedValue, FlowRateInletVelocity
except ImportError as e:
    msg = '\nFailed to import butterfly. Did you install butterfly on your machine?' + \
            '\nYou can download butterfly from package manager.' + \
            '\nOpen an issue on github if you think this is a bug:' + \
            ' https://github.com/ladybug-analysis-tools/butterfly/issues'
        
    raise ImportError('{}\n{}'.format(msg, e))

if _volFlowRate:
    
    velocity =  FlowRateInletVelocity(_volFlowRate, '(0 0 0)')
    
    temperature_ = FixedValue(str(temperature_ + 273.15)) \
                   if temperature_ \
                   else None
                   
    inletBoundary = bc.FixedInletBoundaryCondition(U=velocity, T = temperature_)


# assign outputs to OUT
OUT = (inletBoundary,)