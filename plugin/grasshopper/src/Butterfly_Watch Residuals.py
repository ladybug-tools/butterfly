# Butterfly: A Plugin for CFD Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# This file is part of Butterfly.
#
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Watch residual values for a solution.

-

    Args:
        _solution: Butterfly solution.
        _quants_: Residual quantities. If empty recipe's quantities will be used.
        
    Returns:
        residualValues: List of residual values for the latest timestep.
"""

def tail(filePath, lines=20):
    with open(filePath, 'rb') as f:
        total_lines_wanted = lines

        BLOCK_SIZE = 1024
        f.seek(0, 2)
        block_end_byte = f.tell()
        lines_to_go = total_lines_wanted
        block_number = -1
        blocks = [] # blocks of size BLOCK_SIZE, in reverse order starting
                    # from the end of the file
        while lines_to_go > 0 and block_end_byte > 0:
            if (block_end_byte - BLOCK_SIZE > 0):
                # read the last block we haven't yet read
                f.seek(block_number*BLOCK_SIZE, 2)
                blocks.append(f.read(BLOCK_SIZE))
            else:
                # file too small, start from begining
                f.seek(0,0)
                # only read what was not read
                blocks.append(f.read(block_end_byte))
            lines_found = blocks[-1].count('\n')
            lines_to_go -= lines_found
            block_end_byte -= BLOCK_SIZE
            block_number -= 1
        all_read_text = ''.join(reversed(blocks))

        return '\n'.join(all_read_text.splitlines()[-total_lines_wanted:])

ghenv.Component.Name = "Butterfly_Watch Residuals"
ghenv.Component.NickName = "watchRes"
ghenv.Component.Message = 'VER 0.0.02\nSEP_28_2016'
ghenv.Component.Category = "Butterfly"
ghenv.Component.SubCategory = "06::Solution"
ghenv.Component.AdditionalHelpFromDocStrings = "3"


try:
    from butterfly.gh.core import Case
except ImportError as e:
    msg = '\nFailed to import butterfly. Did you install butterfly on your machine?' + \
            '\nYou can download the installer file from github: ' + \
            'https://github.com/mostaphaRoudsari/Butterfly/tree/master/plugin/grasshopper/samplefiles' + \
            '\nOpen an issue on github if you think this is a bug:' + \
            ' https://github.com/mostaphaRoudsari/Butterfly/issues'
        
    raise ImportError('{}\n{}'.format(msg, e))

from scriptcontext import sticky

if _solution:
    text = tail(_solution.residualFile).split("\nTime =")[-1].split('\n')
    keys = ('Ux', 'Uy', 'Uz', 'epsilon', 'k')
    if 'res' not in sticky:
        sticky['res'] = dict.fromkeys(keys, 0)
    results = sticky['res']
    
    try:
        t = int(text[0])
    except:
        t = 'unknown'

    for key in keys:
        print key    

    for line in text:
        try:
            p, ir, fr, ni = line.split('smoothSolver:  Solving for ')[1].split(',')
            results[p] = fr.split('= ')[-1]
            # print (p, ir.split('= ')[-1], fr.split('= ')[-1])
        except IndexError:
            pass
    residualValues = (results[key] for key in keys)
    ghenv.Component.Message = "TimeStep = {}".format(t)
