import re
import os

def set_config(_ofrunners):
    """set config for butterfly run manager."""
    BASEFOLDERS = {
        'ESI': r'C:\Program Files (x86)',
        'blueCFD': r'C:\Program Files'
    }
    
    if not _ofrunners:
        raise ImportError('Set your installation flavor in confing.yml.')
    
    # look up for folders
    for of_runner in _ofrunners:
        try:
            base_folder = BASEFOLDERS[of_runner]
        except KeyError:
            # invalid installation option
            pass
        else:
            for f in os.listdir(base_folder):
                of_folder = os.path.join(base_folder, f)
                if not os.path.isdir(of_folder):
                    continue
                if f.startswith(of_runner):
                    # in case of two installation finds the older one but for now
                    # it is fine.
                    return {'runner': of_runner, 'of_folder': of_folder}
        
    raise ImportError('Set your installation flavor in confing.yml.')

os.chdir(os.path.dirname(__file__))
with open('config.yml') as inst:
    _ofrunners = re.findall(r'\s- (.*)', inst.read(),re.MULTILINE )

config = set_config(_ofrunners)
print('OpenFOAM installation: {}'.format(config['runner']))
