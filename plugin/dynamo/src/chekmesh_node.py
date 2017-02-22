# assign inputs
_case, _run = IN
max = average = None

if _case and _run:
    max, average = _case.calculateMeshOrthogonality()
    print "Mesh non-orthogonality max: {}, Mesh non-orthogonality average: {}".format(max, average)


# assign outputs to OUT
OUT = max, average