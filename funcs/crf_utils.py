## written by Dr Daniel Buscombe
## Northern Arizona University
## daniel.buscombe@nau.edu

import pydensecrf.densecrf as dcrf
from pydensecrf.utils import create_pairwise_bilateral, unary_from_labels, unary_from_softmax
import numpy as np
from collections import namedtuple
from imageio import imwrite
import os

# =========================================================
def write_label_image(imfile, out):

   name = os.path.basename(imfile)
   imwrite(name+'_mres_label.png', out)

# =========================================================
def get_sparse_label(anno, nx, ny, labels, brush):

   Lc = np.zeros((nx, ny))
   for k in range(len(labels)):
      X = np.floor(anno[labels[k]][:,1]).astype('int')
      Y = np.floor(anno[labels[k]][:,0]).astype('int')   
      for (x,y) in zip(X,Y):
         if np.min([nx,x+brush]) - np.max([0,x-brush]) == np.min([ny,y+brush]) - np.max([0,y-brush]):
            Lc[np.max([0,x-brush]):np.min([nx,x+brush]), np.max([0,y-brush]):np.min([ny,y+brush])] = np.ones((brush*2, brush*2))*k+1

   return np.flipud(Lc)   

# =========================================================
def get_rgb(res, labels, colors):

   hexcol = [col.lstrip('#').split('\n')[0] for col in colors]
   Label = namedtuple('Label', ['name', 'color'])
   rgb = [tuple(int(h[i:i+2], 16) for i in (0, 2 ,4)) for h in hexcol]

   label_defs = []
   for k in range(len(labels)):
      label_defs.append(Label(labels[k],(rgb[k][0], rgb[k][1], rgb[k][2])))
	
   out = np.zeros((np.shape(res)[0], np.shape(res)[1], 3), dtype='uint8')
   for k in np.unique(res):
      out[:,:,0][res==k] = label_defs[k].color[0]
      out[:,:,1][res==k] = label_defs[k].color[1]
      out[:,:,2][res==k] = label_defs[k].color[2]
   return out
	
# =========================================================
def get_labels_and_colors(label_editor):
    N = len(label_editor.children[0].children)
    labels = [callback(label_editor.children[0].children[k].children[0]) for k  in range(N)]
    colors = [callback(label_editor.children[0].children[k].children[1]) for k  in range(N)]
    return labels, colors
	
# =========================================================	
def callback(wdgt):
    return wdgt.value

# =========================================================	
def access_annotation_coordinates(freehand_stream):
    X = [freehand_stream.element.data[1:][k]['x'] for k in range(len(freehand_stream.element.data[1:]))]
    Y = [freehand_stream.element.data[1:][k]['y'] for k in range(len(freehand_stream.element.data[1:]))]
    return np.hstack(X), np.hstack(Y)
	
# =========================================================
def getCRF(image, Lc, theta, n_iter, label_lines, compat_spat=12, compat_col=40):

#        n_iters: number of iterations of MAP inference.
#        sxy_gaussian: standard deviations for the location component
#            of the colour-independent term.
#        compat_gaussian: label compatibilities for the colour-independent
#            term (can be a number, a 1D array, or a 2D array).
#        kernel_gaussian: kernel precision matrix for the colour-independent
#            term (can take values CONST_KERNEL, DIAG_KERNEL, or FULL_KERNEL).
#        normalisation_gaussian: normalisation for the colour-independent term
#            (possible values are NO_NORMALIZATION, NORMALIZE_BEFORE, NORMALIZE_AFTER, NORMALIZE_SYMMETRIC).
#        sxy_bilateral: standard deviations for the location component of the colour-dependent term.
#        compat_bilateral: label compatibilities for the colour-dependent
#            term (can be a number, a 1D array, or a 2D array).
#        srgb_bilateral: standard deviations for the colour component
#            of the colour-dependent term.
#        kernel_bilateral: kernel precision matrix for the colour-dependent term
#            (can take values CONST_KERNEL, DIAG_KERNEL, or FULL_KERNEL).
#        normalisation_bilateral: normalisation for the colour-dependent term
#            (possible values are NO_NORMALIZATION, NORMALIZE_BEFORE, NORMALIZE_AFTER, NORMALIZE_SYMMETRIC).

      scale = 1
	  
      image = np.array(image)
      H = image.shape[0]
      W = image.shape[1]

      d = dcrf.DenseCRF2D(H, W, len(label_lines)+1)
      U = unary_from_labels(Lc.astype('int'), len(label_lines)+1, gt_prob= 0.5)

      d.setUnaryEnergy(U)

      del U

      # This potential penalizes small pieces of segmentation that are
      # spatially isolated -- enforces more spatially consistent segmentations
      # This adds the color-independent term, features are the locations only.
      # sxy = The scaling factors per dimension.
      d.addPairwiseGaussian(sxy=(theta,theta), compat=compat_spat, kernel=dcrf.DIAG_KERNEL, #compat=6
                      normalization=dcrf.NORMALIZE_SYMMETRIC)

      # sdims = The scaling factors per dimension.
      # schan = The scaling factors per channel in the image.
      # This creates the color-dependent features and then add them to the CRF
      feats = create_pairwise_bilateral(sdims=(theta, theta), schan=(scale, scale, scale), 
                                  img=image, chdim=2)

      del image

      d.addPairwiseEnergy(feats, compat=compat_col, #20
                    kernel=dcrf.DIAG_KERNEL,
                    normalization=dcrf.NORMALIZE_SYMMETRIC)
      del feats

      Q = d.inference(n_iter)

      return np.argmax(Q, axis=0).reshape((H, W)) 
