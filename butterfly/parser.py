"""OpenFOAM/c++ dictionary parser."""
import re


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
                    # if not a list and doesn't include ';' it's a key and next item is the value
                    d[pp] = self._convertToDict(next(itp))
                else:
                    s = pp.split(';')
                    if not pp.endswith(';'):
                        # last item is a key and next item is the value
                        d[s[-1]] = self._convertToDict(next(itp))
                        s = s[:-1]
                    for ppp in s:
                        ss = ppp.split()
                        if ss:
                            d[ss[0]] = ' '.join(ss[1:])
        return d

    @staticmethod
    def _parseNested(text, left=r'[{]', right=r'[}]', sep=r','):
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
