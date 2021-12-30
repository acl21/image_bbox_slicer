from distutils.core import setup
setup(
  name='image_bbox_slicer',
  packages=['image_bbox_slicer'],
  version='0.3',
  license='MIT',
  long_description='This easy-to-use library is a data transformer useful in Object Detection and Segmentation tasks. \
    It splits images and their bounding box annotations into tiles, both into specific sizes and into any \
      arbitrary number of equal parts. It can also resize them, both by specific sizes and by a \
        resizing/scaling factor. \n\nRead the docs at https://image-bbox-slicer.readthedocs.io/en/latest/.',
  author='Akshay L Chandra',
  author_email='research@akshaychandra.com',
  url='https://github.com/acl21/image_bbox_slicer/',
  download_url='https://github.com/acl21/image_bbox_slicer/archive/refs/tags/v0.3.tar.gz',
  keywords=['Image Slicer', 'Bounding Box Annotations Slicer', 'Slicer', 'PASCAL VOC Slicer', 'Object Detection',
            'Resize Images', 'Resize Bounding Box Annotations'],
  install_requires=[
    'Pillow',
    'numpy',
    'matplotlib',
    'pascal-voc-writer'
    ],
  classifiers=[
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.8',
  ],
)
