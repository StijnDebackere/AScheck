# AScheck
This script computes the asymmetry index of the biggest assumed object in an image. It was developed to compute the asymmetry of archaeological bifaces. It greatly simplifies the task of classifying the asymmetry of large samples of bifaces.

The object is found by reading in a grayscale image and then binarizing it in the object (which needs to have similar grayscale values) and the background using Otsu's method. The contour of the object is computed and the object is flipped alongst its longest axis. The difference in pixels between the minimum and the maximum symmetric outline defines the asymmetric pixels. Dividing this number by the total number of pixels in the object, gives the asymmetry index.

# Example
We start out with the image of a rock.

![alt text](https://github.com/StijnDebackere/AScheck/blob/master/example.jpg "Rock image")

This image is then converted into a grayscale and the object is separated from the background. Now we have a black and white image of the rock for which we can find the contour.

![alt text](https://github.com/StijnDebackere/AScheck/blob/master/example_bw.jpg "Rock image black and white")

The contour can then be flipped around the longest axis of the rock, which is assumed to be the axis of symmetry. By taking the difference between the minimum and maximum symmetric outlines, we find the number of asymmetric pixels.

![alt text](https://github.com/StijnDebackere/AScheck/blob/master/example_asymmetric_pixels.jpg "Asymmetric pixels")

# Usage
Currently, the script is very basic. It can be run by opening up your terminal and navigating to the directory where you keep the script. Make the script executable for you by running

```bash
chmod u+x ascheck.py
```

Then, you can run the script on a directory containing your images, e.g. path/to/images, with extension ext, e.g. jpg, by invoking

```bash
./ascheck.py path/to/images jpg
```

The script will create a folder bw in path/to/images where it saves the black and white outlines and it will save the asymmetry indices in a file called ascheck_results_folder.txt, where folder is the final folder in path/to/images.

This text file contains the image filename and its asymmetry index.
