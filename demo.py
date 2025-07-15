import numpy as np
import pylab as plt

class DataContainer:
    """Container for simulation data."""

    def __init__(
        self,
        resolution: tuple[int, int, int],
        dimensions: tuple[float, float, float],
        dataset_name: str,
        field_list: list[str],
    ) -> None:
        """
        Initialize the data snapshot.

        Parameters:
            resolution: Dimensions (nx, ny, nz).
            dimensions: Physical dimensions (Lx, Ly, Lz).
            dataset_name: Name of the dataset.
            field_list: List of field names in this dataset.
            fields: Collection of snapshot fields
        """
        self.resolution   = resolution
        self.dimensions   = dimensions
        self.dataset_name = dataset_name
        self.field_list   = field_list
        self.fields       = {} 
        self.dxyz         = tuple(a / b for a, b in zip(self.dimensions, self.resolution))


    def get_meshgrid(self) -> None:
        """Generate a 3D meshgrid based on resolution and dimensions."""
        x = np.linspace(0, self.dimensions[0], self.resolution[0]) 
        y = np.linspace(0, self.dimensions[1], self.resolution[1]) 
        z = np.linspace(0, self.dimensions[2], self.resolution[2]) 
        self.xx, self.yy, self.zz = np.meshgrid(x, y, z, indexing='ij')

    def set_field(self, field_name: str, field_array: np.ndarray) -> None:
        """
        Assign a field array to the container.

        Parameters:
            field_name: Name of the field.
            field_array: Data array for the field.
        """
        self.fields[field_name] = field_array

def keplerian_rotation(
    data: DataContainer,
    location: tuple[float, float, float],
    inner_r: float,
    max_omega: float
) -> np.ndarray:
    """
    Compute a 3D Keplerian rotation velocity field in the XY-plane,
    centered at a given location. Angular velocity follows omega ∝ r^(-3/2),
    capped at max_omega for small radii.

    Parameters:
        data: DataContainer with xx, yy, zz meshgrid attributes.
        location: Tuple (x, y, z) specifying the rotation center.
        inner_r: Radius below which solid-body rotation is assumed.
        max_omega: Angular velocity at inner radius (used as cap).

    Returns:
        A 4D NumPy array of shape (nx, ny, nz, 3), where the last dimension
        represents the velocity vector components (vx, vy, vz).
    """

    # Compute radius from the center
    dx = data.xx - location[0]
    dy = data.yy - location[1]
    radius_xy = np.sqrt(dx**2 + dy**2)

    with np.errstate(divide='ignore', invalid='ignore'):
        omega   = max_omega * (inner_r/radius_xy)**(3/2)
        omega[radius_xy <= inner_r] = max_omega

    v_azimuth = radius_xy * omega
    phi       = np.atan2(dy, dx) 

    v_x       = -v_azimuth*np.sin(phi)
    v_y       =  v_azimuth*np.cos(phi)

    velocity = np.zeros((*data.resolution, 3), dtype=np.float64)
    velocity[:,:,:,0] = v_x
    velocity[:,:,:,1] = v_y
    #velocity[:,:,:,2] is zero (no z-component)

    return velocity


def r2_density(
    data: DataContainer,
    location: tuple[float, float, float],
    inner_r: float,
    max_density: float
) -> np.ndarray:

    """
    Compute an inverse-square density profile centered at a given location.
    Density is capped at max_density within the inner radius.

    Parameters:
        data: DataContainer with xx, yy, zz attributes.
        location: Center of the profile (x, y, z).
        inner_r: Radius below which density is constant.
        max_density: Maximum density value.

    Returns:
        3D NumPy array of density values.
    """

    # Compute radius from the center
    dx = data.xx - location[0]
    dy = data.yy - location[1]
    dz = data.zz - location[2]
    radius = np.sqrt(dx**2 + dy**2 + dz**2)

    # Avoid division by zero
    with np.errstate(divide='ignore', invalid='ignore'):
        #TODO: Needs to be scaled correctly. 
        density = max_density * ((inner_r**2) / (radius**2))
        density[radius <= inner_r] = max_density

    return density

def make_contourmap(data: DataContainer, levels: int = 20, quiver_step: int = 10) -> None:
    """Generate and save a contour map of the density field with velocity vectors.

    Parameters
    ----------
    data : DataContainer
        Data container holding simulation grid, dimensions, and field values.
    levels : int, optional
        Number of contour levels for the density field. Default is 20.
    quiver_step : int, optional
        Step size for subsampling the grid for velocity arrows.
        Larger values = fewer arrows. Default is 10.
    """
    # Extract dimensions for aspect ratio
    lx = data.dimensions[0]
    ly = data.dimensions[1]
    aspect_ratio = ly / lx

    # --- Extract fields ---
    # Density field on the first z-plane
    rho = data.fields['density'][:, :, 0]

    # Velocity components on the same plane
    vx = data.fields['velocity3'][:, :, 0, 0]
    vy = data.fields['velocity3'][:, :, 0, 1]

    # Velocity magnitude for debugging or optional plotting
    vmag = np.sqrt(vx ** 2 + vy ** 2)

    # Grid coordinates 
    X = data.xx[:, :, 0]
    Y = data.yy[:, :, 0]

    # --- Set figure size ---
    # Width is arbitrary; height is scaled with aspect ratio
    width = 10
    height = width * aspect_ratio
    plt.figure(figsize=(width, height))

    # --- Filled contour plot for density ---
    contour_density = plt.contourf(
        X,
        Y,
        rho,
        levels=levels,
        cmap='viridis'
    )

    # ---- Arrow (quiver) plot ----
    # Subsample grid to avoid too many arrows
    Xq = X[::quiver_step, ::quiver_step]
    Yq = Y[::quiver_step, ::quiver_step]
    VXq = vx[::quiver_step, ::quiver_step]
    VYq = vy[::quiver_step, ::quiver_step]

    plt.quiver(
        Xq, Yq, VXq, VYq,
        color="white",   # arrows in white for contrast
        scale=1,         # adjust for vector scaling
        width=0.004,     # thinner arrows
        angles="xy",
        pivot="mid" 
    )

    # Set equal aspect ratio
    plt.gca().set_aspect('equal')
    
    plt.xlabel("x")
    plt.ylabel("y")
    cbar = plt.colorbar(contour_density, orientation='horizontal', pad=0.1)
    cbar.set_label("Density")

    plt.savefig("test.svg", format='svg', bbox_inches='tight')
    plt.close()


def main() -> None:
    """Main execution function for the demo."""
    print("This shows a simple visualization demo with the created tools.")

    # Create a sample model in a Cartesian grid
    demo_data = DataContainer(
        resolution=(512, 512, 1),
        dimensions=(1.0, 1.0, 0.0),
        dataset_name="radial_profile",
        field_list=["density", "velocity3"]
    )

    demo_data.get_meshgrid()

    print("Initializing density...")
    demo_data.set_field("density", r2_density(demo_data, (0.5, 0.5, 0.5), 0.01, 1.0))
    print("Initializing velocity...")
    #TODO: Include also free fall speed componet. 
    demo_data.set_field("velocity3", keplerian_rotation(demo_data, (0.5, 0.5, 0,5), 0.01, 1.0))

    print("Plotting...")
    make_contourmap(demo_data, 20)

    print("DONE")

if __name__ == "__main__":
    main()








