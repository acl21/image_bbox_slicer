"""
Resizer functionality of ``image_bbox_slicer``.
"""
import os
import csv
import glob
import random
from PIL import Image
from pascal_voc_writer import Writer
from .helpers import *


class Resizer(object):
    """
    Resizer class.

    Attributes
    ----------
    IMG_SRC : str
        /path/to/images/source/directory.
        Default value is the current working directory.
    IMG_DST : str
        /path/to/images/destination/directory.
        Default value is the `/resized_images` in the current working directory.
    ANN_SRC : str
        /path/to/annotations/source/directory.
        Default value is the current working directory.
    ANN_DST : str
        /path/to/annotations/source/directory.
        Default value is the `/resized_annotations` in the current working directory.
    """

    def __init__(self):
        """
        Constructor.

        Assigns default values to path attributes and other preference attributes.

        Parameters
        ----------
        None
        """
        self.IMG_SRC = os.getcwd()
        self.IMG_DST = os.path.join(os.getcwd(), 'resized_images')
        self.ANN_SRC = os.getcwd()
        self.ANN_DST = os.path.join(os.getcwd(), 'resized_annotations')

    def config_dirs(self, img_src, ann_src,
                    img_dst=os.path.join(os.getcwd(), 'resized_images'),
                    ann_dst=os.path.join(os.getcwd(), 'resized_annotations')):
        """Configures paths to source and destination directories after validating them.

        Parameters
        ----------
        img_src : str
            /path/to/image/source/directory
        ann_src : str
            /path/to/annotation/source/directory
        img_dst : str, optional
            /path/to/image/destination/directory
            Default value is `/resized_images`.
        ann_dst : str, optional
            /path/to/annotation/destination/directory
            Default value is `/resized_annotations`.

        Returns
        ----------
        None
        """
        validate_dir(img_src)
        validate_dir(ann_src)
        validate_dir(img_dst, src=False)
        validate_dir(ann_dst, src=False)
        validate_file_names(img_src, ann_src)
        self.IMG_SRC = img_src
        self.IMG_DST = img_dst
        self.ANN_SRC = ann_src
        self.ANN_DST = ann_dst

    def config_image_dirs(self, img_src, img_dst=os.path.join(os.getcwd(), 'resized_images')):
        """Configures paths to source and destination directories after validating them.
        Suitable when doing only image resizing.

        Parameters
        ----------
        img_src : str
            /path/to/image/source/directory
        img_dst : str, optional
            /path/to/image/destination/directory
            Default value is `/resized_images`.

        Returns
        ----------
        None
        """
        validate_dir(img_src)
        validate_dir(img_dst, src=False)
        self.IMG_SRC = img_src
        self.IMG_DST = img_dst

    def config_ann_dirs(self, ann_src, ann_dst=os.path.join(os.getcwd(), 'resized_annotations')):
        """Configures paths to source and destination directories after validating them.
        Suitable when doing only annotations resizing.

        Parameters
        ----------
        ann_src : str
            /path/to/annotation/source/directory
        ann_dst : str, optional
            /path/to/annotation/destination/directory
            Default value is `/resized_annotations`.

        Returns
        ----------
        None
        """
        validate_dir(ann_src)
        validate_dir(ann_dst, src=False)
        self.ANN_SRC = ann_src
        self.ANN_DST = ann_dst

    def resize_by_size(self, new_size, resample=0):
        """Resizes both images and box annotations in source directories to specified size `new_size`.

        Parameters
        ----------
        new_size : tuple
            The requested size in pixels, as a 2-tuple: (width, height)
        resample: int, optional
            An optional resampling filter, same as the one used in PIL.Image.resize() function.
            Check it out at https://pillow.readthedocs.io/en/3.1.x/reference/Image.html#PIL.Image.Image.resize
            `0` (Default) for NEAREST (nearest neighbour)
            `1` for LANCZOS/ANTIALIAS (a high-quality downsampling filter)
            `2` for BILINEAR/LINEAR (linear interpolation)
            `3` for BICUBIC/CUBIC (cubic spline interpolation)

        Returns
        ----------
        None
        """
        self.resize_images_by_size(new_size, resample)
        self.resize_bboxes_by_size(new_size)

    def resize_images_by_size(self, new_size, resample=0):
        """Resizes images in the image source directory to specified size `new_size`.

        Parameters
        ----------
        new_size : tuple
            The requested size in pixels, as a 2-tuple: (width, height)
        resample: int, optional
            An optional resampling filter, same as the one used in PIL.Image.resize() function.
            Check it out at https://pillow.readthedocs.io/en/3.1.x/reference/Image.html#PIL.Image.Image.resize
            `0` (Default) for NEAREST (nearest neighbour)
            `1` for LANCZOS/ANTIALIAS (a high-quality downsampling filter)
            `2` for BILINEAR/LINEAR (linear interpolation)
            `3` for BICUBIC/CUBIC (cubic spline interpolation)

        Returns
        ----------
        None
        """
        validate_new_size(new_size)
        self.__resize_images(new_size, resample, None)

    def resize_by_factor(self, resize_factor, resample=0):
        """Resizes both images and annotations in the source directories by a scaling/resizing factor.

        Parameters
        ----------
        resize_factor : float
            A factor by which the images and the annotations should be scaled.
        resample: int, optional
            An optional resampling filter, same as the one used in PIL.Image.resize() function.
            Check it out at https://pillow.readthedocs.io/en/3.1.x/reference/Image.html#PIL.Image.Image.resize
            `0` (Default) for NEAREST (nearest neighbour)
            `1` for LANCZOS/ANTIALIAS (a high-quality downsampling filter)
            `2` for BILINEAR/LINEAR (linear interpolation)
            `3` for BICUBIC/CUBIC (cubic spline interpolation)

        Returns
        ----------
        None
        """
        validate_resize_factor(resize_factor)
        self.resize_images_by_factor(resize_factor, resample)
        self.resize_bboxes_by_factor(resize_factor)

    def resize_images_by_factor(self, resize_factor, resample=0):
        """Resizes images in the image source directory by a scaling/resizing factor.

        Parameters
        ----------
        resize_factor : float
            A factor by which the images should be scaled.
        resample: int, optional
            An optional resampling filter, same as the one used in PIL.Image.resize() function.
            Check it out at https://pillow.readthedocs.io/en/3.1.x/reference/Image.html#PIL.Image.Image.resize
            `0` (Default) for NEAREST (nearest neighbour)
            `1` for LANCZOS/ANTIALIAS (a high-quality downsampling filter)
            `2` for BILINEAR/LINEAR (linear interpolation)
            `3` for BICUBIC/CUBIC (cubic spline interpolation)

        Returns
        ----------
        None
        """
        validate_resize_factor(resize_factor)
        self.__resize_images(None, resample, resize_factor)

    def __resize_images(self, new_size, resample, resize_factor):
        """Private Method
        """
        for file in sorted(glob.glob(self.IMG_SRC + os.sep + "*")):
            file_name = file.split(os.sep)[-1].split('.')[0]
            file_type = file.split(os.sep)[-1].split('.')[-1].lower()
            if file_type not in IMG_FORMAT_LIST:
                continue
            im = Image.open(file)
            if resize_factor is not None:
                new_size = [0, 0]
                new_size[0] = int(im.size[0] * resize_factor)
                new_size[1] = int(im.size[1] * resize_factor)
                new_size = tuple(new_size)

            new_im = im.resize(size=new_size, resample=resample)
            new_im.save('{}{}{}.{}'.format(self.IMG_DST, os.sep, file_name, file_type))

    def resize_bboxes_by_size(self, new_size):
        """Resizes bounding box annotations in the source directory to specified size `new_size`.

        Parameters
        ----------
        new_size : tuple
            The requested size in pixels, as a 2-tuple: (width, height)

        Returns
        ----------
        None
        """
        validate_new_size(new_size)
        self.__resize_bboxes(new_size, None)

    def resize_bboxes_by_factor(self, resize_factor):
        """Resizes bounding box annotations in the source directory by a scaling/resizing factor.

        Parameters
        ----------
        resize_factor : float
            A factor by which the bounding box annotations should be scaled.

        Returns
        ----------
        None
        """
        validate_resize_factor(resize_factor)
        self.__resize_bboxes(None, resize_factor)

    def __resize_bboxes(self, new_size, resize_factor):
        """Private Method
        """
        for xml_file in sorted(glob.glob(self.ANN_SRC + os.sep + '*.xml')):
            root, objects = extract_from_xml(xml_file)
            im_w, im_h = int(root.find('size')[0].text), int(
                root.find('size')[1].text)
            im_filename = os.path.splitext(root.find('filename').text)[0]
            an_filename = xml_file.split(os.sep)[-1].split('.')[0]
            extn = os.path.splitext(root.find('filename').text)[1]
            if resize_factor is None:
                w_scale, h_scale = new_size[0]/im_w, new_size[1]/im_h
            else:
                w_scale, h_scale = resize_factor, resize_factor
                new_size = [0, 0]
                new_size[0], new_size[1] = int(
                    im_w * w_scale), int(im_h * h_scale)
                new_size = tuple(new_size)

            voc_writer = Writer(
                '{}{}{}{}'.format(self.ANN_DST, os.sep, im_filename, extn), new_size[0], new_size[1])

            for obj in objects:
                obj_lbl = list(obj[-4:])
                obj_lbl[0] = int(obj_lbl[0] * w_scale)
                obj_lbl[1] = int(obj_lbl[1] * h_scale)
                obj_lbl[2] = int(obj_lbl[2] * w_scale)
                obj_lbl[3] = int(obj_lbl[3] * h_scale)

                voc_writer.addObject(obj[0], obj_lbl[0], obj_lbl[1], obj_lbl[2], obj_lbl[3],
                                     obj[1], obj[2], obj[3])
            voc_writer.save('{}{}{}.xml'.format(self.ANN_DST, os.sep, an_filename))

    def visualize_resized_random(self):
        """Picks an image randomly and visualizes original and resized images using `matplotlib`

        Parameters:
        ----------
        None

        Returns:
        ----------
        None
            However, displays the final plots.
        """
        im_file = random.choice(list(glob.glob('{}{}*'.format(self.IMG_SRC, os.sep))))
        file_name = im_file.split(os.sep)[-1].split('.')[0]

        plot_image_boxes(self.IMG_SRC, self.ANN_SRC, file_name)
        plot_image_boxes(self.IMG_DST, self.ANN_DST, file_name)
