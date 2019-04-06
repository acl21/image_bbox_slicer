# image_bbox_slicer [![](https://img.shields.io/github/license/mashape/apistatus.svg)](LICENSE)

This easy-to-use library splits images and its bounding box annotations into tiles, both into specific sizes and into any arbitrary number of equal parts.

<div align="center">
<img src="imgs/ibs_demo.jpg" alt="Partial Labels Example" style="width: 500px;" />
</div>

## Installation
```python
$ pip install image_bbox_slicer
```

_Requirements:_
```python
Pillow==5.4.1
numpy==1.16.2
pascal-voc-writer==0.1.4
matplotlib==3.0.3
```

## Usage - A Quick Demo
_Note: This usage demo can be found in `demo.ipynb` in the repo._

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
slicer.visualize_random()
```

<div align="center">
<img src="imgs/output_10_1.png" alt="Output1" style="width: 200px;" />

<img src="imgs/output_10_2.png" alt="Output2" style="width: 200px;" />
</div>


#### By Specific Size

```python
slicer.slice_by_size(tile_size=(418,279), tile_overlap=0)
slicer.visualize_random()
```


<div align="center">
<img src="imgs/output_12_1.png" alt="Output3" style="width: 200px;" />

<img src="imgs/output_12_2.png" alt="Output4" style="width: 200px;" />
</div>

*Note: `visualize_random()` randomly picks a recently sliced image from the directory for plotting.*

### Other Slicing Functions

#### Slicing Only Images

#### By Number Of Tiles
`slicer.slice_images_by_number(number_tiles=4)`

#### By Specific Size
`slicer.slice_images_by_size(tile_size=(418,279), tile_overlap=0)`

#### Slicing Only Bounding Box Annotations
#### By Number Of Tiles
`slicer.slice_bboxes_by_number(number_tiles=4)`

#### By Specifc Size
`slicer.slice_bboxes_by_size(tile_size=(418,279), tile_overlap=0)`
