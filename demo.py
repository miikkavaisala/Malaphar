import numpy as np
import pylab as plt

class DataContainer:
    """Container for simulation data"""

    def __init__(self, resolution, data_set_name, field_list):
        """Set the basic parameters of the data snapshot."""
        self.resolution    = resolution    # Tuple (nx, ny, nz) 
        self.data_set_name = data_set_name # name of the dataset
        self.field_list    = field_list    # List of fields in this dataset

print("This shows a simple visualizarion demo with the created tools")

# Create a sample model in cartesian grid

DemoData = DataContainer([512, 512, 512], "radial_profile", ["density", "velocity3"])

# Display its contour map 
