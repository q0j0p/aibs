import os
import src

class Expt(object):
    """Parent class to set up a data science experiment"""
    def __init__(self, expt_title):
        self.data_path, self.results_path = self.setup_expt(expt_title)

    def setup_expt(self, expt_title):
        """Sets up data and results directories for this expt"""
        results_path = os.path.join(src.PROJECT_ROOT,"results",expt_title)
        data_path = os.path.join(src.PROJECT_ROOT,"data",expt_title)
        pathlist = [data_path, results_path]
        for path in pathlist:
            if os.path.exists(path):
                print(f"{path} already exists")
            else:
                os.mkdir(path)
                print(f"{path} created")
        return pathlist
