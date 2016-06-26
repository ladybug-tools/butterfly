#Embedded file name: C:\Users\Administrator\Dropbox\ladybug\Butterfly\butterfly\helper.py
from __future__ import print_function
import os
import sys
from collections import OrderedDict
from subprocess import Popen, PIPE, STDOUT, call

def mkdir(directory, overwrite=True):
    if not os.path.isdir(directory):
        try:
            os.mkdir(directory)
        except Exception as e:
            raise ValueError('Failed to create %s:\n%s' % (directory, e))

    return directory


def wfile(fullPath, content):
    """write string content to a file."""
    try:
        with open(fullPath, 'wb') as outf:
            outf.write(content)

    except Exception as e:
        raise ValueError('Failed to create %s:\n%s' % (directory, e))

    return fullPath


def runbatchfile(filepath, printLog=True):
    """run an executable .bat file."""
    if not os.path.isfile(filepath):
        raise ValueError('Cannot find %s' % filepath)

    sys.stdout.flush()
    p = Popen(filepath, shell=False, stdin=PIPE)
    p.communicate(input='\n')
    if printLog:
        try:
            logfile = ".".join(filepath.split(".")[:-1]) + ".log"
            with open(logfile, 'rb') as log:
                print(' '.join(log.readlines()))
        except Exception as e:
            print('Failed to read {}:\n{}'.format(logfile, e))

def getSnappyHexMeshGeometryFeild(projectName, BFSurfaces,
                                  meshingType='triSurfaceMesh',
                                  stlFile=None):
    """Get data for Geometry as a dictionary.

    Args:
        projectName: Name of OpenFOAM case.
        BFSurfaces: List of Butterfly surfaces.
        meshingType: Meshing type. (Default: triSurfaceMesh)
        stlFile: Name of .stl file if it is different from projectName.stl

    Returns:
        A dictionary of data that can be passed to snappyHexMeshDict.
    """
    stlFile = '{}.stl'.format(projectName) if not stlFile else stlFile
    _geo = {stlFile: OrderedDict()}
    _geo[stlFile]['type'] = meshingType
    _geo[stlFile]['name'] = projectName
    _geo[stlFile]['regions'] = {}
    for bfsrf in BFSurfaces:
        if bfsrf.name not in _geo[stlFile]['regions']:
            _geo[stlFile]['regions'][bfsrf.name] = {'name': bfsrf.name}

    return _geo


def getSnappyHexMeshRefinementSurfaces(projectName, BFSurfaces, globalLevels=None):
    """Get data for MeshRefinementSurfaces as a dictionary.

    Args:
        projectName: Name of OpenFOAM case.
        BFSurfaces: List of Butterfly surfaces.
        globalLevels: Default Min, max level of surface mesh refinement.

    Returns:
        A dictionary of data that can be passed to snappyHexMeshDict.
    """
    globalLevels = (0, 0) if not globalLevels else tuple(globalLevels)
    _ref = {projectName: OrderedDict()}
    _ref[projectName]['level'] = '({} {})'.format(*(int(v) for v in globalLevels))
    _ref[projectName]['regions'] = {}
    for bfsrf in BFSurfaces:
        if not bfsrf.boundaryCondition.refLevels:
            continue
        if bfsrf.name not in _ref[projectName]['regions']:
            _ref[projectName]['regions'][bfsrf.name] = {'level': '({} {})'.format(bfsrf.boundaryCondition.refLevels[0], bfsrf.boundaryCondition.refLevels[1])}

    return _ref


def getBoundaryField(BFSurfaces, field = 'u'):
    """Get data for boundaryField as a dictionary.

    Args:
        BFSurfaces: List of Butterfly surfaces.
        parameter: One of the fileds as a string (u , p, k , epsilon, nut)

    Returns:
        A dictionary of data that can be passed to snappyHexMeshDict.
    """
    _bou = {}
    for bfsrf in BFSurfaces:
        if bfsrf.name not in _bou:
            _bc = getattr(bfsrf.boundaryCondition, field)
            _bou[bfsrf.name] = _bc.valueDict

    return _bou
