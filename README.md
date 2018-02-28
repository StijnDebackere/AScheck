# AScheck
This script computes the asymmetry index of the biggest assumed object in an image.

The object is found by reading in a grayscale image and then binarizing it in the object (which needs to have similar grayscale values) and the background using Otsu's method. The contour of the object is computed and the object is flipped alongst its longest axis. The difference in pixels between the minimum and the maximum symmetric outline defines the asymmetric pixels. Dividing this number by the total number of pixels in the object, gives the asymmetry index.
