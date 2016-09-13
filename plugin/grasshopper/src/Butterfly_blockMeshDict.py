# Butterfly: A Plugin for CFD Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# This file is part of Butterfly.
#
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Set parameters for snappyHexMeshDict.
Read more about snappyHexMeshDict here:
    https://openfoamwiki.net/images/f/f0/Final-AndrewJacksonSlidesOFW7.pdf


    Args:
        _bbox: A geometry that represents bounding box of the the domain. It should be slightly bigger than the domain itself.
        _nDivXYZ_: Number of Block divisions in X, Y and Z. You can use a point component to input values.
        _gradXYZ_: Grading value for X, Y and Z. You can use a point component to input values.
    Returns:
        blockMeshDict: Butterfly blockMeshDict.
"""

ghenv.Component.Name = "Butterfly_blockMeshDict"
ghenv.Component.NickName = "blockMeshDict"
ghenv.Component.Message = 'VER 0.0.01\nSEP_13_2016'
ghenv.Component.Category = "Butterfly"
ghenv.Component.SubCategory = "06::Etc"
ghenv.Component.AdditionalHelpFromDocStrings = "1"

try:
    # import butterfly
    from butterfly.gh.bfsurface import BFSurface
    from butterfly.gh.block import Block
    from butterfly.gh.unitconversion import convertDocumentUnitsToMeters
    from butterfly.blockMeshDict import BlockMeshDict
    from butterfly.boundarycondition import BoundingBoxBoundaryCondition
except ImportError as e:
    msg = '\nFailed to import butterfly. Did you install butterfly on your machine?' + \
            '\nYou can download the installer file from github: ' + \
            'https://github.com/mostaphaRoudsari/Butterfly/tree/master/plugin/grasshopper/samplefiles' + \
            '\nOpen an issue on github if you think this is a bug:' + \
            ' https://github.com/mostaphaRoudsari/Butterfly/issues'
        
    raise ImportError('{}\n{}'.format(msg, e))

# create blockMeshDict based on BBox
if _bbox:
    block = Block(_bbox, _nDivXYZ_, _gradXYZ_)
    bc = BoundingBoxBoundaryCondition()
    BBBFSurface = BFSurface('boundingbox', [_bbox], bc)
    blockMeshDict = BlockMeshDict(convertDocumentUnitsToMeters(), [BBBFSurface], [block])