# assign inputs
_bType_, _alphat_, _U_, _p_, _p_rgh_, _k_, _epsilon_, _nut_, _T_ = IN
boundary = None

try:
    from butterfly import boundarycondition
except ImportError as e:
    msg = '\nFailed to import butterfly. Did you install butterfly on your machine?' + \
            '\nYou can download butterfly from package manager.' + \
            '\nOpen an issue on github if you think this is a bug:' + \
            ' https://github.com/ladybug-analysis-tools/butterfly/issues'
        
    raise ImportError('{}\n{}'.format(msg, e))

_bType_ = 'patch' if not _bType_ else _bType_

boundary = boundarycondition.BoundaryCondition(
    _bType_, U=_U_, p=_p_, k=_k_, epsilon=_epsilon_,
    nut=_nut_, alphat=_alphat_, p_rgh=_p_rgh_, T=_T_
)

boundary = boundary.duplicate()

# assign outputs to OUT
OUT = (boundary,)