[![PyPI version](https://badge.fury.io/py/image-bbox-slicer.svg)](https://badge.fury.io/py/image-bbox-slicer) [![](https://img.shields.io/github/license/mashape/apistatus.svg)](LICENSE)
# image_bbox_slicer 

This easy-to-use library splits images and its bounding box annotations into tiles, both into specific sizes and into any arbitrary number of equal parts. Read the docs [here](https://image-bbox-slicer.readthedocs.io/en/latest/).

Currently, this library only supports bounding box annotations in [PASCAL VOC](http://host.robots.ox.ac.uk/pascal/VOC/) format. And as of now, there is **no command line execution support**. 

## Installation
```python
$ pip install image_bbox_slicer
```

Works with Python 3.4 and higher versions and requires:
```python
Pillow==5.4.1
numpy==1.16.2
pascal-voc-writer==0.1.4
matplotlib==3.0.3
```

## A Quick Demo

```python
import image_bbox_slicer as ibs
```

### Create And Configure `Slicer` Object

#### Setting Paths To Source And Destination Directories.
You must configure paths to source and destination directories like the following. 

```python
im_src = './src/images'
an_src = './src/annotations'
im_dst = './dst/images'
an_dst = './dst/annotations'

slicer = ibs.Slicer()
slicer.config_dirs(img_src=im_src, ann_src=an_src, 
                   img_dst=im_dst, ann_dst=an_dst)
```

#### Dealing With Partial Labels
<div align="center">
<img src="imgs/partial_labels.jpg" alt="Partial Labels Example" style="width: 850px;" />
</div>

The above images show the difference in slicing with and without partial labels. In the image on the left, all the box annotations masked in <span style="color:green">**green**</span> are called Partial Labels. Configure your slicer to either ignore or consider them by setting `Slicer` object's `keep_partial_labels` instance variable to `True` or `False` respectively. By default it is set to `False`.


```python
slicer.keep_partial_labels = True
```

#### Before-After Mapping

You can choose to store the mapping between file names of the images before and after slicing by setting the `Slicer` object's `save_before_after_map` instance variable to `True`. By default it is set to `False`.

Typically, `mapper.csv` looks like the following:
```
| old_name   | new_names                       |
|------------|---------------------------------|
| 2102       | 000001, 000002, 000003, 000004  |
| 3931       | 000005, 000005, 000007, 000008  |
| test_image | 000009, 000010, 000011, 000012  |
| ...        | ...                             |
```


```python
slicer.save_before_after_map = True
```

### Slicing

#### Images and Bounding Box Annotations Simultaneously

#### By Number Of Tiles


```python
slicer.slice_by_number(number_tiles=4)
```

#### By Specific Size

```python
slicer.slice_by_size(tile_size=(418,279), tile_overlap=0)
```

### Other Slicing Functions

#### Slicing Only Images

#### By Number Of Tiles
```python
slicer.slice_images_by_number(number_tiles=4)
```

#### By Specific Size
```python
slicer.slice_images_by_size(tile_size=(418,279), tile_overlap=0)
```

#### Slicing Only Bounding Box Annotations
#### By Number Of Tiles
```python
slicer.slice_bboxes_by_number(number_tiles=4)
```

#### By Specifc Size
```python
slicer.slice_bboxes_by_size(tile_size=(418,279), tile_overlap=0)
```