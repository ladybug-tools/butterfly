"""OpenFOAM/c++ dictionary parser."""
import re
from collections import OrderedDict


class CppDictParser(object):
    """Parse OpenFOAM dictionary to Python dictionary.

    Use values property to get the dictionary.

    Attributes:
        text: OpenFOAM dictionary as a single multiline string.
    """

    def __init__(self, text):
        """Init an OpenFOAMDictParser."""
        _t = self._removeComments(text)
        _t = ''.join(_t.replace('\r\n', ' ').replace('\n', ' '))
        self.__values = self._convertToDict(self._parseNested(_t))

    @classmethod
    def fromFile(cls, filepath):
        """Create a parser from an OpenFOAM file."""
        with open(filepath) as f:
            return cls('\n'.join(f.readlines()))

    @property
    def values(self):
        """Get OpenFOAM dictionary values as a python dictionary."""
        return self.__values

    @staticmethod
    def _removeComments(code):
        """Remove comments from c++ codes."""
        # remove all occurance streamed comments (/*COMMENT */) from string
        text = re.sub(re.compile('/\*.*?\*/', re.DOTALL), '', code)
        # remove all occurance singleline comments (//COMMENT\n ) from string
        return re.sub(re.compile('//.*?\n'), '', text)

    def _convertToDict(self, parsed):
        """Convert parsed list to a dictionary."""
        d = dict()
        itp = iter(parsed)
        for pp in itp:
            if not isinstance(pp, list):
                if pp.find(';') == -1:
                    # if not a list and doesn't include ';' it's a key and
                    # next item is the value
                    d[pp.strip()] = self._convertToDict(next(itp))
                else:
                    s = pp.split(';')
                    if not pp.endswith(';'):
                        # last item is a key and next item is the value
                        d[s[-1].strip()] = self._convertToDict(next(itp))
                        s = s[:-1]
                    for ppp in s:
                        ss = ppp.split()
                        if ss:
                            d[ss[0].strip()] = ' '.join(ss[1:]).strip()
        return d

    @staticmethod
    def _parseNested(text, left=r'[{]', right=r'[}]', sep='#'):
        """Parse nested.

        http://stackoverflow.com/a/14715850/4394669
        """
        pat = r'({}|{}|{})'.format(left, right, sep)
        tokens = re.split(pat, text)
        stack = [[]]
        for x in tokens:
            if not x.strip() or re.match(sep, x):
                continue
            if re.match(left, x):
                # Nest a new list inside the current list
                current = []
                stack[-1].append(current)
                stack.append(current)
            elif re.match(right, x):
                stack.pop()
                if not stack:
                    raise ValueError('error: opening bracket is missing')
            else:
                stack[-1].append(x.strip())
        if len(stack) > 1:
            print(stack)
            raise ValueError('error: closing bracket is missing')
        return stack.pop()

    def ToString(self):
        """Overwrite ToString method."""
        return self.__repr__()

    def __repr__(self):
        """Class representation."""
        return '{}'.format(self.values)


class ResidualParser(object):
    """Paeser for residual values from a log file.

    Attributes:
        filepath: Full file path to .log file.
        parser: If ture Parser will start parsing the values once initiated.
    """

    def __init__(self, filepath, parse=True):
        """Init residual parser."""
        self.filepath = filepath
        self.__residuals = OrderedDict()
        if parse:
            self.parse()

    def parse(self):
        """Parse the log file."""
        # open the file
        # try to find the first line with Time =
        # send the file to a recursive residualParser
        try:
            with open(self.filepath, 'rb') as f:
                for line in f:
                    if line.startswith('Time ='):
                        self.timestep = self.__getTime(line)
                        self.__residuals[self.timestep] = {}
                        self.__parseResiduals(f)
        except Exception as e:
            raise 'Failed to parse {}:\n\t{}'.format(self.filepath, e)

    @property
    def residuals(self):
        """Get residuals as a dictionary."""
        return self.__residuals

    @property
    def timeRange(self):
        """Get time range as a tuple."""
        _times = self.getTimes()
        return _times[0], _times[-1]

    def getTimes(self):
        """Get time steps."""
        return self.__residuals.keys()

    def getResiduals(self, quantity, timeRange):
        """Get residuals for a quantity."""
        if quantity not in self.quantities:
            print 'Invalid quantity [{}]. Try from the list below:\n{}' \
                .format(quantity, self.quantities)
            return ()

        if not timeRange:
            return (v[quantity] for v in self.__residuals.itervalues())
        else:
            availableTimeRange = self.timeRange
            try:
                t0 = max(availableTimeRange[0], timeRange[0])
                t1 = min(availableTimeRange[1], timeRange[1])
            except IndexError as e:
                raise ValueError('Failed to read timeRange:\n{}'.format(e))

            return (self.__residuals[int(t)][quantity] for t in xrange(t0, t1))

    @staticmethod
    def __getTime(line):
        return int(line.split('Time =')[-1])

    def __parseResiduals(self, f):
        for line in f:
            if not line.startswith('Time ='):
                try:
                    # quantity, Initial residual, Final residual, No Iterations
                    q, ir, fr, ni = line.split(':  Solving for ')[1].split(',')
                    self.__residuals[self.timestep][q] = ir.split('= ')[-1]
                except IndexError:
                    pass
            else:
                self.timestep = self.__getTime(line)
                self.__residuals[self.timestep] = {}

        self.quantities = self.__residuals[self.timestep].keys()
