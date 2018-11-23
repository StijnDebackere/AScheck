#! /usr/local/bin/python
# ------------------------------------------------------------------------------
# Ascheck computes the fraction of asymmetric pixels in an image of an object
# Copyright (C) 2017  Laurie Hutchence & Stijn Debackere
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
# ------------------------------------------------------------------------------
import cv2
import numpy as np
import os
import glob
import argparse
from tkinter import filedialog

import matplotlib.pyplot as plt

def fill_contour(image, contour, fill_value=255):
    temp = np.zeros_like(image)
    contour_img = cv2.fillPoly(np.uint8(temp), pts=[contour], color=fill_value)
    return contour_img

# ----------------------------------------------------------------------
# End of fill_contour()
# ----------------------------------------------------------------------

def center_on_contour(contour_img, contour):
    # get maximum and minimum value of the contour along both axes
    mx = np.max(contour, axis=0)
    mn = np.min(contour, axis=0)

    # calculate the centre + the extent in along both axes for the rock
    centre = np.round((mx + mn) / 2.).astype(int)
    extent = np.round((mx - mn) / 2.).astype(int)
    centered = contour_img[centre[1] - extent[1]:centre[1] + extent[1]+1,
                           centre[0] - extent[0]:centre[0] + extent[0]+1]

    return centered

# ----------------------------------------------------------------------
# End of center_on_contour()
# ----------------------------------------------------------------------

def show_contours(image, contours):
    if len(image.shape) == 2.:
        image_rgb = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)

    plt.imshow(cv2.drawContours(image_rgb, contours, contourIdx=-1,
                                color=(255,0,0), thickness=3))
    plt.show()

# ----------------------------------------------------------------------
# End of show_contours()
# ----------------------------------------------------------------------

def threshold_image(image, method):
    methods = ['Otsu', 'GaussianThreshold']
    if method not in methods:
        print("Using Otsu's method")
        method = 'Otsu'

    if len(image.shape) > 2.:
        image_bw = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    else:
        image_bw = np.copy(image)

    if method == 'Otsu':
        ret, image_thresh = cv2.threshold(image_bw, 0, 255,
                                          cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    else:
        image_thresh = cv2.adaptiveThreshold(image_bw, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                             cv2.THRESH_BINARY,
                                             901,0)
    return image_thresh

# ----------------------------------------------------------------------
# End of threshold_image()
# ----------------------------------------------------------------------

def open_and_close(image, iterations=2):
    # open up the image, removes noise
    opened = cv2.morphologyEx(image, cv2.MORPH_OPEN, None,
                              iterations=iterations)
    # close the image, fill up inner regions
    closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, None,
                              iterations=iterations)
    return closed

# ----------------------------------------------------------------------
# End of erode_and_dilate()
# ----------------------------------------------------------------------

def calculate_asymmetry(image):
    # flip image along longest axis
    shape = np.array(image.shape)
    flipped = np.flip(image, axis=np.argmin(shape))

    # Compute difference
    diff_1 = image - flipped
    diff_2 = np.flip(diff_1, axis=np.argmin(shape))

    diff = np.logical_or(diff_1, diff_2)

    try:
        A = np.float(diff.sum()) / image.astype(bool).sum()
    except ZeroDivisionError:
        print(f.split('/')[-1] + ' went wrong...')
        A = 1.

    return A

# ----------------------------------------------------------------------
# End of calculate_asymmetry()
# ----------------------------------------------------------------------

def get_image_asymmetry(image):
    # binarize image
    image_thresh = threshold_image(image, 'Otsu')

    # we pad the image to avoid edge effects and to help smoothing out noise
    image_thresh_padded = cv2.copyMakeBorder(image_thresh, 50, 50, 50, 50,
                                             cv2.BORDER_CONSTANT, value=255)

    # now we open and close the image
    image_final = open_and_close(image_thresh_padded)

    # find contours in thresholded images
    im2, contours, hierarchy = cv2.findContours(image_final,
                                                cv2.RETR_CCOMP,
                                                cv2.CHAIN_APPROX_SIMPLE)

    # need to turn list into array
    contours = np.array(contours)

    # reshape hierarchy to be more useful
    hierarchy = hierarchy.reshape(len(contours), 4)

    # criterion for closed contour
    closed = (hierarchy[:,2] < 0)
    # closed = (hierarchy[:,2] < 0) & (hierarchy[:,3] < 0)

    # need to get shapes of contours to find the largest closed one
    shapes = np.array([c.shape[0] for c in contours])
    contour = contours[closed][shapes[closed].argmax()].reshape(-1,2)

    # fill the contour
    contour_img = fill_contour(image_thresh, contour)

    # center on contour
    final = center_on_contour(contour_img, contour)
    final = final.astype('uint8')

    # get asymmetry
    A = calculate_asymmetry(final)

    return final, A

# ----------------------------------------------------------------------
# End of get_image_asymmetry()
# ----------------------------------------------------------------------
# Ask user for input directory
read_dir = filedialog.askdirectory().rstrip(os.sep)

bw_dir = read_dir + '/bw_new/'
# create output directory
if not os.path.exists(bw_dir):
    os.makedirs(bw_dir)

files = glob.glob(read_dir + '/*.*')
info = np.empty((len(files), 3), dtype=object)

save_name = read_dir + '/ascheck_results.txt'

for idx, f in enumerate(files):
    ext = f.split('.')[-1]

    # read greyscale data
    image = cv2.imread(f, 0)
    if image is None:
        continue

    # get final image and its asymmetry index
    final, A = get_image_asymmetry(image)

    # flag image as suspicious if size is abnormally small
    # or if asymmetry is larger than 1
    if ((final.shape[0] < image.shape[0] / 6.
         or final.shape[1] < image.shape[1] / 6.)
        or A >= 1.):
        flag = 'suspicious'
    else:
        flag = 'OK'

    # save image
    fname = os.path.split(f)[-1].split('.')[0]
    cv2.imwrite(bw_dir + fname + '_bw.{}'.format(ext), final)

    # save info to array
    info[idx] = [f, A, flag]

np.savetxt(save_name, info.astype(str), fmt='%s', comments='#',
           header='filename asymmetry_index flag')
