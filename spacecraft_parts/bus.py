import cadquery as cq

def create_bus(width, depth, height, wall_thickness):
    """
    Creates the main spacecraft bus.

    :param width: The width of the bus (Y direction).
    :param depth: The depth of the bus (X direction).
    :param height: The height of the bus (Z direction).
    :param wall_thickness: The thickness of the bus walls.
    :return: A CadQuery Workplane object representing the bus.
    """
    # Create a solid box
    bus_solid = cq.Workplane("XY").box(depth, width, height)

    # Hollow it out
    bus_hollow = bus_solid.faces(">Z").shell(-wall_thickness)

    return bus_hollow