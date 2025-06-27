import cadquery as cq

def create_solar_array(panel_length, panel_width, panel_thickness, yoke_length, yoke_diameter):
    """
    Creates a single solar array assembly.

    :param panel_length: The length of the solar panel.
    :param panel_width: The width of the solar panel.
    :param panel_thickness: The thickness of the solar panel.
    :param yoke_length: The length of the attachment yoke.
    :param yoke_diameter: The diameter of the attachment yoke.
    :return: A CadQuery Assembly object.
    """
    panel = cq.Workplane("XY").box(panel_length, panel_width, panel_thickness)
    yoke = cq.Workplane("XY").workplane(offset=-yoke_length/2).circle(yoke_diameter/2).extrude(yoke_length)

    # Use an assembly to position the parts relative to each other
    assy = cq.Assembly()
    assy.add(panel, name="panel", loc=cq.Location(cq.Vector(yoke_length/2 + panel_length/2, 0, 0)))
    assy.add(yoke, name="yoke")

    return assy