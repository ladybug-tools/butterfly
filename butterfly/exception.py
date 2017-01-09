"""Butterfly exceptions."""


class CaseFoldersNotFoundError(IOError):
    """Exception when case folder is not created."""

    _msg = 'Can\'t find the folder for this case.\n' + \
           'Save the Case before running any commands.'

    def __init__(self):
        """Init Exception."""
        IOError.__init__(self, self._msg)
