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

import numpy
import time
import matplotlib.pyplot as plt
import sys
import h5py
from cylemon.segmentation import MSTSegmentor


import vigra
import numpy


def h5ToStack(inputf):
    h5f = h5py.File(inputf,"r")
    for i in xrange(10):
        vol = h5f["raw"][:,:,][i]
        f = 1.0/256
        volume = numpy.array([[[x*f,0,0] for x in y] for y in vol])
        print volume
        plt.imshow(volume)
        print volume
        file_ = open("C:/Users/Ben/Desktop/carvingData/imageStack/pic"+str(i)+".png","w+")
        print "C:/Users/Ben/Desktop/carvingData/imageStack/pic"+str(i)+".png"
        plt.savefig(file_)
        file_.close()

def preprocess(inputf,outputf,sigma = 1.6):
    
    print "preprocessing file %s to outputfile %s" % (inputf, outputf)
    
    h5f = h5py.File(inputf,"r")
    
    volume = h5f["raw"][:35,:35,:35]
    
    print "input volume shape: ", volume.shape
    print "input volume size: ", volume.nbytes / 1024**2, "MB"
    fvol = volume.astype(numpy.float32)
    #volume_feat = vigra.filters.gaussianGradientMagnitude(fvol,sigma)
    
    volume_feat = vigra.filters.hessianOfGaussianEigenvalues(fvol,sigma)[:,:,:,0]
    
    volume_ma = numpy.max(volume_feat)
    volume_mi = numpy.min(volume_feat)
    volume_feat = (volume_feat - volume_mi) * 255.0 / (volume_ma-volume_mi)
    print "Watershed..."
    labelVolume = vigra.analysis.watersheds(volume_feat)[0].astype(numpy.int32)
    print labelVolume
    print labelVolume.shape, labelVolume.dtype
    mst = MSTSegmentor(labelVolume, volume_feat.astype(numpy.float32), edgeWeightFunctor = "minimum")
    mst.raw = volume
    mst.saveH5("C:/Users/Ben/Desktop/carvingData/unprecarv_part35.h5","graph")
    #mst2 = MSTSegmentor.loadH5("C:/Users/Ben/Desktop/carvingData/test1.ilp","preprocessing/graph")
    
#h5ToStack("C:/Users/Ben/Desktop/carvingData/unprecarv_part.h5")
#preprocess("C:/Users/Ben/Desktop/carvingData/unprecarv.h5","C:/Users/Ben/Desktop/carvingData/temp.h5",1)
