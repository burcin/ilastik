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

from ilastik.applets.base.appletSerializer import AppletSerializer, SerialSlot, SerialDictSlot, SerialHdf5BlockSlot

class SplitBodyPostprocessingSerializer(AppletSerializer):
    def __init__(self, operator, projectFileGroupName):
        slots = []
# NOTE: Ideally, we would store the final segmentation output so it can be deserialized into the cache,
#       but the split-body carving workflow relies on the GUI to load the annotation info, which means that the 
#       cache can't be loaded during deserialization.
#       The right way to fix this is to either:
#       (1) re-implement the annotation loading code as part of the operator itself 
#             so it is loaded during deserialization (not deferred to the gui)
#       OR
#       (2) (easier) Cache the annotation points/body ids so that the operators are fully configured by deserialization.
#
#        ... anyway, once that is finished, this line will cause the cache to be saved and loaded.       
#
#        slots = [SerialHdf5BlockSlot(operator.FinalSegmentationHdf5CacheOutput,
#                                     operator.FinalSegmentationHdf5CacheInput,
#                                     operator.FinalSegmentationCleanBlocks,
#                                     name="CachedFinalSegmentation")
#                ]

        super(self.__class__, self).__init__(projectFileGroupName, slots=slots)
