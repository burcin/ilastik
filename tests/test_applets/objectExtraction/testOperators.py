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

import unittest
import numpy as np
import vigra
from lazyflow.graph import Graph
from lazyflow.operators import OpLabelImage
from ilastik.applets.objectExtraction.opObjectExtraction import OpAdaptTimeListRoi, OpRegionFeatures
from ilastik.plugins import pluginManager

NAME = "Standard Object Features"

FEATURES = {
    NAME : {
        "Count" : {},
        "RegionCenter" : {},
        "Coord<Principal<Kurtosis>>" : {},
        "Coord<Minimum>" : {},
        "Coord<Maximum>" : {},
    }
}

def binaryImage():
    img = np.zeros((2, 50, 50, 50, 1), dtype=np.float32)
    img[0,  0:10,  0:10,  0:10, 0] = 1
    img[0, 20:30, 20:30, 20:30, 0] = 1
    img[0, 40:45, 40:45, 40:45, 0] = 1

    img[1, 20:30, 20:30, 20:30, 0] = 1
    img[1, 5:10, 5:10, 0, 0] = 1
    img[1, 12:15, 12:15, 0, 0] = 1
    img = img.view(vigra.VigraArray)
    img.axistags = vigra.defaultAxistags('txyzc')

    return img

def rawImage():
    img = np.zeros((2, 50, 50, 50, 1), dtype=np.float32)
    img[0,  0:10,  0:10,  0:10, 0] = 200
    img[0, 20:30, 20:30, 20:30, 0] = 100

    # this object is further out than the margin and tests
    # regionCenter feature
    img[0, 40:45, 40:45, 40:45, 0] = 75

    img[1, 20:30, 20:30, 20:30, 0] = 50

    # this and next object are in each other's excl features
    img[1, 5:10, 5:10, 0, 0] = 25
    img[1, 12:15, 12:15, 0, 0] = 13
    img = img.view(vigra.VigraArray)
    img.axistags = vigra.defaultAxistags('txyzc')

    return img

class TestOpLabelImage(object):
    def setUp(self):
        g = Graph()
        self.op = OpLabelImage(graph=g)
        self.img = binaryImage()
        self.op.Input.setValue(self.img)

    def test_segment(self):
        labelImg = self.op.Output.value
        labelImg = labelImg.astype(np.int)
        assert np.all(labelImg.shape==self.img.shape)

        vigraImage0 = vigra.analysis.labelVolumeWithBackground(self.img[0,...])
        vigraImage1 = vigra.analysis.labelVolumeWithBackground(self.img[1,...])

        assert np.all(np.asarray(vigraImage0)==labelImg[0,...])
        assert np.all(np.asarray(vigraImage1)==labelImg[1,...])


class TestOpRegionFeatures(object):
    def setUp(self):
        g = Graph()
        self.labelop = OpLabelImage(graph=g)
        self.op = OpRegionFeatures(graph=g)
        self.op.LabelImage.connect(self.labelop.Output)

        # Raw image is arbitrary for our purposes. Just re-use the
        # label image
        self.op.RawImage.connect(self.labelop.Output)
        self.op.Features.setValue(FEATURES)
        self.img = binaryImage()
        self.labelop.Input.setValue(self.img)

    def test_features(self):
        self.op.Output.fixed = False
        # FIXME: roi specification
        opAdapt = OpAdaptTimeListRoi(graph=self.op.graph)
        opAdapt.Input.connect(self.op.Output)

        feats = opAdapt.Output([0, 1]).wait()
        assert len(feats)== self.img.shape[0]
        for t in feats:
            assert feats[t][NAME]['Count'].shape[0] > 0
            assert feats[t][NAME]['RegionCenter'].shape[0] > 0

        assert np.any(feats[0][NAME]['Count'] != feats[1][NAME]['Count'])
        assert np.any(feats[0][NAME]['RegionCenter'] != feats[1][NAME]['RegionCenter'])


class testOpRegionFeaturesAgainstNumpy(object):
    def setUp(self):
        g = Graph()
        self.features = {
            NAME : {
                "Count" : {},
                "RegionCenter" : {},
                "Mean" : {},
                "Coord<Minimum>" : {},
                "Coord<Maximum>" : {},
                "Mean in neighborhood" : {"margin" : (30, 30, 1)},
                "Sum" : {},
                "Sum in neighborhood" : {"margin" : (30, 30, 1)}
            }
        }

        binimage = binaryImage()
        self.rawimage = rawImage()
        self.labelop = OpLabelImage(graph=g)
        self.op = OpRegionFeatures(graph=g)
        self.op.LabelImage.connect(self.labelop.Output)
        self.op.RawImage.setValue(self.rawimage)
        self.op.Features.setValue(self.features)
        self.img = binaryImage()
        self.labelop.Input.setValue(binimage)

    def test(self):
        self.op.Output.fixed = False
        # FIXME: roi specification
        opAdapt = OpAdaptTimeListRoi(graph=self.op.graph)
        opAdapt.Input.connect(self.op.Output)

        feats = opAdapt.Output([0, 1]).wait()
        assert len(feats)==self.img.shape[0]
        for key in self.features[NAME]:
            assert key in feats[0][NAME].keys()

        labelimage = self.labelop.Output[:].wait()
        nt = labelimage.shape[0]
        for t in range(nt):
            npcounts = np.bincount(np.asarray(labelimage[t,...].flat, dtype=int))
            counts = feats[t][NAME]["Count"].astype(np.uint32)
            means = feats[t][NAME]["Mean"]
            sum_excl = feats[t][NAME]["Sum in neighborhood"] #sum, not mean, to avoid 0/0
            sum_incl = feats[t][NAME]["Sum in object and neighborhood"]
            sum = feats[t][NAME]["Sum"]
            mins = feats[t][NAME]["Coord<Minimum>"]
            maxs = feats[t][NAME]["Coord<Maximum>"]
            centers = feats[t][NAME]["RegionCenter"]
            #print mins, maxs
            nobj = npcounts.shape[0]
            for iobj in range(1, nobj):
                assert npcounts[iobj] == counts[iobj]
                objmask = labelimage[t,...]==iobj
                npmean = np.mean(np.asarray(self.rawimage)[t,...][objmask])
                assert npmean == means[iobj]
                #currently, we have a margin of 30, this assert is very dependent on it
                #FIXME: make margin visible from outside and use it here
                zmin = max(mins[iobj][2]-1, 0)
                zmax = min(maxs[iobj][2]+1, self.rawimage.shape[3])

                exclmask = labelimage[t,:, :, zmin:zmax, :]!=iobj
                npsum_excl = np.sum(np.asarray(self.rawimage)[t,:, :, zmin:zmax,:][exclmask])
                assert npsum_excl == sum_excl[iobj]

                assert sum_incl[iobj] == sum[iobj]+sum_excl[iobj]
                #check that regionCenter wasn't shifted
                for icoord, coord in enumerate(centers[iobj]):
                    center_good = mins[iobj][icoord] + (maxs[iobj][icoord]-mins[iobj][icoord])/2.
                    assert abs(coord-center_good)<0.01


if __name__ == '__main__':
    import sys
    import nose

    # Don't steal stdout. Show it on the console as usual.
    sys.argv.append("--nocapture")

    # Don't set the logging level to DEBUG. Leave it alone.
    sys.argv.append("--nologcapture")

    nose.run(defaultTest=__file__)
