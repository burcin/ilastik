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

from ilastik.workflow import Workflow

from ilastik.applets.dataSelection import DataSelectionApplet
from ilastik.applets.vigraWatershedViewer import VigraWatershedViewerApplet

from lazyflow.graph import Graph

class VigraWatershedWorkflow(Workflow):

    workflowName = "Watershed Preview"

    @property
    def applets(self):
        return self._applets

    @property
    def imageNameListSlot(self):
        return self.dataSelectionApplet.topLevelOperator.ImageName

    def __init__(self, shell, headless, workflow_cmdline_args, project_creation_workflow, *args, **kwargs):
        # Create a graph to be shared by all operators
        graph = Graph()

        super(VigraWatershedWorkflow, self).__init__( shell, headless, workflow_cmdline_args, project_creation_workflow, graph=graph, *args, **kwargs)
        self._applets = []

        # Create applets 
        self.dataSelectionApplet = DataSelectionApplet(self, "Input Data", "Input Data", supportIlastik05Import=True, batchDataGui=False)
        self.watershedApplet = VigraWatershedViewerApplet(self, "Watershed", "Watershed")

        # Dataset inputs
        opDataSelection = self.dataSelectionApplet.topLevelOperator
        opDataSelection.DatasetRoles.setValue( ['Raw Data'] )

        # Expose to shell
        self._applets.append(self.dataSelectionApplet)
        self._applets.append(self.watershedApplet)

    def connectLane(self, laneIndex):
        """
        Override from base class.
        """
        opData = self.dataSelectionApplet.topLevelOperator.getLane(laneIndex)
        opWatershed = self.watershedApplet.topLevelOperator.getLane(laneIndex)

        # Connect top-level operators
        opWatershed.InputImage.connect( opData.Image )
        opWatershed.RawImage.connect( opData.Image )

