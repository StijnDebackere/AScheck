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
import matplotlib.pyplot as plt
import scipy.stats as stats
import os


class Image(object):
    """
    Base class for image manipulations
    """
    def __init__(self,
                 filename,
                 save=True,
                 save_dir=None):
        self.filename = filename
        self._load_image()

        # extract filename to prepend
        path_list = self.filename.rstrip(os.sep).split("/")
        self.img_name = os.path.splitext(path_list[-1])[0]
        self.img_ext = os.path.splitext(path_list[-1])[1]
        self.save_dir = save_dir

        if save and save_dir is None:
            self.save_dir = "/".join(path_list[:-1]) + "/"

    def _load_image(self):
        self.image = cv2.imread(
            self.filename,
            cv2.IMREAD_UNCHANGED
        )
        self.image_bw = cv2.imread(
            self.filename,
            cv2.IMREAD_GRAYSCALE
        )
        if self.image is None:
            raise TypeError("{} is not an image".format(self.filename))

    def threshold_image(
            self,
            image,
            thresh=0, maxval=255,
            blur=True,
            open_close=True,
            iterations=2,
            method=cv2.THRESH_BINARY+cv2.THRESH_OTSU
    ):
        '''
        Returns an image that is thresholded into a binary background and
        foreground

        Parameters
        ----------
        image : array
            grayscale image to threshold
        thresh : int
            threshold value (default: 0)
        maxval : int
            maximum value (default: 255)
        blur : bool
            blur image before thresholding, reduce noise
        open_close : bool
            unify image after thresholding
        iterations : int
            number of iterations for open and close
        method : valid cv2.THRESHOLD type
            method for thresholding (default: Otsu's method)

        Returns
        -------
        image_thresh : array
            thresholded image
        '''
        if blur:
            img_blur = cv2.blur(image, (5, 5))
            ret, image_thresh = cv2.threshold(
                img_blur, thresh, maxval, method
            )
        else:
            ret, image_thresh = cv2.threshold(
                image, thresh, maxval, method
            )

        if open_close:
            image_thresh = self.open_and_close_image(
                image_thresh, iterations=iterations
            )

        return image_thresh

    def pad_image(
            self,
            image,
            size,
            value=None,
            method=cv2.BORDER_REPLICATE
    ):
        '''
        Pad img by size along each edge using method

        Parameters
        ----------
        image : array
            image to pad
        size : int
            number of pixels to add
        method : cv2.BORDER_REPLICATE or cv2.BORDER_CONSTANT

        Returns
        -------
        img_pad : array with padded image
        '''
        methods = [cv2.BORDER_REPLICATE, cv2.BORDER_CONSTANT]
        if method not in methods:
            raise ValueError("method should be in {}".format(methods))
        if method == cv2.BORDER_CONSTANT:
            return cv2.copyMakeBorder(
                image, size, size, size, size,
                cv2.BORDER_CONSTANT, value
            )

        else:
            return cv2.copyMakeBorder(
                image, size, size, size, size,
                cv2.BORDER_REPLICATE
            )

    def open_and_close_image(self, image, iterations=2):
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
        opened = cv2.morphologyEx(
            image, cv2.MORPH_OPEN, None,
            iterations=iterations
        )
        # close the image, fill up inner regions
        closed = cv2.morphologyEx(
            opened, cv2.MORPH_CLOSE, None,
            iterations=iterations
        )
        return closed

    def max_closed_contour(self, image):
        contours, hierarchy = cv2.findContours(
            image,
            cv2.RETR_CCOMP,
            cv2.CHAIN_APPROX_NONE
        )
        contours = np.array(contours)
        hierarchy = hierarchy.reshape(len(contours), 4)

        # criterion for closed contour
        closed = (hierarchy[:, 2] < 0)

        # now find the largest closed contour
        shapes = np.array([c.shape[0] for c in contours])
        contour = contours[closed][shapes[closed].argmax()].reshape(-1, 2)

        return contour

    def fill_contour(self, image_bw, contour, color=(255, 0, 0)):
        '''
        Return a copy of image with contour filled in with color

        Parameters
        ----------
        image_bw : array
            grayscale image
        contour : array with polygon points
            cv2 contour
        color : (R, G, B) array or single value

        Returns
        -------
        image_contour : array
            image with the contour filled
        '''
        color = np.atleast_1d(color).astype(int)
        if color.shape[0] == 3:
            image_rgb = cv2.cvtColor(image_bw, cv2.COLOR_GRAY2RGB)
            image_contour = cv2.fillPoly(
                image_rgb,
                pts=[contour],
                color=color.tolist()
            )
        elif color.shape[0] == 1:
            temp = np.copy(image_bw)
            image_contour = cv2.fillPoly(
                np.uint8(temp),
                pts=[contour],
                color=color.tolist()
            )

        return image_contour

    def center_on_contour(self, image, contour):
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
        # contour has (x, y) coordinates -> swap to rows, columns for slicing
        # image
        mx = np.max(contour[:, ::-1], axis=0)
        mn = np.min(contour[:, ::-1], axis=0)

        # calculate the center + the extent in along both axes
        center = np.round((mx + mn) / 2.).astype(int)
        extent = np.round((mx - mn) / 2.).astype(int)

        centered = image[center[0] - extent[0]:center[0] + extent[0]+1,
                         center[1] - extent[1]:center[1] + extent[1]+1]

        return centered

    def slice_intervals(self, image, contour,
                        intervals=np.linspace(0, 1, 50),
                        save=True):
        '''
        Slice the contour in image at the given intervals along the maximum
        extent. The central coordinates, the intersections between the
        slices and the contour, the normalized centers and the intersections
        normalized by the geometric mean of the total widths are returned.

        Parameters
        ----------
        image : array
            image to center on contour
        contour : array with polygon points
            cv2 contour
        intervals : array
            fractional slices along maximum extent
        save : bool
            save information to csv file

        Returns
        -------
        centers : array
            center (x, y) coordinates
        coords : array
            lower and upper slice intersections
        centers_norm : array
            center (x, y) coordinates normalized to tip of tool
        coords_norm : array
            lower and upper slice intersections, with minimum extent
            coordinates normalized by the geometric mean of the widths
            along this direction
        '''
        # get maximum and minimum value of the contour along both axes
        # contour has (x, y) coordinates -> swap to rows, columns for slicing
        # image
        mx = np.max(contour[:, ::-1], axis=0)
        mn = np.min(contour[:, ::-1], axis=0)

        # calculate the extent along rows, columns
        center = np.round((mx + mn) / 2.).astype(int)
        extent = np.round(mx - mn).astype(int)

        # get the interval slices by multiplying extent with scaling
        slice_idx = (mn.reshape(-1, 1) + extent.reshape(-1, 1) *
                     intervals.reshape(1, -1))[np.argmax(extent)].astype(int)

        # set all intervals to slices
        slices = [slice(None), slice(None)]
        slices[np.argmax(extent)] = slice_idx[np.argmax(extent)]

        # get the center (row, column) coordinates for each interval
        centers = np.zeros((slice_idx.shape[-1], 2), dtype=int)
        centers[:, np.argmax(extent)] = slice_idx
        centers[:, np.argmin(extent)] = center[np.argmin(extent)]

        coords = np.empty((0, 2), dtype=int)
        for sl in slice_idx:
            # find the (x, y) coordinates of the contour that match the slice
            # and convert back to (row, column)
            match = (contour[:, ::-1][:, np.argmax(extent)].reshape(-1, 1)
                     == sl.reshape(1, -1)).any(axis=1)
            # only get the smallest and largest value along the perpendicular
            # direction
            slice_edge = contour[:, ::-1][match, np.argmin(extent)]
            min_max_idx = [np.argmin(slice_edge), np.argmax(slice_edge)]
            coords = np.concatenate(
                [
                    coords, contour[:, ::-1][match][min_max_idx]
                ],
                axis=0)

        centers_norm = centers - centers[0]
        coords_norm = (coords.reshape(coords.shape[0] // 2, 2, 2) -
                       centers[0]).reshape(centers.shape[0], 4).astype(float)

        # get the coordinates for the lower and upper intersections
        lower = coords_norm.reshape(-1, 2, 2)[:, 0, :]
        upper = coords_norm.reshape(-1, 2, 2)[:, 1, :]
        # compute the width and the geometric mean
        d = np.linalg.norm(upper - lower, axis=1)
        geom_mean = stats.gmean(d)
        # normalize coordinates by the geometric mean
        lower[:, np.argmin(extent)] /= geom_mean
        upper[:, np.argmin(extent)] /= geom_mean

        if save:
            # longest axis along columns
            if np.argmax(extent) == 1:
                centers_x = centers[:, 1].reshape(-1, 1)
                centers_y = centers[:, 0].reshape(-1, 1)
                lower_x = lower[:, 1].reshape(-1, 1)
                lower_y = lower[:, 0].reshape(-1, 1)
                upper_x = upper[:, 1].reshape(-1, 1)
                upper_y = upper[:, 0].reshape(-1, 1)
            # longest axis along rows -> flip to keep things consistent
            elif np.argmax(extent) == 0:
                centers_x = centers[:, 0].reshape(-1, 1)
                centers_y = centers[:, 1].reshape(-1, 1)
                lower_x = lower[:, 0].reshape(-1, 1)
                lower_y = lower[:, 1].reshape(-1, 1)
                upper_x = upper[:, 0].reshape(-1, 1)
                upper_y = upper[:, 1].reshape(-1, 1)

            info = np.concatenate([intervals.reshape(-1, 1),
                                   centers,
                                   coords.reshape(coords.shape[0] // 2, 4),
                                   centers_x - centers_x[0],
                                   centers_y - centers_y[0],
                                   lower_x, lower_y,
                                   upper_x, upper_y],
                                  axis=-1)

            np.savetxt(self.save_dir + self.img_name + "_slices.csv",
                       info, delimiter=",",
                       fmt=[
                           "%.3f", "%i", "%i", "%i", "%i", "%i", "%i",
                           "%i", "%i", "%.3f", "%.3f", "%.3f", "%.3f"
                       ],
                       header=(
                           "interval, true center x, true center y, "
                           "true lower x, true lower y, "
                           "true upper x, true upper y, "
                           "center norm long, center norm short, "
                           "lower norm long, lower norm short, "
                           "upper norm long, upper norm short"
                       ))
        else:
            return (
                centers[:, ::-1], coords[:, ::-1],
                centers_norm[:, ::-1], coords_norm[:, ::-1]
            )

    def calculate_asymmetry(self, image):
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
            # need to invert image, since the contour is filled with zeroes
            A = np.float(diff.sum()) / (~image.astype(bool)).sum()
        except ZeroDivisionError:
            A = 1.

        return A, np.uint8(diff) * 255
