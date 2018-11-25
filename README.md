# AScheck
This script computes the asymmetry index of the biggest assumed object
in an image. It greatly simplifies the task of classifying the
asymmetry of large samples of bifaces.

The object is found by reading in an image and then binarizing it in
the object and the background. The contour of the object is computed
and the object is flipped along its longest axis. The difference in
pixels between the minimum and the maximum symmetric outline defines
the asymmetric pixels. Dividing this number by the total number of
pixels in the object, gives the asymmetry index.

Go to the (official
release)[https://github.com/StijnDebackere/AScheck/releases]

# Usage
## Downloading executable
Download the [zip
file](https://github.com/StijnDebackere/AScheck/blob/v0.1/ascheck.zip). In
the `ascheck` folder, locate the `ascheck` file and double click it.

![alt
text](https://github.com/StijnDebackere/AScheck/blob/master/examples/ascheck_decompressed.png
"Decompressed zip folder")

![alt
text](https://github.com/StijnDebackere/AScheck/blob/master/examples/ascheck_folder.png
"ascheck file in folder")

After double clicking, a dialog will open asking you for the folder
that contains your images.

![alt
text](https://github.com/StijnDebackere/AScheck/blob/master/examples/ascheck_dialog.png
"ascheck asking for folder")

Choose the right folder and the program will run, creating a folder
`bw/` in the selected folder where it saves the black and white
outlines and it will save the asymmetry indices in a file called
`ascheck_results.txt`.

## Running from source
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

# Example
We start out with the image of a biface.

![alt text](https://github.com/StijnDebackere/AScheck/blob/master/examples/example.jpg "Biface image")

This image is then converted into a grayscale and the object is separated from the background. Now we have a black and white image of the biface for which we can find the contour.

![alt text](https://github.com/StijnDebackere/AScheck/blob/master/examples/example_bw.jpg "Biface image black and white")

The contour can then be flipped around the longest axis of the biface, which is assumed to be the axis of symmetry. By taking the difference between the minimum and maximum symmetric outlines, we find the number of asymmetric pixels.

![alt text](https://github.com/StijnDebackere/AScheck/blob/master/examples/example_asymmetric_pixels.jpg "Asymmetric pixels")

# Issues
The object detection in the script is automatic and it assumes that the
foreground object is clearly marked against the background. Do not put the
object on a background with similar colours, since the script will fail in that
case.
