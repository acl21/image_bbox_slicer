"""
Main functionality of ``image_bbox_slicer``.
"""
import os
import csv
import glob
import random
from PIL import Image
from pascal_voc_writer import Writer
from .helpers import *


class Slicer(object):
    """
    Slicer class.

    Attributes
    ----------
    IMG_SRC : str
        /path/to/images/source/directory.
        Default value is the current working directory. 
    IMG_DST : str
        /path/to/images/destination/directory.
        Default value is the `/sliced_images` in the current working directory.
    ANN_SRC : str
        /path/to/annotations/source/directory.
        Default value is the current working directory.
    ANN_DST : str
        /path/to/annotations/source/directory.
        Default value is the `/sliced_annotations` in the current working directory.
    keep_partial_labels : bool
        A boolean flag to denote if the slicer should keep partial labels or not.
        Partial labels are the labels that are partly in a tile post slicing.
        Default value is `False`.
    save_before_after_map : bool
        A boolean flag to denote if mapping between 
        original file names and post-slicing file names in a csv or not. 
        Default value is `False`.
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
        self.IMG_DST = os.path.join(os.getcwd(), 'sliced_images')
        self.ANN_SRC = os.getcwd()
        self.ANN_DST = os.path.join(os.getcwd(), 'sliced_annotations')
        self.keep_partial_labels = False
        self.save_before_after_map = False

    def config_dirs(self, img_src, ann_src,
                    img_dst=os.path.join(os.getcwd(), 'sliced_images'),
                    ann_dst=os.path.join(os.getcwd(), 'sliced_annotations')):
        """Configures paths to source and destination directories after validating them. 

        Parameters
        ----------
        img_src : str
            /path/to/image/source/directory
        ann_src : str
            /path/to/annotation/source/directory
        img_dst : str, optional
            /path/to/image/destination/directory
            Default value is `/sliced_images`.
        ann_dst : str, optional
            /path/to/annotation/destination/directory
            Default value is `/sliced_annotations`.

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

    def get_tiles(self, img_size, tile_size, tile_overlap):
        """Generates a list coordinates of all the tiles after validating the values.

        Parameters
        ----------
        img_size : tuple
            Size (width, height) of the original image.
        tile_size : tuple
            Size (width, height) of each tile.
        tile_overlap: float  
            Percentage of tile overlap between two consecutive strides.

        Returns
        ----------
        list
            A list of tuples.
            Each holding coordinates of possible tiles 
            in the format - `(xmin, ymin, xmax, ymax)` 
        """
        validate_tile_size(tile_size, img_size)
        tiles = []
        img_w, img_h = img_size
        tile_w, tile_h = tile_size
        stride_w = int((1 - tile_overlap) * tile_w)
        stride_h = int((1 - tile_overlap) * tile_h)
        for y in range(0, img_h-tile_h+1, stride_h):
            for x in range(0, img_w-tile_w+1, stride_w):
                x2 = x + tile_w
                y2 = y + tile_h
                tiles.append((x, y, x2, y2))
        return tiles

    def slice_by_size(self, tile_size, tile_overlap=0.0):
        """Slices both images and box annotations in source directories by specified size and overlap.

        Parameters
        ----------
        tile_size : tuple
            Size (width, height) of each tile.
        tile_overlap: float, optional  
            Percentage of tile overlap between two consecutive strides.
            Default value is `0`.

        Returns
        ----------
        None
        """
        self.slice_images_by_size(tile_size, tile_overlap)
        self.slice_bboxes_by_size(tile_size, tile_overlap)

    def slice_by_number(self, number_tiles):
        """Slices both images and box annotations in source directories into specified number of tiles.

        Parameters
        ----------
        number_tiles : int
            The number of tiles an image needs to be sliced into.

        Returns
        ----------
        None
        """
        self.slice_images_by_number(number_tiles)
        self.slice_bboxes_by_number(number_tiles)

    def slice_images_by_size(self, tile_size, tile_overlap=0.0):
        """Slices each image in the source directory by specified size and overlap.

        Parameters
        ----------
        tile_size : tuple
            Size (width, height) of each tile.
        tile_overlap: float, optional  
            Percentage of tile overlap between two consecutive strides.
            Default value is `0`.

        Returns
        ----------
        None
        """
        validate_tile_size(tile_size)
        validate_overlap(tile_overlap)
        mapper = self.__slice_images(tile_size, tile_overlap, number_tiles=-1)
        if self.save_before_after_map:
            save_before_after_map_csv(mapper, self.IMG_DST)

    def slice_images_by_number(self, number_tiles):
        """Slices each image in the source directory into specified number of tiles.

        Parameters
        ----------
        number_tiles : int
            The number of tiles an image needs to be sliced into.

        Returns
        ----------
        None
        """
        validate_number_tiles(number_tiles)
        mapper = self.__slice_images(None, None, number_tiles=number_tiles)
        if self.save_before_after_map:
            save_before_after_map_csv(mapper, self.IMG_DST)

    def __slice_images(self, tile_size, tile_overlap, number_tiles):
        """
        Private Method
        """
        mapper = {}
        img_no = 1

        for file in sorted(glob.glob(self.IMG_SRC + "/*")):
            file_name = file.split('/')[-1].split('.')[0]
            file_type = file.split('/')[-1].split('.')[-1].lower()
            if file_type.lower() not in IMG_FORMAT_LIST:
                continue
            im = Image.open(file)

            if number_tiles > 0:
                n_cols, n_rows = calc_columns_rows(number_tiles)
                tile_w, tile_h = int(
                    floor(im.size[0] / n_cols)), int(floor(im.size[1] / n_rows))
                tile_size = (tile_w, tile_h)
                tile_overlap = 0.0

            tiles = self.get_tiles(im.size, tile_size, tile_overlap)
            new_ids = []
            for tile in tiles:
                new_im = im.crop(tile)
                img_id_str = str('{:06d}'.format(img_no))
                new_im.save(
                    '{}/{}.{}'.format(self.IMG_DST, img_id_str, file_type))
                new_ids.append(img_id_str)
                img_no += 1
            mapper[file_name] = new_ids

        print('Obtained {} image slices!'.format(img_no-1))
        return mapper

    def slice_bboxes_by_size(self, tile_size, tile_overlap=0.0):
        """Slices each box annotation in the source directory by specified size and overlap.

        Parameters
        ----------
        tile_size : tuple
            Size (width, height) of each tile.
        tile_overlap: float, optional  
            Percentage of tile overlap between two consecutive strides.
            Default value is `0`.

        Returns
        ----------
        None
        """
        validate_tile_size(tile_size)
        validate_overlap(tile_overlap)
        mapper = self.__slice_bboxes(tile_size, tile_overlap, number_tiles=-1)
        if self.save_before_after_map:
            save_before_after_map_csv(mapper, self.ANN_DST)

    def slice_bboxes_by_number(self, number_tiles):
        """Slices each box annotation in source directories into specified number of tiles.

        Parameters
        ----------
        number_tiles : int
            The number of tiles an image needs to be sliced into.

        Returns
        ----------
        None
        """
        validate_number_tiles(number_tiles)
        mapper = self.__slice_bboxes(None, None, number_tiles=number_tiles)
        if self.save_before_after_map:
            save_before_after_map_csv(mapper, self.ANN_DST)

    def __slice_bboxes(self, tile_size, tile_overlap, number_tiles):
        """
        Private Method
        """
        img_no = 1
        mapper = {}

        for xml_file in sorted(glob.glob(self.ANN_SRC + '/*.xml')):
            root, objects = extract_from_xml(xml_file)
            im_w, im_h = int(root.find('size')[0].text), int(
                root.find('size')[1].text)
            im_filename = root.find('filename').text.split('.')[0]
            if '.' in root.find('filename').text:
                im_format = root.find('filename').text.split('.')[-1].lower()
            else:
                im_format = 'jpg'
            if number_tiles > 0:
                n_cols, n_rows = calc_columns_rows(number_tiles)
                tile_w = int(floor(im_w / n_cols))
                tile_h = int(floor(im_h / n_rows))
                tile_size = (tile_w, tile_h)
                tile_overlap = 0.0
            else:
                tile_w, tile_h = tile_size
            tiles = self.get_tiles((im_w, im_h), tile_size, tile_overlap)
            tile_ids = []
            for tile in tiles:
                img_no_str = '{:06d}'.format(img_no)
                voc_writer = Writer(
                    '{}/{}.{}'.format(self.IMG_DST, img_no_str, im_format), tile_w, tile_h)
                for obj in objects:
                    obj_lbl = obj[-4:]
                    points_info = which_points_lie(obj_lbl, tile)

                    if points_info == Points.NONE:
                        continue

                    elif points_info == Points.ALL:         # All points lie inside the tile
                        new_lbl = (obj_lbl[0] - tile[0], obj_lbl[1] - tile[1],
                                   obj_lbl[2] - tile[0], obj_lbl[3] - tile[1])

                    elif not self.keep_partial_labels:            # Ignore partial labels based on configuration
                        continue

                    elif points_info == Points.P1:
                        new_lbl = (obj_lbl[0] - tile[0], obj_lbl[1] - tile[1],
                                   tile_w, tile_h)

                    elif points_info == Points.P2:
                        new_lbl = (0, obj_lbl[1] - tile[1],
                                   obj_lbl[2] - tile[0], tile_h)

                    elif points_info == Points.P3:
                        new_lbl = (obj_lbl[0] - tile[0], 0,
                                   tile_w, obj_lbl[3] - tile[1])

                    elif points_info == Points.P4:
                        new_lbl = (0, 0, obj_lbl[2] - tile[0],
                                   obj_lbl[3] - tile[1])

                    elif points_info == Points.P1_P2:
                        new_lbl = (obj_lbl[0] - tile[0], obj_lbl[1] - tile[1],
                                   obj_lbl[2] - tile[0], tile_h)

                    elif points_info == Points.P1_P3:
                        new_lbl = (obj_lbl[0] - tile[0], obj_lbl[1] - tile[1],
                                   tile_w, obj_lbl[3] - tile[1])

                    elif points_info == Points.P2_P4:
                        new_lbl = (0, obj_lbl[1] - tile[1],
                                   obj_lbl[2] - tile[0], obj_lbl[3] - tile[1])

                    elif points_info == Points.P3_P4:
                        new_lbl = (obj_lbl[0] - tile[0], 0,
                                   obj_lbl[2] - tile[0], obj_lbl[3] - tile[1])

                    voc_writer.addObject(obj[0], new_lbl[0], new_lbl[1], new_lbl[2], new_lbl[3],
                                         obj[1], obj[2], obj[3])
                voc_writer.save('{}/{}.xml'.format(self.ANN_DST, img_no_str))
                tile_ids.append(img_no_str)
                img_no += 1
            mapper[im_filename] = tile_ids

        print('Obtained {} annotation slices!'.format(img_no-1))
        return mapper

    def visualize_random(self, map_dir=None):
        """Picks an image randomly and visualizes unsliced and sliced images using `matplotlib`.


        Parameters:
        ----------
        map_dir : str, optional
            /path/to/mapper/directory.
            By default, looks for `mapper.csv` in image destination folder. 

        Returns:
        ----------
        None
            However, displays the final plots.
        """
        if not self.save_before_after_map and map_dir is None:
            print('No argument passed to `map_dir` and save_before_after_map is set False. \
                Looking for `mapper.csv` in image destination folder.')
        mapping = ''

        if map_dir is None:
            map_path = self.IMG_DST + '/mapper.csv'
        else:
            map_path = map_dir + '/mapper.csv'
        with open(map_path) as src_map:
            read_csv = csv.reader(src_map, delimiter=',')
            # Skip the header
            next(read_csv, None)
            mapping = random.choice(list(read_csv))

            src_file = mapping[0]
            tile_files = mapping[1:]

            plot_image_boxes(self.IMG_SRC, self.ANN_SRC, src_file)
            plot_image_boxes(self.IMG_DST, self.ANN_DST, tile_files)


class Points(Enum):
    """An Enum to hold info of points of a bounding box or a tile.
    Used by the method `which_points_lie` and a private method in `Slicer` class. 
    See `which_points_lie` method for more details.

    Example
    ----------
    A box and its points
    P1- - - - - - -P2
    |               |
    |               |
    |               |
    |               |
    P3- - - - - - -P4
    """

    P1, P2, P3, P4 = 1, 2, 3, 4
    P1_P2 = 5
    P1_P3 = 6
    P2_P4 = 7
    P3_P4 = 8
    ALL, NONE = 9, 10


def which_points_lie(label, tile):
    """Method to check if/which points of a label lie inside/on the tile.

    Parameters
    ----------
    label: tuple
        A tuple with label coordinates in `(xmin, ymin, xmax, ymax)` format.
    tile: tuple
        A tuple with tile coordinates in `(xmin, ymin, xmax, ymax)` format.  

    Note
    ----------
    Ignoring the cases where either all 4 points of the `label` or none of them lie on the `tile`, 
    at most only 2 points can lie on the `tile`. 

    Returns
    ----------
    Point (Enum)
        Specifies which point(s) of the `label` lie on the `tile`.
    """
    # 0,1 -- 2,1
    # |        |
    # 0,3 -- 2,3
    points = [False, False, False, False]

    if (tile[0] <= label[0] and tile[2] >= label[0]):
        if (tile[1] <= label[1] and tile[3] >= label[1]):
            points[0] = True
        if (tile[1] <= label[3] and tile[3] >= label[3]):
            points[2] = True

    if (tile[0] <= label[2] and tile[2] >= label[2]):
        if (tile[1] <= label[1] and tile[3] >= label[1]):
            points[1] = True
        if (tile[1] <= label[3] and tile[3] >= label[3]):
            points[3] = True

    if sum(points) == 0:
        return Points.NONE
    elif sum(points) == 4:
        return Points.ALL

    elif points[0]:
        if points[1]:
            return Points.P1_P2
        elif points[2]:
            return Points.P1_P3
        else:
            return Points.P1

    elif points[1]:
        if points[3]:
            return Points.P2_P4
        else:
            return Points.P2

    elif points[2]:
        if points[3]:
            return Points.P3_P4
        else:
            return Points.P3

    else:
        return Points.P4
