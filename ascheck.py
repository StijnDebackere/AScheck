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

parser = argparse.ArgumentParser(description='Read all files in read_dir with extension ext and compute the index of asymmetry.')

parser.add_argument('read_dir', help='directory to read', type=str)
parser.add_argument('ext', help='file extension', type=str)

args = parser.parse_args()
# read_dir without final separator
read_dir = args.read_dir.rstrip(os.sep)
# extension without dot
ext = args.ext.strip('.')

if not os.path.exists(read_dir + '/bw/'):
    os.makedirs(read_dir + '/bw/')

files = glob.glob(read_dir + '/*.' + ext.strip('.'))
info = np.empty((len(files), 2), dtype=object)

for idx, f in enumerate(files):
    # read greyscale data
    data = cv2.imread(f, 0)

    # use Otsu method to produce binary image to look for contours
    ret, data = cv2.threshold(data, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)

    # find contours in thresholded images
    im2, contours, hierarchy = cv2.findContours(data,
                                                cv2.RETR_CCOMP,
                                                cv2.CHAIN_APPROX_SIMPLE)

    hierarchy = hierarchy.reshape(len(contours), 4)
    # criterion for closed contour
    closed = hierarchy[:,2] < 0
    shapes = np.array([c.shape[0] for c in contours])
    contour = np.array(contours)[closed][shapes[closed].argmax()].reshape(-1,2)

    # fill the contour
    temp = np.zeros_like(data)
    data = cv2.fillPoly(np.uint8(temp), pts=[contour], color=255)

    # get maximum and minimum value of the contour along both axes
    mx = np.max(contour, axis=0)
    mn = np.min(contour, axis=0)

    # calculate the centre + the extent in along both axes for the rock
    centre = np.round((mx + mn) / 2.).astype(int)
    extent = np.round((mx - mn) / 2.).astype(int)

    # slice to square image
    final = data[centre[1] - extent[1]:centre[1] + extent[1]+1,
                 centre[0] - extent[0]:centre[0] + extent[0]+1]
    final = final.astype('uint8')

    # flip image along longest axis
    flipped = np.flip(final, axis=np.argmax(extent))
    diff_1 = final - flipped
    diff_2 = np.flip(diff_1, axis=np.argmax(extent))

    diff = np.logical_or(diff_1, diff_2)

    try:
        A = np.float(diff.sum()) / final.astype(bool).sum()
    except ZeroDivisionError:
        print f.split('/')[-1] + ' went wrong...'
        A = 1.

    # save image
    fname = os.path.split(f)[-1].split('.')[0]
    cv2.imwrite(read_dir + '/bw/' + fname + '_bw.%s'%ext, final)

    print fname
    print A
    print '========='
    # save info to array
    info[idx] = [f, A]

save_name = 'ascheck_results_' + read_dir.split('/')[-1] + '.txt'
print 'Saving AScheck results to %s'%save_name
np.savetxt(save_name, info.astype(str), fmt='%s')
