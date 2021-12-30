[![PyPI version](https://badge.fury.io/py/image-bbox-slicer.svg)](https://badge.fury.io/py/image-bbox-slicer) [![](https://img.shields.io/github/license/mashape/apistatus.svg)](LICENSE)
# Image and Bounding Box Slicer-Resizer (image_bbox_slicer)

This easy-to-use library is a data transformer sometimes useful in Object Detection tasks. It splits images and their bounding box annotations into tiles, both into specific sizes and into any arbitrary number of equal parts. It can also resize them, both by specific sizes and by a resizing/scaling factor. Of course it goes without saying that just image slicing could in Segmentation tasks (where input and labels both are images). Read the docs [here](https://image-bbox-slicer.readthedocs.io/en/latest/).

<div align="center">
<img src="imgs/ibs_demo2.jpg" alt="Partial Labels Example" />
</div>

Currently, this library only supports bounding box annotations in [PASCAL VOC](http://host.robots.ox.ac.uk/pascal/VOC/) format. And as of now, there is **no command line execution support**. Please raise an issue if needed. 

## Installation
```python
$ pip install image_bbox_slicer
```

This tool was tested on both Windows and Linx. Works well with Python 3.8. 
```python
Pillow
numpy
pascal-voc-writer
matplotlib
```

## Slicing Demo: [Docs](https://image-bbox-slicer.readthedocs.io/en/latest/slicing-demo.html) and [Notebook](https://github.com/acl21/image_bbox_slicer/blob/master/Slicing_Demo.ipynb)

## Resizing Demo: [Docs](https://image-bbox-slicer.readthedocs.io/en/latest/resizing-demo.html) and [Notebook](https://github.com/acl21/image_bbox_slicer/blob/master/Resizing_Demo.ipynb) 