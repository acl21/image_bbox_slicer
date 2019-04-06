from distutils.core import setup
setup(
  name = 'image_bbox_slicer',
  packages = ['image_bbox_slicer'],   
  version = '0.1.2',      
  license='MIT',        
  long_description = open('docs/DESC.md').read() + '\n\n' + open('HISTORY.md').read(),   
  author = 'AKSHAY CHANDRA LAGANDULA',
  author_email = 'akshaychandra111@gmail.com',
  url = 'https://github.com/akshaychandra21/image_bbox_slicer/',
  download_url = 'https://github.com/akshaychandra21/image_bbox_slicer/archive/v0.1.2.tar.gz',
  keywords = ['IMAGE SLICER', 'BOUNDING BOX SLICER', 'SLICER', 'PASCAL VOC SLICER', 'OBJECT DETECTION'],  
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
    'Programming Language :: Python :: 3',      
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
  ],
)
