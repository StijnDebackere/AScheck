# AScheck
This script can easily load and perform calculations on a directory of
images.

Functionality can be added to the `core.ascheck.Image` class. This can
then be called from the `ascheck` script.

The script can find the biggest assumed object in an image by
binarizing it in the object and the background. The contour of the
object can then easily be found.

Currently, the script can compute the asymmetry index of the biggest
assumed object in an image and it can compute the width of the object
at a given set of intervals along its longest dimension.

The assymetry of the object can be computed by flipping it along its
longest axis. The difference in pixels between the minimum and the
maximum symmetric outline defines the asymmetric pixels. Dividing this
number by the total number of pixels in the object, gives the
asymmetry index.

## Installation

### Using pip

`ascheck` is available on [PyPI](https://pypi.org/), install using

```
pip install ascheck --upgrade
```

After installing, simply open a terminal and type the following command

```
ascheck
```

### Github

The package can be installed from Github by running the following
commands in the preferred installation location:
```
git clone https://github.com/StijnDebackere/AScheck
cd AScheck
python3 setup.py install
```

After installing, simply open a terminal and type the following command

```
ascheck
```

## Usage
After installing the package, you should be able to run it from
anywhere within the terminal 
![alt
text](https://github.com/StijnDebackere/AScheck/blob/master/examples/ascheck_terminal.png
"run ascheck in terminal")

A dialog will open asking you for the folder that contains your
images.

![alt
text](https://github.com/StijnDebackere/AScheck/blob/master/examples/ascheck_dialog.png
"ascheck asking for folder")

Choose the folder and the program will ask some questions: do you want
to compute the asymmetry?

![alt
text](https://github.com/StijnDebackere/AScheck/blob/master/examples/ascheck_dialog_asymmetry.png
"compute asymmetry?")

Optionally, diagnostic images can also be saved to check whether
anything went wrong in the automatic object detection.

![alt
text](https://github.com/StijnDebackere/AScheck/blob/master/examples/ascheck_dialog_diagnostics.png
"save diagnostics?")

We also ask whether you want to compute the slices

![alt
text](https://github.com/StijnDebackere/AScheck/blob/master/examples/ascheck_dialog_slices.png
"compute slices?")

and how many

![alt
text](https://github.com/StijnDebackere/AScheck/blob/master/examples/ascheck_dialog_n_slices.png
"compute slices?")

again, with optional diagnostics.


### Outputs
The asymmetry calculation creates a folder `bw/` in the selected
folder where it saves the black and white outlines and it will save
the asymmetry indices in a file called `ascheck_results.txt`. This
text file contains the image filename, its asymmetry index and a flag
for the trustworthiness of the result.

As diagnostic, the following images are saved:
- image\_name\_asym.ext: black and white image of the asymmetric pixels
- image\_name\_contour.ext: grayscale image with the contour filled in red

![alt
text](https://github.com/StijnDebackere/AScheck/blob/master/examples/example_asym.jpg 
"asymmetric pixels")
![alt
text](https://github.com/StijnDebackere/AScheck/blob/master/examples/example_contour.jpg 
"contour filled")


The object widths calculation creates a folder `slices/` in the
selected folder where it saves `.csv` files with the coordinates of
each interval and the lower and upper intersections with the object
outline. It also provides the coordinates in normalized form, where
the widths are divided by the geometric mean of the widths of all
intervals.

As diagnostic, the object and all the coordinates are saved in
- image\_name\_slices.ext: grayscale image with contour filled in red,
  the central intervals indicated with crosses, and the intersections
  with dots.

![alt
text](https://github.com/StijnDebackere/AScheck/blob/master/examples/example_slices.jpg 
"contour with intervals and intersections")


## Example
We start out with the image of a biface.

![alt text](https://github.com/StijnDebackere/AScheck/blob/master/examples/example.jpg "Biface image")

This image is then converted into a grayscale and the object is
separated from the background. Now we have a black and white image of
the biface for which we can find the contour.

![alt text](https://github.com/StijnDebackere/AScheck/blob/master/examples/example_bw.jpg "Biface image black and white")

The contour can then be flipped around the longest axis of the biface,
which is assumed to be the axis of symmetry. By taking the difference
between the minimum and maximum symmetric outlines, we find the number
of asymmetric pixels.

![alt text](https://github.com/StijnDebackere/AScheck/blob/master/examples/example_asymmetric_pixels.jpg "Asymmetric pixels")

Computing the intervals along the longest axis, the intersections with
the contour can then be found.

![alt
text](https://github.com/StijnDebackere/AScheck/blob/master/examples/example_slices.jpg 
"contour with intervals and intersections")

## Issues
The object detection in the script is automatic and it assumes that
the foreground object is clearly marked against the background. Do not
put the object on a background with similar colours, since the script
will fail in that case. Diagnostic images should enable you to see
whether everything went OK.
