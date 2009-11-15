"Contains the `Version` class for easily comparing versions of Maya with the current running version."

import pymel.util as util
import re
from maya.OpenMaya import MGlobal  as _MGlobal
import maya.cmds as cmds
__all__ = ['Version']

# TODO: finish this, replace current Version class...
#class newVersion( object ):
#    """
#    Class for retrieving apiVersions, which are the best method for comparing versions,
#    as well as other version info.
#    
#    >>> if Version.current > Version.v85:
#    >>>     print "The current version is later than Maya 8.5"
#    """
#    __metaclass__ = util.Singleton
#
#    def __init__(self):
#        self.refresh()
#        
#    def refresh(self):
#        """Refreshes the stored version information."""
#        # Basically, should only need to be called if _fromStringProcessing is True, 
#        # and maya has since been initialized.
#        if mayaIsRunning():
#            # Since about(apiVersion=True) will work on all version after 8.5,
#            # and 8.5 is the first version with python support, if the command fails,
#            # we know it is 8.5
#            try:
#                self.current = about(apiVersion=True)
#            except TypeError:
#                # Since about(apiVersion=True) will work on all version after 8.5,
#                # and 8.5 is the first version with python support, if the command fails,
#                # we know it is 8.5
#                self.current = {
#                 '8.5 Service Pack 1': 200701,
#                 '8.5': 200700,
#                }[ cmds.about(version=1)]
#
#            self.versionNum = self.current // 100;
#        else:
#            pass






def _getApiVersion():
    """backward compatibility hack for api version in maya 8.5"""
    try:
        return _MGlobal.apiVersion()
    except AttributeError:
        versionStr = _MGlobal.mayaVersion()
        if versionStr.startswith('8.5 Service Pack 1'):
            return 200701
        else:
            return 200700


def parseVersionStr(versionStr, extension=False):
    """
    >>> from pymel.all import *
    >>> mayahook.parseVersionStr('2008 Service Pack1 x64')
    '2008'
    >>> mayahook.parseVersionStr('2008 Service Pack1 x64', extension=True)
    '2008-x64'
    >>> mayahook.parseVersionStr('2008x64', extension=True)
    '2008-x64'
    >>> mayahook.parseVersionStr('8.5', extension=True)
    '8.5'
    >>> mayahook.parseVersionStr('2008 Extension 2')
    '2008'
    >>> mayahook.parseVersionStr('/Applications/Autodesk/maya2009/Maya.app/Contents', extension=True)
    '2009'
    >>> mayahook.parseVersionStr('C:\Program Files (x86)\Autodesk\Maya2008', extension=True)
    '2008'

    """
    # problem with service packs addition, must be able to match things such as :
    # '2008 Service Pack 1 x64', '2008x64', '2008', '8.5'

    # NOTE: we're using the same regular expression (parseVersionStr) to parse both the crazy human readable
    # maya versions as returned by about, and the maya location directory.  to handle both of these i'm afraid 
    # the regular expression might be getting unwieldy

    ma = re.search( "((?:maya)?(?P<base>[\d.]{3,})(?:(?:[ ].*[ ])|(?:-))?(?P<ext>x[\d.]+)?)", versionStr)
    version = ma.group('base')

    if extension and (ma.group('ext') is not None) :
        version += "-"+ma.group('ext')
    return version


class Version(object):
    """
    Class for storing apiVersions, which are the best method for comparing versions.
    
    >>> if Version.current >= Version.v85sp1:
    ...     print "The current version is later than Maya 8.5 Service Pack 1"
    The current version is later than Maya 8.5 Service Pack 1
    """
    #TODO: make these read-only
    __metaclass__ = util.metaReadOnlyAttr
    __readonly__ = ['v85', 'v85sp1', 'v2008', 'v2008sp1', 'v2008ext2', 'v2009', 
                    'current', 'fullName', 'installName', 'shortName']
    
    
    current = _getApiVersion()

    # should this be an enum class?  
    #enum = util.Enum( { 'v85' : 200700, 'v85sp1' : 200701, 'v2008' : 200800, 'v2008sp1' : 200806, 'v2008ext2' : 200806 } )
    v85      = 200700
    v85sp1   = 200701
    v2008    = 200800
    v2008sp1  = 200806
    v2008ext2 = 200806
    v2009     = 200900
    v2009sp1  = 200904
    v2009sp1a = 200906
    v2010     = 201000
#    CURRENT = _getApiVersion()
#    
#    v85      = 200700
#    v85SP1   = 200701
#    v2008    = 200800
#    v2008SP1  = 200806
#    v2008EXT2 = 200806
#    v2009     = 200900

    
    #: Unlimited or Complete
    
    @staticmethod
    def fullName():
        return _MGlobal.mayaVersion()
    @classmethod
    def installName(cls):
        return parseVersionStr(cls.fullName(), extension=True)
    @classmethod
    def shortName(cls):
        return parseVersionStr(cls.fullName(), extension=False)
    
#    fullName = _MGlobal.mayaVersion()
#    installName = parseVersionStr(fullName, extension=True)
#    shortName = parseVersionStr(fullName, extension=False)
    
    @classmethod
    def flavor(cls):
        try:
            return cmds.about(product=1).split()[1]
        except AttributeError:
            raise RuntimeError, "This method cannot be used until maya is fully initialized"

    @classmethod
    def isUnlimited(cls): return cls.flavor() == 'Unlimited'
    
    @classmethod
    def isComplete(cls): return cls.flavor() == 'Complete'

    @classmethod
    def isRenderNode(cls): return cls.flavor() == 'Render'
    
    @classmethod
    def isEval(cls): return cmds.about(evalVersion=1)
    