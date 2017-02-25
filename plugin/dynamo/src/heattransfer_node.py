# assign inputs
_turbulenceProp_, fvSchemes_, fvSolution_, residualControl_, _relaxationFactors_ = IN
recipe = None

try:
    from butterfly.recipe import HeatTransfer
except ImportError as e:
    msg = '\nFailed to import butterfly. Did you install butterfly on your machine?' + \
            '\nYou can download butterfly from package manager.' + \
            '\nOpen an issue on github if you think this is a bug:' + \
            ' https://github.com/ladybug-analysis-tools/butterfly/issues'
        
    raise ImportError('{}\n{}'.format(msg, e))

recipe = HeatTransfer(_turbulenceProp_, fvSchemes_, fvSolution_, residualControl_,
                      _relaxationFactors_)

l = len(recipe.quantities)
q = ''.join(q + ' ..... ' if (c + 1) % 4 != 0 and c + 1 != l else q + '\n'
            for c, q in enumerate(recipe.quantities))

# assign outputs to OUT
OUT = (recipe,)