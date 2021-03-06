## Project description
The neurons that make up our complex brains are intricately shaped and organized, and we need to make sense of the various cell types involved to begin to understand how neurons confer the amazing functions of the brain.  The morphological, physiological, and transcriptomic characteristics of a cell, along with its connectivity, are the main features that shape function.  

Even with the latest technologies, single cell neuronal experiments are painstaking and manually labor intensive, but by aggregating all available data, we may now be able to make use of data science tools to gain further understanding of the cell types.  

This personal project attempts to shape this neuroscientific endeavor into a data science project, using relevant tools in the Python ecosystem.  As a first step, it makes use of >20k 3D reconstruction data available for the fruitfly and implements the persistence barcoding algorithm to represent the morphology of the neurons.  


## Data sources
- [neuromorpho.org](http://neuromorpho.org/byspecies.jsp)
    - This is a .jsp site that requires scraping to obtain zipped files of the .swc data
    - Derived morphometry and other metadata are available by REST API.  

zip files of .swc files were stored in an AWS s3 bucket, and metadata stored in a mongoDB database.  

## Data cleaning and EDA  
- <https://github.com/q0j0p/aibs/blob/master/docs/Data_cleaning.ipynb>
- <https://github.com/q0j0p/aibs/blob/master/docs/Data_labels.ipynb>


## Data Analysis
### [Persistence images of sample data](https://github.com/q0j0p/aibs/blob/master/docs/4%20Persistence%20images%20of%20Bacci%20data.ipynb)
### [Hierarchical clustering of neurons based on persistence images](https://github.com/q0j0p/aibs/blob/master/docs/Kenyon_cells.ipynb)

### Basic modeling with classifiers
- <https://github.com/q0j0p/aibs/blob/master/docs/Modeling.ipynb>
