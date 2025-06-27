# Parametric Spacecraft Modeler

This project contains a Python script for generating a 3D model of a spacecraft using the [CadQuery](https://github.com/CadQuery/cadquery) library. The design is fully parametric, allowing for easy customization of the spacecraft's dimensions and features.

![Placeholder for spacecraft rendering](https://via.placeholder.com/600x400.png?text=Render+of+spacecraft.step)
*(A rendering of the generated `output/spacecraft.step` file would go here.)*

## Features

-   **Parametric Design:** Easily change the spacecraft's dimensions by modifying parameters in the script.
-   **Modular:** The spacecraft is built from individual components (bus, solar arrays) which are defined in separate modules.
-   **STEP Export:** Generates a high-quality, standard STEP file suitable for use in other CAD software.
-   **Robust:** Includes geometry validation and clear error handling to ensure a valid output model.

## Prerequisites

To run this script, you need to have Python and the CadQuery library installed.

-   **Python 3.9+**
-   **CadQuery 2.2+**

For detailed installation instructions for CadQuery, please follow the official CadQuery Installation Guide. A Conda-based installation is highly recommended.

```bash
# Example installation using mamba (recommended)
mamba install -c conda-forge cadquery
```

## How to Run

1.  Navigate to the project's root directory.
2.  Run the script from your terminal:

    ```bash
    conda activate cadquery
    python my_model.py
    ```

3.  Upon successful execution, you will see output similar to this:

    ```
    INFO: Creating compound solid from assembly...
    INFO: Result is a <class 'cadquery.occ_impl.shapes.Compound'>.
    INFO: The generated model is a valid solid.
    INFO: Attempting to export to: /path/to/your/project/output/spacecraft.step
    SUCCESS: Model exported to /path/to/your/project/output/spacecraft.step
    ```

4.  The generated 3D model will be saved as `output/spacecraft.step`.

## Customization

You can easily generate different spacecraft designs by modifying the parameters at the top of the `my_model.py` script.

The main parameters are located in these two dictionaries:

```python
# --- Spacecraft Parameters ---
# By changing these values, you can generate a completely different design.
bus_params = {
    "width": 1.0, "depth": 1.0, "height": 1.5, "wall_thickness": 0.05
}

solar_array_params = {
    "panel_length": 2.0, "panel_width": 1.0, "panel_thickness": 0.02,
    "yoke_length": 0.2, "yoke_diameter": 0.1
}
```

Change any of these values and re-run the script to see your new design.



## Performance Profiling

Understanding the performance of your script is crucial for optimization. You can use Python's built-in `cProfile` module combined with `snakeviz` to get a visual and interactive breakdown of where your script spends its time. This is especially useful for identifying bottlenecks in complex CAD generation scripts.

### How to Profile with `snakeviz`

1.  **Install `snakeviz`:** If you don't have it installed, you can add it to your environment with pip:

    ```bash
    pip install snakeviz
    ```

2.  **Generate a Profile File:** Run your script using Python's `cProfile` module and save the statistics to an output file (e.g., `spacecraft.prof`).

    ```bash
    python -m cProfile -o spacecraft.prof my_model.py
    ```

3.  **Visualize the Profile:** Launch `snakeviz` with the profile file.

    ```bash
    snakeviz spacecraft.prof
    ```

This will open a new tab in your web browser with an interactive sunburst chart. The chart shows the call stack, with wider segments indicating functions that took more time to execute. You can click on segments to zoom in and analyze specific parts of your code.

!Example of snakeviz output



## Project Structure

A brief overview of the project's file structure:

```
.
├── my_model.py             # Main script to generate the spacecraft model.
├── spacecraft_parts/
│   ├── bus.py              # Module for creating the spacecraft bus.
│   └── solar_array.py      # Module for creating the solar arrays.
└── output/
    └── spacecraft.step     # The generated STEP file.
```SPACECRAFT_
