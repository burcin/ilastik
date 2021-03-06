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

class ThresholdTwoLevelsSerializer(AppletSerializer):
    def __init__(self, operator, projectFileGroupName):
        slots = [SerialSlot(operator.CurOperator, selfdepends=True),
                 SerialSlot(operator.MinSize, selfdepends=True),
                 SerialSlot(operator.MaxSize, selfdepends=True),
                 SerialSlot(operator.HighThreshold, selfdepends=True),
                 SerialSlot(operator.LowThreshold, selfdepends=True),
                 SerialSlot(operator.SingleThreshold, selfdepends=True),
                 SerialDictSlot(operator.SmootherSigma, selfdepends=True),
                 SerialSlot(operator.Channel, selfdepends=True),
                 SerialHdf5BlockSlot(operator.OutputHdf5,
                                     operator.InputHdf5,
                                     operator.CleanBlocks,
                                     name="CachedThresholdOutput")
                ]

        super(self.__class__, self).__init__(projectFileGroupName, slots=slots)
