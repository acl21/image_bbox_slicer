'''
Main functionality of ``image_bbox_slicer``.
'''
import os
import csv
import errno
import warnings
import glob
import pickle
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import random
from math import sqrt, ceil, floor
from PIL import Image
from pascal_voc_writer import Writer


class Slicer(object):
    '''
    '''

    def __init__(self):
        self.IMG_SRC = os.getcwd()
        self.IMG_DST = os.path.join(os.getcwd(), 'sliced_images')
        self.ANN_SRC = os.getcwd()
        self.ANN_DST = os.path.join(os.getcwd(), 'sliced_annotations')
        self.IMG_FORMAT_LIST = ['jpg', 'jpeg', 'png', 'tiff', 'exif', 'bmp']

    def config_dirs(self, img_src, ann_src,
                    img_dst=os.path.join(os.getcwd(), 'sliced_images'),
                    ann_dst=os.path.join(os.getcwd(), 'sliced_annotations')):
        validate_dir(img_src)
        validate_dir(ann_src)
        validate_dir(img_dst, src=False)
        validate_dir(ann_dst, src=False)
        self.IMG_SRC = img_src
        self.IMG_DST = img_dst
        self.ANN_SRC = ann_src
        self.ANN_DST = ann_dst

    def get_tiles(self, img_size, tile_size, tile_overlap):
        """
        Returns a list of (xmin, ymin, xmax, ymax) of tiles.

        tile_overlap: Percentage oftile_overlapbetween each tile with its next tile.
        tile_size: (W, H) of tile
        img_size: (W, H) of original images
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

    def slice_by_size(self, tile_size, tile_overlap=0.0, save_old_new_map=True):
        self.slice_images_by_size(tile_size, tile_overlap, save_old_new_map)
        self.slice_bboxes_by_size(tile_size, tile_overlap, save_old_new_map)

    def slice_by_number(self, number_tiles, save_old_new_map=True):
        self.slice_images_by_number(number_tiles, save_old_new_map)
        self.slice_bboxes_by_number(number_tiles, save_old_new_map)

    def slice_images_by_size(self, tile_size, tile_overlap=0.0, save_old_new_map=True):
        '''
        '''
        validate_tile_size(tile_size)
        validate_overlap(tile_overlap)
        mapper = self.__slice_images(tile_size, tile_overlap, number_tiles=-1)
        if save_old_new_map:
            save_old_new_map_csv(mapper, self.IMG_DST)

    def slice_images_by_number(self, number_tiles, save_old_new_map=True):
        '''
        '''
        validate_number_tiles(number_tiles)
        mapper = self.__slice_images(None, None, number_tiles=number_tiles)
        if save_old_new_map:
            save_old_new_map_csv(mapper, self.IMG_DST)

    def __slice_images(self, tile_size, tile_overlap, number_tiles):
        '''
        '''
        old_new_map = {}
        img_no = 1

        for file in sorted(glob.glob(self.IMG_SRC + "/*")):
            file_name = file.split('/')[-1].split('.')[0]
            file_type = file.split('/')[-1].split('.')[-1].lower()
            if file_type.lower() not in self.IMG_FORMAT_LIST:
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
            old_new_map[file_name] = new_ids

        print('\nSaved {} image slices at {} succesfully!'.format(
            img_no-1, self.IMG_DST))
        return old_new_map

    def slice_bboxes_by_size(self, tile_size, tile_overlap=0.0, save_old_new_map=True):
        '''
        '''
        validate_tile_size(tile_size)
        validate_overlap(tile_overlap)
        mapper = self.__slice_bboxes(tile_size, tile_overlap, number_tiles=-1)
        if save_old_new_map:
            save_old_new_map_csv(mapper, self.ANN_DST)

    def slice_bboxes_by_number(self, number_tiles, save_old_new_map=True):
        '''
        '''
        validate_number_tiles(number_tiles)
        mapper = self.__slice_bboxes(None, None, number_tiles=number_tiles)
        if save_old_new_map:
            save_old_new_map_csv(mapper, self.ANN_DST)
    
    def __slice_bboxes(self, tile_size, tile_overlap, number_tiles):
        img_no = 1
        old_new_map = {}
        
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
                    result = is_contained(obj_lbl, tile)
                    side = None
                    if sum(result) == 0:
                        continue

                    elif sum(result) == 2:         # Both points lie inside the tile
                        new_lbl = (obj_lbl[0] - tile[0], obj_lbl[1] - tile[1],
                                   obj_lbl[2] - tile[0], obj_lbl[3] - tile[1])

                    elif result[0] == True:        # Only left-top point lies inside the tile
                        side = which_side(obj_lbl, tile, result)
                        if side == 'Bottom':
                            new_lbl = (
                                obj_lbl[0] - tile[0], obj_lbl[1] - tile[1], obj_lbl[2] - tile[0], tile_h)
                        elif side == 'Right':
                            new_lbl = (
                                obj_lbl[0] - tile[0], obj_lbl[1] - tile[1], tile_w, obj_lbl[3] - tile[1])
                        elif side == 'RightBottom':
                            new_lbl = (obj_lbl[0] - tile[0],
                                       obj_lbl[1] - tile[1], tile_w, tile_h)
                        else:
                            raise Exception('Side should not be {} for when left-top \
                            lies inside tile'.format(side))

                    elif result[1] == True:        # Only right-bottom point lies inside the tile
                        side = which_side(obj_lbl, tile, result)
                        if side == 'Top':
                            new_lbl = (
                                obj_lbl[0] - tile[0], 0, obj_lbl[2] - tile[0], obj_lbl[3] - tile[1])
                        elif side == 'Left':
                            new_lbl = (
                                0, obj_lbl[1] - tile[1], obj_lbl[2] - tile[0], obj_lbl[3] - tile[1])
                        elif side == 'LeftTop':
                            new_lbl = (
                                0, 0, obj_lbl[2] - tile[0], obj_lbl[3] - tile[1])
                        else:
                            raise Exception('Side should not be {} for when right-bottom \
                            lies inside tile'.format(side))
                    voc_writer.addObject(obj[0], new_lbl[0], new_lbl[1], new_lbl[2], new_lbl[3],
                                         obj[1], obj[2], obj[3])
                voc_writer.save('{}/{}.xml'.format(self.ANN_DST, img_no_str))
                tile_ids.append(img_no_str)
                img_no += 1
            old_new_map[im_filename] = tile_ids

        print('\nSaved {} annotations slices at {} succesfully!'.format(
            img_no-1, self.ANN_DST))
        return old_new_map
    
    def visualize_random(self):
        mapping = ''
        with open(self.IMG_DST + '/old_new_map.csv') as src_map:
            read_csv = csv.reader(src_map, delimiter=',')
            mapping = random.choice(list(read_csv))
            
            src_file = mapping[0]
            tile_files = mapping[1:]
            
            plot_image_boxes(self.IMG_SRC, self.ANN_SRC, src_file)
            plot_image_boxes(self.IMG_DST, self.ANN_DST, tile_files)

# Source : Sam Dobson
# https://github.com/samdobson/image_slicer
def calc_columns_rows(n):
    """
    Calculate the number of columns and rows required to divide an image
    into ``n`` parts.
    Return a tuple of integers in the format (num_columns, num_rows)
    """
    num_columns = int(ceil(sqrt(n)))
    num_rows = int(ceil(n / float(num_columns)))
    return (num_columns, num_rows)

# Source : Sam Dobson
# https://github.com/samdobson/image_slicer


def validate_number_tiles(number_tiles):
    if number_tiles is not None:
        TILE_LIMIT = 99 * 99

        try:
            number_tiles = int(number_tiles)
        except:
            raise ValueError('number_tiles could not be cast to integer.')

        if number_tiles > TILE_LIMIT or number_tiles < 2:
            raise ValueError('Number of tiles must be between 2 (inclusive) and {} (you \
                            asked for {}).'.format(TILE_LIMIT, number_tiles))


def validate_dir(dir_path, src=True):
    '''
    '''
    if os.path.isdir(dir_path):
        if not os.listdir(dir_path) and src:
            raise Exception('{} should not be empty'.format(dir_path))
    else:
        warnings.warn(
            '{} directory does not exist so creating it now'.format(dir_path))
        os.makedirs(dir_path, exist_ok=True)


def validate_overlap(tile_overlap):
    '''
    '''
    if not (0.0 <= tile_overlap <= 1.0):
        raise Exception('Tile overlap percentage should be between 0 and 1. \
                        The value provided was {}'.format(tile_overlap))


def validate_tile_size(tile_size, img_size=None):
    if img_size is None:
        if isinstance(tile_size, tuple):
            if len(tile_size) != 2:
                raise Exception('Tile size must be a tuple of size 2 i.e., (w, h). \
                The tuple provided was {}'.format(tile_size))
        else:
            raise Exception('Tile size must be a tuple \
                The argument was of type {}'.format(type(tile_size)))
    else:
        if sum(tile_size) >= sum(img_size):
            raise Exception('Tile size cannot exceed image size. \
            Tile size was {} while image size was {}'.format(tile_size, img_size))


def save_old_new_map_csv(mapper, path):
    with open('{}/old_new_map.csv'.format(path), 'w') as f:
        for key in mapper.keys():
            f.write("%s,%s\n" % (key, ','.join(mapper[key])))
    print('\nSuccessfully saved the mapping between old and new filenames at {}'.format(path))


def extract_from_xml(file):
    '''
    '''
    objects = []
    tree = ET.parse(file)
    root = tree.getroot()
    for member in root.findall('object'):
        value = (member[0].text,
                 member[1].text,
                 member[2].text,
                 member[3].text,
                 int(member[4][0].text),
                 int(member[4][1].text),
                 int(member[4][2].text),
                 int(member[4][3].text)
                 )
        objects.append(value)
    return root, objects


def is_contained(label, tile):
    '''
    Method to check if/which points of the label lie inside a sub image.

    label: (xmin, ymin, xmax, ymax) Bounding box label
    tile: (xmin, ymin, xmax, ymax) Tile coordinates

    Outputs a list.
    result: [LeftTop, RightBottom] - e.g., [True, False] if LeftTop point lies inside the tile
            while RightBottom point lies outside the yile
    '''

    box = tile
    result = [False, False]
    if (box[0] <= label[0] and box[2] >= label[0]) and (box[1] <= label[1] and box[3] >= label[1]):
        result[0] = True
    if (box[0] <= label[2] and box[2] >= label[2]) and (box[1] <= label[3] and box[3] >= label[3]):
        result[1] = True
    return result


def which_side(label, tile, contains_info):
    '''
    Returns the direction in which the label point lies outside the sub image box.

    label: (xmin, ymin, xmax, ymax) Bounding box label
    tile: (xmin, ymin, xmax, ymax) Tile coordinates
    contains_info: Output of is_contained() method

    Outputs a string
    result = 'Left' or 'Right' or 'Top' or 'Bottom' or 'LeftTop' or 'RightBottom'
    '''
    box = tile
    result = ''
    if sum(contains_info) == 0:
        raise Exception('Invalid contains_info parameter. The value of parameter passed was {}. \
                         Seems like both the points lie outside tile'.format(contains_info))
    elif sum(contains_info) == 2:
        raise Exception('Invalid contains_info parameter. The value of parameter passed was {}. \
                         Seems like both the points lie inside tile'.format(contains_info))
    elif contains_info[0] == False:
        idx1 = 0
        idx2 = 1
    else:
        idx1 = 2
        idx2 = 3

    if label[idx1] < box[0]:
        result += 'Left'
    if label[idx1] > box[2]:
        result += 'Right'
    if label[idx2] < box[1]:
        result += 'Top'
    if label[idx2] > box[3]:
        result += 'Bottom'

    return result


def plot_image_boxes(img_path, ann_path, file_name):
    if isinstance(file_name, str): 
        tree = ET.parse(ann_path + '/' + file_name + '.xml')  
        root = tree.getroot()

        im = Image.open(img_path + '/' + file_name + '.jpg')
        im = np.array(im, dtype=np.uint8)

        rois = []
        for member in root.findall('object'):
            rois.append((int(member[4][0].text),int(member[4][1].text),\
                         int(member[4][2].text),int(member[4][3].text)))

        # Create figure and axes
        fig,ax = plt.subplots(1, figsize=(10,10))

        # Display the image
        ax.imshow(im)

        for roi in rois:
            # Create a Rectangle patch
            rect = patches.Rectangle((roi[0],roi[1]),roi[2]-roi[0],roi[3]-roi[1],\
                                     linewidth=3,edgecolor='b',facecolor='none')

            # Add the patch to the Axes
            ax.add_patch(rect)
    else:
        cols, rows = calc_columns_rows(len(file_name))
        pos = []
        for i in range(0, rows):
            for j in range(0, cols):
                pos.append((i,j))
        fig, ax = plt.subplots(rows, cols, sharex='col', sharey='row', figsize=(10,10))
        for idx, file in enumerate(file_name):
            
            tree = ET.parse(ann_path + '/' + file + '.xml')  
            root = tree.getroot()

            im = Image.open(img_path + '/' + file + '.jpg')
            im = np.array(im, dtype=np.uint8)
            
            rois = []
            for member in root.findall('object'):
                rois.append((int(member[4][0].text),int(member[4][1].text),\
                             int(member[4][2].text),int(member[4][3].text)))

            # Display the image at the right position
            ax[pos[idx][0], pos[idx][1]].imshow(im)

            for roi in rois:
                # Create a Rectangle patch
                rect = patches.Rectangle((roi[0],roi[1]),roi[2]-roi[0],roi[3]-roi[1],\
                                         linewidth=3,edgecolor='b',facecolor='none')

                # Add the patch to the Axes
                ax[pos[idx][0], pos[idx][1]].add_patch(rect)
        
    plt.show()



