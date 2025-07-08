import numpy as np
import pylab as plt

class DataContainer:
    """Container for simulation data."""

    def __init__(self, resolution, dimensions, dataset_name, field_list):
        """
        Initialize the data snapshot.

        Parameters:
            resolution (tuple, int): Dimensions (nx, ny, nz).
            dimensions (tuple, float): Set dimensions with respect to length (Lx, Ly, Lz).
            dataset_name (str): Name of the dataset.
            field_list (list): List of fields in this dataset.
            fields (dict): Collection of snapshot fields
        """
        self.resolution   = resolution
        self.dataset_name = dataset_name
        self.field_list   = field_list
        self.fields       = {} 
        self.dimensions   = dimensions
        self.dxyz         = tuple(a / b for a, b in zip(self.dimensions, self.resolution))

    def get_meshgrid(self):
        # Define coordinate axes
        x = np.linspace(0, self.dimensions[0], self.resolution[0]) 
        y = np.linspace(0, self.dimensions[1], self.resolution[1]) 
        z = np.linspace(0, self.dimensions[2], self.resolution[2]) 
       
        # Create 3D meshgrid
        self.xx, self.yy, self.zz = np.meshgrid(x, y, z, indexing='ij')
        

    def set_field(self, field_name, field_array):
        """
        Assign a field array to the container.

        Parameters:
            field_name (str): Name of the field.
            field_array (np.ndarray): Data array for the field.
        """
        self.fields[field_name] = field_array

def r2_density(MyData, location, inner_r, max_density):
    """
    Computes an inverse-square density profile centered at a given location.
    The density is capped at max_density for radii less than or equal to inner_r.

    Parameters:
    - MyData: an object with attributes xx, yy, zz (3D numpy arrays of coordinates)
    - location: tuple or array-like of shape (3,) for the center (x, y, z)
    - inner_r: scalar radius below which density is capped
    - max_density: scalar, maximum density value at the center

    Returns:
    - density: 3D numpy array of the same shape as MyData.xx
    """

    # Compute radius from the center
    dx = MyData.xx - location[0]
    dy = MyData.yy - location[1]
    dz = MyData.zz - location[2]
    radius = np.sqrt(dx**2 + dy**2 + dz**2)

    # Avoid division by zero
    with np.errstate(divide='ignore', invalid='ignore'):
        #TODO: Needs to be scaled correctly. 
        density = max_density / (radius**2)
        density[radius <= inner_r] = max_density

    return density

###
###
###

def main():
    print("This shows a simple visualization demo with the created tools.")

    # Create a sample model in a Cartesian grid
    demo_data = DataContainer(
        resolution=(512, 512, 1),
        dimensions=(1.0,1.0,0.0),
        dataset_name="radial_profile",
        field_list=["density", "velocity3"]
    )

    demo_data.get_meshgrid()

    #demo_data.set_field("density", np.zeros(demo_data.resolution))
    demo_data.set_field("density", r2_density(demo_data, (0.5, 0.5, 0.5), 0.01, 1.0))

    # Display its contour map (placeholder – actual plotting logic not yet implemented)

    print("DONE")

if __name__ == "__main__":
    main()








