# coding=utf-8
"""Collection of useful methods."""
from __future__ import print_function
import os
import sys
import collections
from collections import OrderedDict, namedtuple
from subprocess import Popen, PIPE
import gzip


def list_files(folder, fullpath=False):
    """list files in a folder."""
    if not os.path.isdir(folder):
        yield None

    for f in os.listdir(folder):
        if os.path.isfile(os.path.join(folder, f)):
            if fullpath:
                yield os.path.join(folder, f)
            else:
                yield f
        else:
            yield


def load_case_files(folder, fullpath=False):
    """load openfoam files from a folder."""
    files = []
    for p in ('0', 'constant', 'system', 'constant/triSurface'):
        fp = os.path.join(folder, p)
        files.append(tuple(list_files(fp, fullpath)))

    Files = namedtuple('Files', 'zero constant system stl')
    return Files(*files)


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


def write_to_file(full_path, content):
    """write string content to a file."""
    try:
        with open(full_path, 'wb') as outf:
            outf.write(content)

    except Exception as e:
        raise ValueError('Failed to create %s:\n%s' % (full_path, e))

    return full_path


def run_batch_file(filepath, wait=True):
    """run an executable .bat file.

    args:
        wait: Wait for analysis to finish (default: True).

    returns:
        Popen process.
    """
    if not os.path.isfile(filepath):
        raise ValueError('Cannot find %s' % filepath)

    sys.stdout.flush()
    p = Popen(filepath, shell=False, stdin=PIPE)

    if wait:
        (output, err) = p.communicate(input='Y\n')

    return p


def tail(file_path, lines=20):
    """Get tail of the file."""
    with open(file_path, 'rb') as f:
        total_lines_wanted = lines

        BLOCK_SIZE = 1024
        f.seek(0, 2)
        block_end_byte = f.tell()
        lines_to_go = total_lines_wanted
        block_number = -1
        # blocks of size BLOCK_SIZE, in reverse order starting from the end of
        # the file
        blocks = []
        while lines_to_go > 0 and block_end_byte > 0:
            if (block_end_byte - BLOCK_SIZE > 0):
                # read the last block we haven't yet read
                f.seek(block_number * BLOCK_SIZE, 2)
                blocks.append(f.read(BLOCK_SIZE))
            else:
                # file too small, start from begining
                f.seek(0, 0)
                # only read what was not read
                blocks.append(f.read(block_end_byte))
            lines_found = blocks[-1].count('\n')
            lines_to_go -= lines_found
            block_end_byte -= BLOCK_SIZE
            block_number -= 1
        all_read_text = ''.join(reversed(blocks))

        return '\n'.join(all_read_text.splitlines()[-total_lines_wanted:])


def read_last_line(filepath, block_size=1024):
    """Read the last line of a file.

    Modified from: http://www.manugarg.com/2007/04/tailing-in-python.html
    Args:
        filepath: path to file
        block_size:  data is read in chunks of this size (optional, default=1024)

    Raises:
        IOError if file cannot be processed.
    """
    # rU is to open it with Universal newline support
    f = open(filepath, 'rU')
    offset = block_size
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

            offset += block_size
    except Exception as e:
        raise Exception(str(e))
    finally:
        f.close()


def update_dict(d, u):
    """Update a dictionary witout overwriting the currect values.

    source: http://stackoverflow.com/a/3233356/4394669
    Args:
        d: original dictionary.
        u: new dictionary.
    """
    for k, v in u.iteritems():
        if isinstance(v, collections.Mapping):
            r = update_dict(d.get(k, {}), v)
            d[k] = r
        else:
            d[k] = u[k]
    return d


def get_snappyHexMesh_geometry_feild(project_name, bf_geometries,
                                     meshing_type='triSurfaceMesh',
                                     stl_file=None):
    """Get data for Geometry as a dictionary.

    Args:
        project_name: Name of OpenFOAM case.
        bf_geometries: List of Butterfly geometries.
        meshing_type: Meshing type. (Default: triSurfaceMesh)
        stl_file: Name of .stl file if it is different from project_name.stl

    Returns:
        A dictionary of data that can be passed to snappyHexMeshDict.
    """
    stl_file = '{}.stl'.format(project_name) if not stl_file else stl_file
    _geo = {stl_file: OrderedDict()}
    _geo[stl_file]['type'] = meshing_type
    _geo[stl_file]['name'] = project_name
    _geo[stl_file]['regions'] = {}
    for bfgeo in bf_geometries:
        if bfgeo.name not in _geo[stl_file]['regions']:
            _geo[stl_file]['regions'][bfgeo.name] = {'name': bfgeo.name}

    return _geo


def get_snappyHexMesh_refinement_surfaces(
        project_name, bf_geometries, global_levels=None):
    """Get data for MeshRefinementSurfaces as a dictionary.

    Args:
        project_name: Name of OpenFOAM case.
        bf_geometries: List of Butterfly geometries.
        global_levels: Default Min, max level of geometry mesh refinement.

    Returns:
        A dictionary of data that can be passed to snappyHexMeshDict.
    """
    global_levels = (0, 0) if not global_levels else tuple(global_levels)
    _ref = {project_name: OrderedDict()}
    _ref[project_name]['level'] = '({} {})'.format(*(int(v) for v in global_levels))
    _ref[project_name]['regions'] = {}
    for bfgeo in bf_geometries:
        if not bfgeo.refinementLevels:
            continue
        if bfgeo.name not in _ref[project_name]['regions']:
            _ref[project_name]['regions'][bfgeo.name] = \
                {'level': '({} {})'.format(int(bfgeo.refinementLevels[0]),
                                           int(bfgeo.refinementLevels[1]))}

    return _ref


def get_snappyHexMesh_surface_layers(bf_geometries):
    """Get data for n_surface_layers as a dictionary.

    Args:
        bf_geometries: List of Butterfly geometries.
    Returns:
        A dictionary of data that can be passed to snappyHexMeshDict.
    """
    _ref = OrderedDict()
    for bfgeo in bf_geometries:
        if not bfgeo.nSurfaceLayers:
            continue
        if bfgeo.name not in _ref:
            _ref[bfgeo.name] = {'nSurfaceLayers': str(bfgeo.nSurfaceLayers)}

    return _ref


def get_boundary_field_from_geometries(bf_geometries, field='U'):
    """Get data for boundaryField as a dictionary.

    Args:
        bf_geometries: List of Butterfly geometries.
        parameter: One of the fileds as a string (U , p, k , epsilon, nut)

    Returns:
        A dictionary of data that can be passed to snappyHexMeshDict.
    """
    _bou = {}
    for bfgeo in bf_geometries:
        if bfgeo.name not in _bou:
            if hasattr(bfgeo.boundary_condition, 'isBoundingBoxBoundaryCondition'):
                # bounding box for meshing. should not be included in files
                continue
            _bc = getattr(bfgeo.boundary_condition, field)
            _bou[bfgeo.name] = _bc.value_dict

    return _bou


def load_skipped_probes(log_file):
    """Return list of skipped points as tuples."""
    assert os.path.isfile(log_file), "Can't find {}.".format(log_file)
    _pts = []
    with open(log_file, 'rb') as inf:
        line = inf.readline()
        while line and not line.startswith('Time = '):
            if line.startswith('    Did not find location'):
                _pts.append(
                    tuple(float(i) for i in line.split("(")[1].split(")")[0].split()))
            line = inf.readline()

    return _pts


def load_probes_from_postProcessing_file(probes_folder, field):
    """Return a generator of probes as tuples.

    Args:
        probes_folder: full path to probes folder.
        field: Probes field (e.g. U, p, T).
    """
    if not os.path.isdir(probes_folder):
        raise ValueError(
            'Failed to find probes folder folder at {}'.format(probes_folder))

    folders = [os.path.join(probes_folder, f) for f in os.listdir(probes_folder)
               if (os.path.isdir(os.path.join(probes_folder, f)) and
                   f.isdigit())]

    # sort based on last modified
    folders = sorted(folders, key=lambda folder:
                     max(tuple(os.stat(os.path.join(folder, f)).st_mtime
                               for f in os.listdir(folder))))

    # load the last line in the file
    _f = os.path.join(probes_folder, str(folders[-1]), field)

    assert os.path.isfile(_f), 'Cannot find {}!'.format(_f)

    with open(_f, 'rb') as inf:
        for line in inf:
            if line.startswith('#        Probe'):
                break
            yield tuple(float(v) for v in line.strip().split('(')[-1][:-1].split())


def load_probe_values_from_folder(probes_folder, field):
    """Return OpenFOAM probe values for a field for the last timestep.

    Args:
        field: Probes field (e.g. U, p, T).
    """
    if not os.path.isdir(probes_folder):
        raise ValueError(
            'Failed to find probes folder folder at {}'.format(probes_folder))

    folders = [os.path.join(probes_folder, f) for f in os.listdir(probes_folder)
               if (os.path.isdir(os.path.join(probes_folder, f)) and
                   f.isdigit())]

    # sort based on last modified
    folders = sorted(folders, key=lambda folder:
                     max(tuple(os.stat(os.path.join(folder, f)).st_mtime
                               for f in os.listdir(folder))))

    # load the last line in the file
    _f = os.path.join(probes_folder, str(folders[-1]), field)

    assert os.path.isfile(_f), 'Cannot find {}!'.format(_f)
    _res = read_last_line(_f).split()[1:]

    # convert values to tuple or number
    _rawres = tuple(d.strip() for d in read_last_line(_f).split()
                    if d.strip())[1:]

    try:
        # it's a number
        _res = tuple(float(r) for r in _rawres)
    except ValueError:
        try:
            # it's a vector
            _res = tuple(eval(','.join(_rawres[3 * i: 3 * (i + 1)]))
                         for i in range(int(len(_rawres) / 3)))
        except Exception as e:
            raise Exception('\nFailed to load probes:\n{}'.format(e))

    return _res


def load_probes_and_values_from_sample_file(fp):
    """Load probes and respected values from the results of a sample file."""
    with open(fp, 'rb') as inf:
        for line in inf:
            res = (float(v) for v in line.split())
            x = res.next()
            y = res.next()
            z = res.next()
            v = tuple(res)
            if len(v) == 1:
                yield (x, y, z), float(v[0])
            else:
                yield (x, y, z), v


def load_of_points_file(path_to_file):
    """Return points as a generator of tuples."""
    assert os.path.isfile(path_to_file), \
        'Failed to find points file at {}'.format(path_to_file)

    if path_to_file.endswith('.gz'):
        pfile = gzip.open(path_to_file, 'rb')
    else:
        pfile = open(path_to_file, 'rb')

    try:
        for l in pfile:
            if l.strip().startswith('(') and l.strip().endswith(')'):
                yield eval(','.join(l.split()))
    finally:
        pfile.close()


def load_of_faces_file(path_to_file, inner_mesh=True):
    """Return faces indecies as a generator of tuples."""
    assert os.path.isfile(path_to_file), \
        'Failed to find faces file: {}'.format(path_to_file)

    if path_to_file.endswith('.gz'):
        ffile = gzip.open(path_to_file, 'rb')
    else:
        ffile = open(path_to_file, 'rb')

    if not inner_mesh:
        p, f = os.path.split(path_to_file)
        fins = load_of_boundary_file(os.path.join(p, f.replace('faces', 'boundary')))
        try:
            fin = -1
            for l in ffile:
                tl = l.strip()
                try:
                    if tl[1] == '(' and tl.endswith(')'):
                        fin += 1  # add to face number
                        if fin in fins:
                            yield eval(','.join(tl[1:].split()))
                except IndexError:
                    continue
        finally:
            ffile.close()
    else:
        try:
            for l in ffile:
                tl = l.strip()
                try:
                    if tl[1] == '(' and tl.endswith(')'):
                        yield eval(','.join(tl[1:].split()))
                except IndexError:
                    continue
        finally:
            ffile.close()


def load_of_boundary_file(path_to_file):
    """Return Face indecies for boundary faces as a set."""
    assert os.path.isfile(path_to_file), \
        'Failed to find boundary file: {}'.format(path_to_file)

    ind = []
    with open(path_to_file, 'rb') as bf:
        for line in bf:
            line = line.strip()
            if line.startswith('nFaces'):
                count = int(line.split()[-1][:-1])
                nl = next(bf)
                st = int(nl.split()[-1][:-1])
                ind.append(xrange(st, st + count))

    return {i for rng in ind for i in rng}
