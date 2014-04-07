# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# Copyright 2011-2014, the ilastik developers

# on windows, the number of "user objects" (widgets) an application can
# use is limited:
#
# http://social.msdn.microsoft.com/Forums/windows/en-US/73aaa1f3-30a7-4593-b299-7ec1fd582b27/the-current-process-has-used-all-of-its-system-allowance-of-handles-for-window-manager-objects?forum=winforms
#
# To avoid running into this limit, each adapter uses an LRU cache and
# keeps open at most LRU_CACHE_SIZE viewers
LRU_CACHE_SIZE=32

from ilastik.utility.lru_cache import lru_cache

class SingleToMultiGuiAdapter( object ):
    """
    Utility class used by the StandardApplet to wrap several single-image 
    GUIs into one multi-image GUI, which is what the shell/Applet API requires.
    """
    def __init__(self, parentApplet, singleImageGuiFactory, topLevelOperator):
        self.singleImageGuiFactory = singleImageGuiFactory
        self._imageLaneIndex = None
        self._tempDrawers = {}
        self.topLevelOperator = topLevelOperator
        self._enabled = False

        # create LRU cache with maximum size LRU_CACHE_SIZE and a callback
        # function that calls stopAndCleanUp() on the cached object.
        self._cachedGUIs = lru_cache(LRU_CACHE_SIZE,
                callback_fn = lambda k, v: v.stopAndCleanUp())(
                        self.singleImageGuiFactory)

    def currentGui(self):
        """
        Return the single-image GUI for the currently selected image lane.

        GUIs are kept in an LRU cache and created / cleaned as necessary.
        """
        if self._imageLaneIndex is None:
            return None

        return self._cachedGUIs(self._imageLaneIndex)

    def appletDrawer(self):
        """
        Return the applet drawer of the current single-image gui.
        """
        if self.currentGui() is not None:
            self._tempDrawers[ self._imageLaneIndex ] = self.currentGui().appletDrawer()
            return self.currentGui().appletDrawer()
        
        if self._imageLaneIndex not in self._tempDrawers:
            from PyQt4.QtGui import QWidget
            self._tempDrawers[ self._imageLaneIndex ] = QWidget()
        return self._tempDrawers[ self._imageLaneIndex ]

    def centralWidget( self ):
        """
        Return the central widget of the currently selected single-image gui.
        """
        if self.currentGui() is None:
            return None
        return self.currentGui().centralWidget()

    def menus(self):
        """
        Return the menus of the currently selected single-image gui.
        """
        if self.currentGui() is None:
            return None
        return self.currentGui().menus()
    
    def viewerControlWidget(self):
        """
        Return the viewer control widget for the currently selectd single-image gui.
        """
        if self.currentGui() is None:
            return None
        return self.currentGui().viewerControlWidget()
    
    def setImageIndex(self, imageIndex):
        """
        Called by the shell when the user has changed the currently selected image lane.
        """
        self._imageLaneIndex = imageIndex

    def stopAndCleanUp(self):
        """
        Called by the workflow when the project is closed and the GUIs are about to be discarded.
        """
        self._cachedGUIs.cache_clear()

    def imageLaneAdded(self, laneIndex):
        """
        Called by the workflow when a new image lane has been created.
        """
        pass

    def imageLaneRemoved(self, laneIndex, finalLength):
        """
        Called by the workflow when an image lane has been destroyed.
        """
        pass
    
    def setEnabled(self, enabled):
        self._enabled = enabled
        for blank_drawer in self._tempDrawers.values():
            # Late import here to avoid importing sip in headless mode.
            import sip
            if not sip.isdeleted(blank_drawer):
                blank_drawer.setEnabled(enabled)
        
