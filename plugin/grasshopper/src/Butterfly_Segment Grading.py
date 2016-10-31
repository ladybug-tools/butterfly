# Butterfly: A Plugin for CFD Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# This file is part of Butterfly.
#
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Segment Grading.
Use this component to create a grading for a segment of the block based on ratio
or length.

-

    Args:
        _percentageLength: Percentage of length of the block.
        _percentageCells: Percentage of cells to be included in this segment.
        _expansionRatio_: Expansion ration in this segment (default: 1).
        
    Returns:
        segmentGrading: A segment grading. Use MultiGrading component to create
            a grading.
"""

ghenv.Component.Name = "Butterfly_Segment Grading"
ghenv.Component.NickName = "segGrading"
ghenv.Component.Message = 'VER 0.0.03\nOCT_30_2016'
ghenv.Component.Category = "Butterfly"
ghenv.Component.SubCategory = "03::Mesh"
ghenv.Component.AdditionalHelpFromDocStrings = "3"

try:
    from butterfly.grading import Grading
except ImportError as e:
    msg = '\nFailed to import butterfly. Did you install butterfly on your machine?' + \
            '\nYou can download the installer file from github: ' + \
            'https://github.com/mostaphaRoudsari/Butterfly/tree/master/plugin/grasshopper/samplefiles' + \
            '\nOpen an issue on github if you think this is a bug:' + \
            ' https://github.com/mostaphaRoudsari/Butterfly/issues'
        
    raise ImportError('{}\n{}'.format(msg, e))

if _percentageLength and _percentageCells:
    segmentGrading = Grading(_percentageLength, _percentageCells, _expansionRatio_)