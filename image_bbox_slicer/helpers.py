"""
Helper functions for ``image_bbox_slicer``.
"""
import os
import glob
import warnings
import numpy as np
from PIL import Image
from enum import Enum
from itertools import compress
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import xml.etree.ElementTree as ET
from math import sqrt, ceil, floor


IMG_FORMAT_LIST = ['jpg', 'jpeg', 'png', 'tiff', 'exif', 'bmp']

# Source : Sam Dobson
# https://github.com/samdobson/image_slicer


def calc_columns_rows(n):
    """Calculates the number of columns and rows required to divide an image
    into equal parts.

    Parameters
    ----------
    n : int
        The number of equals parts an image should be split into.

    Returns
    ----------
    tuple
        Size required to divide an image into in pixels, as a 2-tuple: (columns, rows)..
    """
    num_columns = int(ceil(sqrt(n)))
    num_rows = int(ceil(n / float(num_columns)))
    return (num_columns, num_rows)


def validate_number_tiles(number_tiles):
    """Validates the sanity of the number of tiles asked for.

    Parameters
    ----------
    number_tiles : int
        The number of tiles.

    Returns
    ----------
    None

    Raises
    ----------
    ValueError
        If `number_tiles` can not be casted to integer.
        If `number_tiles` value is less than `2`.
        If `number_tiles` value is more than `TILE_LIMIT` (99 * 99)
    """
    if number_tiles is not None:
        TILE_LIMIT = 99 * 99

        try:
            number_tiles = int(number_tiles)
        except ValueError:
            raise ValueError('number_tiles could not be cast to integer.')

        if number_tiles > TILE_LIMIT or number_tiles < 2:
            raise ValueError('Number of tiles must be between 2 (inclusive) and {} (you asked for {}).'.format(
                TILE_LIMIT, number_tiles))


def validate_dir(dir_path, src=True):
    """Validates if provided directory path exists or not.

    Creates directory when in destination mode if don't exist.

    Parameters
    ----------
    dir_path : str
        path/to/directory
    src : bool, optional
        Default value is `True`.
        Flag to denote if method is called in source mode or destination mode.
        Must be set to False when validating destination directories

    Returns
    ----------
    None

    Raises
    ----------
    FileNotFoundError
        If `src` is `True` and `dir_path` directory either doesn't exist or is empty.
    UserWarning
        If `src` is `False` and `dir_path` directory either doesn't exist or already has files.
    """
    if src:
        if os.path.isdir(dir_path):
            if not os.listdir(dir_path):
                raise FileNotFoundError(
                    'No files found in source directory {}'.format(dir_path))
        else:
            raise FileNotFoundError(
                'Source directory {} not found.'.format(dir_path))
    else:
        if os.path.isdir(dir_path):
            if os.listdir(dir_path):
                warnings.warn(
                    'Destination directory {} already has some files'.format(dir_path))
        else:
            warnings.warn(
                'Destination {} directory does not exist so creating it now'.format(dir_path))
            os.makedirs(dir_path, exist_ok=True)


def validate_file_names(img_src, ann_src):
    """Validates if image and annotation source directories have corresponding and matching file names.

    Parameters
    ----------
    img_src : str
        path/to/image/source/directory
    ann_src : str
        path/to/annotations/source/directory

    Returns
    ----------
    None

    Raises
    ----------
    Exception
        If `img_src` and `ann_src` do not have matching image and annotation file names respectively.
    """
    imgs = sorted(glob.glob(img_src + os.sep + '*'))
    anns = sorted(glob.glob(ann_src + os.sep + '*.xml'))

    imgs_filter = [True if x.split(
        '.')[-1].lower() in IMG_FORMAT_LIST else False for x in imgs]
    imgs = list(compress(imgs, imgs_filter))

    imgs = [os.path.splitext(x.split(os.sep)[-1])[0] for x in imgs]
    anns = [os.path.splitext(x.split(os.sep)[-1])[0] for x in anns]

    if not (imgs == anns):
        raise Exception(
            'Each image in `{}` must have its corresponding XML file in `{}` \
            with the same file name.'.format(img_src, ann_src))


def validate_overlap(tile_overlap):
    """Validates overlap parameter passed to slicing methods.

    Parameters
    ----------
    tile_overlap : float
        The value denotes the overlap between two consecutive strides.

    Returns
    ----------
    None

    Raises
    ----------
    ValueError
        When `tile_overlap` value is not between `0` and `1`, inclusive.
    """
    if not (0.0 <= tile_overlap <= 1.0):
        raise ValueError(
            'Tile overlap percentage should be between 0 and 1, inclusive. \
                The value provided was {}'.format(tile_overlap))


def validate_tile_size(tile_size, img_size=None):
    """Validates tile size argument provided for slicing.

    Parameters
    ----------
    tile_size : tuple
        Size of each tile in pixels, as a 2-tuple: (width, height).
    img_size : tuple, optional
        Size of original image in pixels, as a 2-tuple: (width, height).

    Returns
    ----------
    None

    Raises
    ----------
    ValueError
        If `tile_size` does not hold exactly `2` values
        If `tile_size` does not comply with `img_size`
    TypeError
        If `tile_size` or `img_size` are not of type tuple.
    """
    if img_size is None:
        if isinstance(tile_size, tuple):
            if len(tile_size) != 2:
                raise ValueError(
                    'Tile size must be a tuple of size 2 i.e., (w, h). The tuple provided was {}'.format(tile_size))
        else:
            raise TypeError(
                'Tile size must be a tuple. The argument was of type {}'.format(type(tile_size)))
    else:
        if isinstance(img_size, tuple):
            if (sum(tile_size) >= sum(img_size)) or (tile_size[0] > img_size[0]) or (tile_size[1] > img_size[1]):
                raise ValueError('Tile size cannot exceed image size. Tile size was {} while image size was {}'.format(
                    tile_size, img_size))
        else:
            raise TypeError(
                'Image size must be a tuple. The argument was of type {}'.format(type(img_size)))


def validate_new_size(new_size):
    """Validates `new_size` argument.

    Parameters
    ----------
    new_size : tuple
        The requested size in pixels, as a 2-tuple: (width, height)

    Returns
    ----------
    None

    Raises
    ----------
    TypeError
        When `new_size` is not a tuple.
    ValueError
        When `new_size` is a tuple but not a 2-tuple
    """
    if not isinstance(new_size, tuple):
        raise TypeError(
            'Image size must be a tuple. The argument was of type {}'.format(type(new_size)))
    else:
        if len(new_size) != 2:
            raise ValueError(
                'Image size must be a tuple of size 2 i.e., (w, h). The tuple provided was {}'.format(new_size))


def validate_resize_factor(factor):
    """Validates resizing/scaling factor argument.

    Parameters
    ----------
    factor : float
        A factor by which the images or the bounding box annotations should be scaled.

    Returns
    ----------
    None

    Raises
    ----------
    ValueError
        When `factor` is not positive.
    """
    if factor <= 0:
        raise ValueError(
            'Resize factor must be positive. The value provided was {}'.format(factor))


def save_before_after_map_csv(mapper, path):
    """Saves a dictionary in a csv file.

    Parameters
    ----------
    mapper : dict
        Dictionary containing pre-sliced file names as keys and their respective sliced file names as values.
    path : str
        /path/to/target/directory

    Returns
    ----------
    None
    """
    with open('{}{}mapper.csv'.format(path, os.sep), 'w') as f:
        f.write("old_name,new_names\n")
        for key in mapper.keys():
            f.write("%s,%s\n" % (key, ','.join(mapper[key])))
    print('Successfully saved the mapping between files before and after slicing at {}'.format(path))


def extract_from_xml(file):
    """Extracts useful info (classes, bounding boxes, filename etc.) from annotation (XML) file.

    Parameters
    ----------
    file : str
        /path/to/xml/file.

    Returns
    ----------
    Element, list
        Element is the root of the XML tree.
        list contains info of annotations (objects) in the file.
    """
    objects = []
    tree = ET.parse(file)
    root = tree.getroot()
    for obj in root.findall('object'):
        name = obj.find('name').text
        pose = 'Unknown'
        truncated = '0'
        difficult = '0'
        if obj.find('pose') is not None:
            pose = obj.find('pose').text

        if obj.find('truncated') is not None:
            truncated = obj.find('truncated').text

        if obj.find('difficult') is not None:
            difficult = obj.find('difficult').text

        bbox = obj.find('bndbox')
        xmin, ymin, xmax, ymax = 0, 0, 0, 0
        for point in bbox:
            if point.tag == 'xmin':
                xmin = point.text
            elif point.tag == 'ymin':
                ymin = point.text
            elif point.tag == 'xmax':
                xmax = point.text
            elif point.tag == 'ymax':
                ymax = point.text
        value = (name,
                 pose,
                 int(truncated),
                 int(difficult),
                 int(xmin.split('.')[0]),
                 int(ymin.split('.')[0]),
                 int(xmax.split('.')[0]),
                 int(ymax.split('.')[0])
                 )
        objects.append(value)
    return root, objects


def plot_image_boxes(img_path, ann_path, file_name):
    """Plots bounding boxes on images using `matplotlib`.

    Works in two modes - unsliced and sliced modes.
    In unsliced mode, only one picture is plotted.
    In sliced mode, all the slices are plotted.

    Parameters
    ----------
    img_path : str
        /path/to/image/source/directory
    ann_path : str
        /path/to/annotation/source/directory
    file_name : str or list
        Name of the file (in unsliced mode).
        List of file names (in sliced mode).

    Returns
    ----------
    None
    """

    # Checking if the file is a source image as the data type
    # Source image - string, tile images - list of strings
    if isinstance(file_name, str):
        tree = ET.parse(ann_path + os.sep + file_name + '.xml')
        root = tree.getroot()

        im = Image.open(img_path + os.sep + file_name + '.jpg')
        im = np.array(im, dtype=np.uint8)

        rois = []
        for member in root.findall('object'):
            rois.append((int(member[4][0].text), int(member[4][1].text),
                         int(member[4][2].text), int(member[4][3].text)))

        # Create figure and axes
        fig, ax = plt.subplots(1, figsize=(10, 10))

        # Display the image
        ax.imshow(im)

        for roi in rois:
            # Create a Rectangle patch
            rect = patches.Rectangle((roi[0], roi[1]), roi[2]-roi[0], roi[3]-roi[1],
                                     linewidth=3, edgecolor='b', facecolor='none')

            # Add the patch to the Axes
            ax.add_patch(rect)
    else:
        cols, rows = calc_columns_rows(len(file_name))
        pos = []
        for i in range(0, rows):
            for j in range(0, cols):
                pos.append((i, j))
        fig, ax = plt.subplots(rows, cols, sharex='col',
                               sharey='row', figsize=(10, 7))
        for idx, file in enumerate(file_name):

            tree = ET.parse(ann_path + os.sep + file + '.xml')
            root = tree.getroot()

            im = Image.open(img_path + os.sep + file + '.jpg')
            im = np.array(im, dtype=np.uint8)

            rois = []
            for member in root.findall('object'):
                rois.append((int(member[4][0].text), int(member[4][1].text),
                             int(member[4][2].text), int(member[4][3].text)))

            # Display the image at the right position
            ax[pos[idx][0], pos[idx][1]].imshow(im)

            for roi in rois:
                # Create a Rectangle patch
                rect = patches.Rectangle((roi[0], roi[1]), roi[2]-roi[0], roi[3]-roi[1],
                                         linewidth=3, edgecolor='b', facecolor='none')

                # Add the patch to the Axes
                ax[pos[idx][0], pos[idx][1]].add_patch(rect)
    plt.show()
