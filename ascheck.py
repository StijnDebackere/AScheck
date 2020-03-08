#! /usr/local/bin/python3
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
from __future__ import print_function
import cv2
import numpy as np
import os
import sys
import glob
import tkinter.filedialog as filedialog

import pdb


def extract_contour(image, contour, fill_value=255):
    '''
    Returns an image where contour is filled with fill_value

    Parameters
    ----------
    image : array
        image
    contour : array with polygon points
        cv2 contour
    fill_value : float, int or tuple
        color value to fill contour with

    Returns
    -------
    contour_img : array like image
        image with only the contour filled
    '''
    if len(np.asarray(fill_value).shape) <= 1:
        temp = np.zeros_like(image)
        contour_img = cv2.fillPoly(np.uint8(temp),
                                   pts=[contour],
                                   color=fill_value)

    return contour_img


def center_on_contour(image, contour):
    '''
    Returns an image that is centered and focused contour

    Parameters
    ----------
    image : array
        image to center on contour
    contour : array with polygon points
        cv2 contour

    Returns
    -------
    centered : array
        image focused and centered on contour
    '''
    # get maximum and minimum value of the contour along both axes
    mx = np.max(contour, axis=0)
    mn = np.min(contour, axis=0)

    # calculate the centre + the extent in along both axes for the rock
    centre = np.round((mx + mn) / 2.).astype(int)
    extent = np.round((mx - mn) / 2.).astype(int)
    centered = image[centre[1] - extent[1]:centre[1] + extent[1]+1,
                     centre[0] - extent[0]:centre[0] + extent[0]+1]

    return centered


def show_contours(image, contours):
    '''
    Show image with contours indicated

    Parameters
    ----------
    image : array
        image array
    contours : array with polygon points for different contours
        cv2 contour

    Returns
    -------
    image_contours : array
        image with the contours overlaid in red
    '''
    if len(image.shape) == 2.:
        image_rgb = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)

    image_contours = cv2.drawContours(image_rgb, contours,
                                      contourIdx=-1,
                                      color=(255, 0, 0), thickness=3)

    return image_contours


def fill_contours(image, contours, color="gray"):
    '''
    Fill contours in image

    Parameters
    ----------
    image : array
        grayscale image
    contours : array with polygon points for different contours
        cv2 contour

    Returns
    -------
    image_contours : array
        image with the contours filled in red
    '''
    colors = ["gray", "RGB"]
    if color not in colors:
        print("color {} not recognized, using gray".format(color))
        color = "gray"

    if color == "RGB":
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
    else:
        image = np.uint8(image)

    image_contours = np.copy(image)
    for idx, contour in enumerate(contours):
        color = 255 * (len(contours) - idx / 2) / len(contours)
        image_contours = cv2.fillPoly(image_contours,
                                      pts=[contour],
                                      color=(0, 0, color))

    return image_contours


def threshold_image(image, method):
    '''
    Returns an image that is thresholded into a binary background and
    foreground

    Parameters
    ----------
    image : array
        image to threshold
    method : string 'Otsu' or 'GaussianThreshold'
        method to use for the thresholding
        (default='Otsu')

    Returns
    -------
    image_thresh : array
        thresholded image
    '''
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
        image_thresh = cv2.adaptiveThreshold(image_bw, 255,
                                             cv2.ADAPTIVE_THRESH_MEAN_C,
                                             cv2.THRESH_BINARY,
                                             901, 0)
    return image_thresh


def open_and_close(image, iterations=2):
    '''
    Returns an image where the object should be filled up (closed) and
    the noise removed (opened)

    Parameters
    ----------
    image : array
        image to threshold
    iterations : int
        Number of times to open and close the image
    Returns
    -------
    closed : array
        opened and closed image
    '''
    # open up the image, removes noise
    opened = cv2.morphologyEx(image, cv2.MORPH_OPEN, None,
                              iterations=iterations)
    # close the image, fill up inner regions
    closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, None,
                              iterations=iterations)
    return closed


def calculate_asymmetry(image):
    '''
    Returns the asymmetry index A:

        A = #asymmetric pixels / #total pixels in the object

    The image of the thresholded object is flipped along its longest
    axis and the difference between the minimal and maximal outline
    gives the amount of asymmetric pixels.

    Parameters
    ----------
    image : array
        thresholded image to flip
    Returns
    -------
    A : float
        asymmetry index of the object
    diff : array
        image with asymmetric pixels
    '''
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
        A = 1.

    return A, np.uint8(diff) * 255


def get_image_asymmetry(image, diagnostics=True):
    '''
    Process image to find the object and compute its asymmetry.

    Parameters
    ----------
    image : array
        image to process

    Returns
    -------
    final : array
        processed image with identified object
    A : float
        asymmetry index
    '''
    # binarize image
    image_thresh = threshold_image(image, 'Otsu')

    # we pad the image to avoid edge effects and to help smoothing out noise
    image_thresh_padded = cv2.copyMakeBorder(image_thresh, 50, 50, 50, 50,
                                             cv2.BORDER_REPLICATE)

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
    closed = (hierarchy[:, 2] < 0)
    # closed = (hierarchy[:,2] < 0) & (hierarchy[:,3] < 0)

    # need to get shapes of contours to find the largest closed one
    shapes = np.array([c.shape[0] for c in contours])
    contour = contours[closed][shapes[closed].argmax()].reshape(-1, 2)

    if diagnostics:
        image_padded_gray = cv2.copyMakeBorder(image, 50, 50, 50, 50,
                                               cv2.BORDER_REPLICATE)
        img_with_contour = fill_contours(image_padded_gray,
                                         [contour],
                                         color="RGB")

    # fill the contour
    contour_img = extract_contour(image_final, contour)

    # center on contour
    final = center_on_contour(contour_img, contour)
    final = final.astype('uint8')

    # get asymmetry
    A, diff = calculate_asymmetry(final)

    if diagnostics:
        return final, A, diff, img_with_contour
    else:
        return final, A


def main():
    # Ask user for input directory
    read_dir = filedialog.askdirectory()
    # exit code if no directory selected
    # don't want to accidentally write to /
    if read_dir == "":
        sys.exit("No directory selected")
    else:
        read_dir = read_dir.rstrip(os.sep)

        bw_dir = read_dir + '/bw/'
        # create output directory
        if not os.path.exists(bw_dir):
            os.makedirs(bw_dir)

        files = glob.glob(read_dir + '/*.*')
        info = np.empty((1, 3), dtype=object)

        save_name = read_dir + '/ascheck_results.txt'

        for idx, f in enumerate(files):
            ext = f.split('.')[-1]

            # read greyscale data
            image = cv2.imread(f, 0)
            if image is None:
                continue

            # get final image and its asymmetry index
            final, A, diff, img_contour = get_image_asymmetry(image,
                                                              diagnostics=True)

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
            cv2.imwrite(bw_dir + fname + '_asym.{}'.format(ext), diff)
            cv2.imwrite(bw_dir + fname + '_contour.{}'.format(ext),
                        img_contour)

            # save info to array
            info = np.vstack([info, [f, A, flag]])

        info = info[1:]
        np.savetxt(save_name, info.astype(str), fmt='%s', comments='#',
                   header='filename asymmetry_index flag')


if __name__ == "__main__":
    main()
