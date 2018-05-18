This repository represents a project that attempts to classify neurons based on their morphological characteristics.  

## Project description
The neurons that make up our complex brains are intricately shaped and organized, and an understanding of cell type composition is necessary to understand how neurons confer the amazing functions of the brain.  The morphological, physiological, and transcriptomic characteristics of a cell, along with its connectivity, are the main features that shape function.  

Even with the latest technologies, single cell neuronal experiments are painstaking and manually labor intensive, but by aggregating all available data, we may now be able to make use of data science tools to gain further understanding of the cell types.  

This personal project attempts to shape this neuroscientific endeavor into a data science project, using relevant tools in the Python ecosystem.  As a first step, it makes use of >20k 3D reconstruction data available for the fruitfly and implements the persistence barcoding algorithm to represent the morphology of the neurons.  


### Data sources
- [neuromorpho.org](http://neuromorpho.org/byspecies.jsp)
  - This is a .jsp site that requires scraping to obtain zipped files of the .swc data
  - Derived morphometry and other metadata are available by REST API.  

zip files of .swc files were stored in an AWS s3 bucket, and metadata stored in a mongoDB database.  


### [Hierarchical clustering of persistence images](https://github.com/q0j0p/aibs/blob/master/notes/Hierarchical%20clustering.ipynb)
