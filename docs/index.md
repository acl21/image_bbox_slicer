# Image and Bounding Box Slicer-Resizer

This easy-to-use library is a data transformer sometimes useful in Object Detection and Segmentation tasks. With only a few lines of code, one can slice images and their bounding box annotations into smaller tiles, both into specific sizes and into any arbitrary number of equal parts. The tool also supports resizing of images and their bounding box annotations, both by specific sizes and by a resizing/scaling factor. Click `Next` to see a quick demo. 

<div align="center">
<img src="img/ibs_demo.jpg" alt="Overview"  width="650" height="1200"/>
</div>
<br>
Currently, this library only supports bounding box annotations in [PASCAL VOC](http://host.robots.ox.ac.uk/pascal/VOC/) format. And as of now, there is **no command line execution support**.

## Installation
```python
pip install image_bbox_slicer
```

This tool was tested on both Windows and Linx. Works well with Python 3.4 and higher versions and requires. 
```
Pillow
numpy
pascal-voc-writer
matplotlib
```
