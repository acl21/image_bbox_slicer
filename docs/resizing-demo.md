## Create And Configure `Resizer` Object
_Note: This usage demo can be found in `Resizing_Demo.ipynb` in the project's [repo](https://github.com/acl21/image_bbox_slicer)._

### Setting Paths To Source And Destination Directories
You must configure paths to source and destination directories like the following. 
By default it takes the current working directory as the source folder for both images and annotations and also creates new folders:

* `/resized_images` and 
* `/resized_annotation` 

in the current working directory.

```python
import image_bbox_slicer as ibs

im_src = './src/images'
an_src = './src/annotations'
im_dst = './dst/images'
an_dst = './dst/annotations'

resizer = ibs.Resizer()
resizer.config_dirs(img_src=im_src, ann_src=an_src, 
                   img_dst=im_dst, ann_dst=an_dst)
```

### Images and Bounding Box Annotations Simultaneously

** By Specific Size ** 


```python
resizer.resize_by_size(new_size=(500,200))
resizer.visualize_resized_random()
```


![png](img/output_18_0.png)


![png](img/output_18_1.png)


** By A Resize Factor **


```python
resizer.resize_by_factor(resize_factor=0.05)
resizer.visualize_resized_random()
```

![png](img/output_20_0.png)


![png](img/output_20_1.png)

_Note:_ 
*`visualize_resized_random()` randomly picks a recently resized image from the destination directory for plotting.*


