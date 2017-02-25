# assign inputs
temperature_ = IN[0]
wallBoundary = None

try:
    from butterfly.boundarycondition import IndoorWallBoundaryCondition
    from butterfly.fields import FixedValue
except ImportError as e:
    msg = '\nFailed to import butterfly. Did you install butterfly on your machine?' + \
            '\nYou can download butterfly from package manager.' + \
            '\nOpen an issue on github if you think this is a bug:' + \
            ' https://github.com/ladybug-analysis-tools/butterfly/issues'
        
    raise ImportError('{}\n{}'.format(msg, e))

temperature_ = FixedValue(str(temperature_ + 273.15)) \
               if temperature_ \
               else None

wallBoundary = IndoorWallBoundaryCondition(T=temperature_)


# assign outputs to OUT
OUT = (wallBoundary,)