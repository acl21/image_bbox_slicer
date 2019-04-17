## Slicing Only Images

**  By Number Of Tiles ** 
```python
slicer.slice_images_by_number(number_tiles=4)
```

**  By Specific Size ** 
```python
slicer.slice_images_by_size(tile_size=(418,279), tile_overlap=0)
```

## Slicing Only Bounding Box Annotations
** By Number Of Tiles **
```python
slicer.slice_bboxes_by_number(number_tiles=4)
```

**  By Specifc Size ** 
```python
slicer.slice_bboxes_by_size(tile_size=(418,279), tile_overlap=0)
```

## Resizing Only Images

** By Specific Size **

```python
slicer.resize_images_by_size(new_size=(500,200))
```

** By Resize Factor **

```python
slicer.resize_images_by_factor(resize_factor=0.05)
```

## Resizing Only Bounding Box Annotations

** By Specific Size **

```python
slicer.resize_bboxes_by_size(new_size=(500,200))
```

** By Resize Factor **

```python
slicer.resize_bboxes_by_factor(resize_factor=0.05)
```
