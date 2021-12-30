## Slicing Images and Bounding Box Annotations Separately

### Only Images (Configure Only Image Src and Dst Directories)

```python
import image_bbox_slicer as ibs

im_src = '../../Datasets/voc2007/JPEGImages//'
im_dst = './dst/images'

slicer = ibs.Slicer()
slicer.config_image_dirs(img_src=im_src, img_dst=im_dst)
```

* ### By Number Of Tiles
```python
slicer.slice_images_by_number(number_tiles=4)
```

* ### By Specific Size 
```python
slicer.slice_images_by_size(tile_size=(418,279), tile_overlap=0)
```


###  Only Bounding Box Annotations (Configure Only Annotation Src and Dst Directories)

```python
import image_bbox_slicer as ibs

an_src = '../../Datasets/voc2007/Annotations/'
an_dst = './dst/annotations'

slicer = ibs.Slicer()
slicer.config_ann_dirs(ann_src=an_src, ann_dst=an_dst)
```
* ### By Number Of Tiles
```python
slicer.slice_bboxes_by_number(number_tiles=4)
```

* ### By Specifc Size
```python
slicer.slice_bboxes_by_size(tile_size=(418,279), tile_overlap=0)
```

---

## Resizing Images and Bounding Box Annotations Separately

### Only Images (Configure Only Image Src and Dst Directories)

```python
import image_bbox_slicer as ibs

im_src = '../../Datasets/voc2007/JPEGImages//'
im_dst = './dst/images'

resizer = ibs.Resizer()
resizer.config_image_dirs(img_src=im_src, img_dst=im_dst)
```

* ### By Specific Size
```python
resizer.resize_images_by_size(new_size=(500,200))
```

* ### By Resize Factor
```python
resizer.resize_images_by_factor(resize_factor=0.05)
```

###  Only Bounding Box Annotations (Configure Only Annotation Src and Dst Directories)

```python
import image_bbox_slicer as ibs

an_src = '../../Datasets/voc2007/Annotations/'
an_dst = './dst/annotations'

resizer = ibs.Resizer()
resizer.config_ann_dirs(ann_src=an_src, ann_dst=an_dst)
```

* ### By Specific Size
```python
resizer.resize_bboxes_by_size(new_size=(500,200))
```

* ### By Resize Factor
```python
resizer.resize_bboxes_by_factor(resize_factor=0.05)
```
