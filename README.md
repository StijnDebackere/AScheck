# AScheck
This script computes the asymmetry index of the biggest assumed object in an image. It was developed for Laurence Hutchence's MPhil thesis in archaeology to compute the asymmetry of archaeological bifaces. It greatly simplifies the task of classifying the asymmetry of large samples of bifaces.

The object is found by reading in a grayscale image and then binarizing it in the object (which needs to have similar grayscale values) and the background using Otsu's method. The contour of the object is computed and the object is flipped alongst its longest axis. The difference in pixels between the minimum and the maximum symmetric outline defines the asymmetric pixels. Dividing this number by the total number of pixels in the object, gives the asymmetry index.

# Example
We start out with the image of a biface.

![alt text](https://github.com/StijnDebackere/AScheck/blob/master/example.jpg "Biface image")

This image is then converted into a grayscale and the object is separated from the background. Now we have a black and white image of the biface for which we can find the contour.

![alt text](https://github.com/StijnDebackere/AScheck/blob/master/example_bw.jpg "Biface image black and white")

The contour can then be flipped around the longest axis of the biface, which is assumed to be the axis of symmetry. By taking the difference between the minimum and maximum symmetric outlines, we find the number of asymmetric pixels.

![alt text](https://github.com/StijnDebackere/AScheck/blob/master/example_asymmetric_pixels.jpg "Asymmetric pixels")

# Usage
To run the script, you will need a [Python 3](https://www.python.org/downloads/)
installation on your computer. This should be straightforward to install,
following the instructions given on the website. Moreover, you will need to
install the [NumPy](https://www.scipy.org/install.html),
[Matplotlib](https://matplotlib.org/users/installing.html) and
[opencv](https://pypi.org/project/opencv-python/) packages. Once all of these
are installed, everything else should be straightforward.

Go to the folder where you have the `ascheck.py` script and open a terminal at
this location (on a mac, this can be done by following the instructions
[here](https://stackoverflow.com/q/420456).

In the opened terminal window, type the following command:

```
python ascheck.py
```

A dialog will open asking you to select a folder where your images are
located. Once you have selected the folder, the script will create a folder `bw/`
in the selected folder where it saves the black and white outlines and it will
save the asymmetry indices in a file called `ascheck_results.txt`.

This text file contains the image filename, its asymmetry index and a flag for
the trustworthiness of the result.

# Issues
The object detection in the script is automatic and it assumes that the
foreground object is clearly marked against the background. Do not put the
object on a background with similar colours, since the script will fail in that
case.
