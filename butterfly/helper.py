"""Collection of useful methods."""
from __future__ import print_function
import os
import sys
from collections import OrderedDict, namedtuple
from subprocess import Popen, PIPE


def mkdir(directory, overwrite=True):
    """Make a directory.

    Args:
        directory: directory as a string.
        overwrite: A boolean to overwrite the folder if already exists.
    """
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
        raise ValueError('Failed to create %s:\n%s' % (fullPath, e))

    return fullPath


def runbatchfile(filepath, printLog=True, wait=True):
    """run an executable .bat file.

    args:
        printLog: Boolean switch to print log file to terminal once the analysis
            is over. It will only work if wait is also set to True (default: True).
        wait: Wait for analysis to finish (default: True).

    returns:
        A tuple as (success, err, process).
            success is a boolen.
            err is None in case of success otherwise the error message as a string.
            process is Popen process.
    """
    if not os.path.isfile(filepath):
        raise ValueError('Cannot find %s' % filepath)

    _success = True
    _err = None
    Log = namedtuple('Report', 'success err process')

    sys.stdout.flush()
    p = Popen(filepath, shell=False, stdin=PIPE)

    if wait:
        p.communicate(input='Y\n')

        if printLog:
            try:
                logfile = ".".join(filepath.split(".")[:-1]) + ".log"
                errfile = ".".join(filepath.split(".")[:-1]) + ".err"

                with open(logfile, 'rb') as log:
                    _lines = ' '.join(log.readlines())
                    print(_lines)

                with open(errfile, 'rb') as log:
                    _err = ' '.join(log.readlines())
                    if len(_err) > 0:
                        _success = False
                        print(_err)

            except Exception as e:
                print('Failed to read {} and {}:\n{}'.format(logfile, errfile, e))

    return Log(success=_success, err=_err, process=p)


def readLastLine(filepath, blockSize=1024):
    """
    Read the last line of a file.

    Modified from: http://www.manugarg.com/2007/04/tailing-in-python.html
    Args:
        filepath: path to file
        blockSize:  data is read in chunks of this size (optional, default=1024)

    Raises:
        IOError if file cannot be processed.
    """
    # rU is to open it with Universal newline support
    f = open(filepath, 'rU')
    offset = blockSize
    try:
        f.seek(0, 2)
        file_size = f.tell()
        while True:
            if file_size < offset:
                offset = file_size

            f.seek(-1 * offset, 2)
            read_str = f.read(offset)

            # Remove newline at the end
            if read_str[offset - 1] == '\n':
                read_str = read_str[0:-1]

            lines = read_str.split('\n')

            if len(lines) > 1:  # Got a line
                return lines[len(lines) - 1]

            if offset == file_size:   # Reached the beginning
                return read_str

            offset += blockSize
    except Exception as e:
        raise Exception(str(e))
    finally:
        f.close()


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
            _ref[projectName]['regions'][bfsrf.name] = \
                {'level': '({} {})'.format(bfsrf.boundaryCondition.refLevels[0],
                                           bfsrf.boundaryCondition.refLevels[1])}

    return _ref


def getBoundaryField(BFSurfaces, field='u'):
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


def loadSkippedProbes(logFile):
    """Return list of skipped points as tuples."""
    assert os.path.isfile(logFile), "Can't find {}.".format(logFile)
    _pts = []
    with open(logFile, 'rb') as inf:
        line = inf.readline()
        while line and not line.startswith('Time = '):
            if line.startswith('    Did not find location'):
                _pts.append(tuple(float(i) for i in line.split("(")[1].split(")")[0].split()))
            line = inf.readline()

    return _pts
