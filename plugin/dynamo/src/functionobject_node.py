# assign inputs
_funcObject = IN[0]
funcObject = None

try:
    from butterfly.functions import Function
except ImportError as e:
    msg = '\nFailed to import butterfly. Did you install butterfly on your machine?' + \
            '\nYou can download butterfly from package manager.' + \
            '\nOpen an issue on github if you think this is a bug:' + \
            ' https://github.com/ladybug-analysis-tools/butterfly/issues'
        
    raise ImportError('{}\n{}'.format(msg, e))

if _funcObject:
    funcObject = Function.fromCppDictionary(_funcObject)

# assign outputs to OUT
OUT = (funcObject,)