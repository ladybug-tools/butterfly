# assign inputs
_case, fullpath_ = IN
zero = constant = triSurface = system = None

import os

def listfiles(folder, fullpath):
    for f in os.listdir(folder):
        if os.path.isfile(os.path.join(folder, f)):
            if fullpath:
                yield os.path.normpath(os.path.join(folder, f))
            else:
                yield os.path.normpath(f)

if _case:
    if isinstance(_case, str):
        projectDir = _case.replace('\\\\','/').replace('\\','/')
    else:
        try:
            projectDir = _case.projectDir
        except:
            raise ValueError('Invaild input for _case.')
    
    files = []
    for p in ('0', 'constant', 'constant/triSurface', 'system'):
        files.append(listfiles(os.path.join(projectDir, p), fullpath_))
    
    zero, constant, triSurface, system = files


# assign outputs to OUT
OUT = zero, constant, triSurface, system