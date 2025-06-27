import cadquery as cq
import os
import sys
from spacecraft_parts.bus import create_bus
from spacecraft_parts.solar_array import create_solar_array
from OCP.BRepCheck import BRepCheck_Analyzer

# --- Spacecraft Parameters ---
# By changing these values, you can generate a completely different design.
bus_params = {
    "width": 1.0, "depth": 1.0, "height": 1.5, "wall_thickness": 0.05
}

solar_array_params = {
    "panel_length": 2.0, "panel_width": 1.0, "panel_thickness": 0.02,
    "yoke_length": 0.2, "yoke_diameter": 0.1
}

def add_details(bus_solid):
    """
    Adds some computationally intensive details to the bus.
    This function is a good candidate for profiling as it contains operations
    that are known to be performance-intensive in CAD modeling.

    :param bus_solid: The solid to add details to.
    :return: The modified solid with details added.
    """
    # Add a pattern of small holes. Loops with many boolean operations can be slow.
    hole_radius = 0.02
    for x_ratio in [-0.4, -0.2, 0.2, 0.4]:
        for z_ratio in [-0.8, -0.6, -0.4, -0.2, 0.2, 0.4, 0.6, 0.8]:
            bus_solid = bus_solid.cut(
                cq.Solid.makeCylinder(
                    hole_radius, bus_params["depth"] * 2,
                    pnt=cq.Vector(bus_params["width"] / 2 * x_ratio, 0, bus_params["height"] / 2 * z_ratio),
                    dir=cq.Vector(0, 1, 0)
                )
            )

    # Add some fillets. Filleting is often a major performance bottleneck.
    bus_solid = bus_solid.edges("|Z").fillet(0.02)

    return bus_solid

def create_antenna():
    """
    Creates a helical antenna. Sweeping profiles along complex paths is
    another classic performance-intensive CAD operation.
    """
    print("INFO: Creating helical antenna...")
    pitch = 0.4
    height = 1.2
    radius = 0.3
    wire_radius = 0.02

    # Create the helical path and sweep a circular profile along it
    path = cq.Wire.makeHelix(pitch=pitch, height=height, radius=radius)
    profile = cq.Workplane(cq.Plane(origin=path.startPoint(), normal=path.tangentAt(0))).circle(wire_radius)
    antenna_wire = profile.sweep(cq.Workplane(path), makeSolid=True)

    # Add a small base for the antenna
    base = cq.Workplane("XY").cylinder(height=0.1, radius=radius * 1.2)
    antenna = antenna_wire.union(base)

    return antenna.val()

def assemble_spacecraft(bus_parameters, solar_array_parameters):
    """
    Creates and assembles the spacecraft components.
    """
    # 1. Create the individual components
    bus = create_bus(**bus_parameters)
    solar_array = create_solar_array(**solar_array_parameters)
    antenna = create_antenna()

    # 2. Add some performance-intensive details to make profiling more interesting
    print("INFO: Adding complex details to the bus...")
    bus = add_details(bus)

    # 3. Create the final assembly object
    spacecraft_assy = cq.Assembly()

    # 4. Add the bus at the origin
    spacecraft_assy.add(bus, name="bus")

    # 5. Add the solar arrays, positioning them relative to the bus
    spacecraft_assy.add(solar_array, name="solar_array_right", loc=cq.Location(cq.Vector(0, bus_parameters["width"]/2, 0), cq.Vector(0,0,1), 90))
    spacecraft_assy.add(solar_array, name="solar_array_left", loc=cq.Location(cq.Vector(0, -bus_parameters["width"]/2, 0), cq.Vector(0,0,1), -90))

    # 6. Add the antenna on top of the bus
    antenna_pos = cq.Vector(0, 0, bus_parameters["height"] / 2)
    spacecraft_assy.add(antenna, name="antenna", loc=cq.Location(antenna_pos))

    return spacecraft_assy

def intensive_vector_math():
    """
    Performs a large number of vector operations to make geom.py
    more visible in the profiler. This doesn't create any CAD geometry,
    it just consumes CPU time doing math.
    """
    print("INFO: Performing intensive vector math for profiling demonstration...")
    v = cq.Vector(1, 2, 3)
    # A loop with a million iterations will be slow enough to see clearly.
    for i in range(1000000):
        v = v.add(cq.Vector(i * 1e-7, i * 1e-7, i * 1e-7))
        v = v.normalized()
    print("INFO: Vector math complete.")
    return v

if __name__ == "__main__":
    spacecraft_assembly = assemble_spacecraft(bus_params, solar_array_params)
    intensive_vector_math()
    # Get the directory of the current script and create an output directory there
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, "output")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "spacecraft.step")

    try:
        # Convert the assembly to a single compound solid for exporting
        print("INFO: Creating compound solid from assembly...")
        result = spacecraft_assembly.toCompound()
        print(f"INFO: Result is a {type(result)}.")

        # Diagnostic: Check if the resulting solid is valid before exporting.
        analyzer = BRepCheck_Analyzer(result.wrapped)
        if not analyzer.IsValid():
            raise ValueError("The generated 3D model is not valid. Check for self-intersections or other geometry errors.")
        print("INFO: The generated model is a valid solid.")

        print(f"INFO: Attempting to export to: {output_path}")
        cq.exporters.export(result, output_path)

        # Verification step to combat silent failures.
        if not os.path.exists(output_path):
            raise IOError("Export function completed without error, but the file was not created.")
        print(f"SUCCESS: Model exported to {output_path}")
    except Exception as e:
        # Print errors to stderr and exit with a non-zero code to signal failure.
        print(f"ERROR: Failed to export model. Reason: {e}", file=sys.stderr)
        sys.exit(1)
