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

def assemble_spacecraft(bus_parameters, solar_array_parameters):
    """
    Creates and assembles the spacecraft components.
    """
    # 1. Create the individual components
    bus = create_bus(**bus_parameters)
    solar_array = create_solar_array(**solar_array_parameters)

    # 2. Create the final assembly object
    spacecraft_assy = cq.Assembly()

    # 3. Add the bus at the origin
    spacecraft_assy.add(bus, name="bus")

    # 4. Add the solar arrays, positioning them relative to the bus
    spacecraft_assy.add(solar_array, name="solar_array_right", loc=cq.Location(cq.Vector(0, bus_parameters["width"]/2, 0), cq.Vector(0,0,1), 90))
    spacecraft_assy.add(solar_array, name="solar_array_left", loc=cq.Location(cq.Vector(0, -bus_parameters["width"]/2, 0), cq.Vector(0,0,1), -90))
    
    return spacecraft_assy

if __name__ == "__main__":
    spacecraft_assembly = assemble_spacecraft(bus_params, solar_array_params)

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
