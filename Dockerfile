# --- Builder Stage ---
# Use mambaforge for faster environment creation. Using a specific version is good practice.
FROM condaforge/mambaforge:24.3.0-0 AS cadquery_builder

# Set the working directory
WORKDIR /cadquery_project

# Copy environment file first to leverage Docker layer caching.
# If this file doesn't change, the following RUN command will be cached.
COPY environment-runtime.yml .

# This is the key fix: Copy the application source code and setup files.
# The pip install inside your environment.yml (likely '-e .') needs these files.
COPY setup.py .
COPY README.md .
# The setup.py uses find_packages(), so we need to copy the package source.
COPY cadquery ./cadquery

# Create the conda environment from the file.
# The environment name 'cadquery-runtime' is defined in the yml.
RUN mamba env create -f environment-runtime.yml && \
    mamba clean --all --yes

# --- Final Stage ---
# Use a smaller base image for the final application to reduce image size.
FROM debian:bullseye-slim

# Add build arguments to accept host user's UID/GID
ARG UID=1001
ARG GID=1001

# Set the working directory in the final image
WORKDIR /app

# Create a non-root user with the provided UID/GID for better security.
# This ensures file permissions match the host user and sets HOME correctly.
RUN apt-get update && apt-get install -y --no-install-recommends \
    # OCCT, the CAD kernel, requires some system libraries to run, even headless.
    libxext6 \
    libfontconfig1 \
    libfreetype6 \
    # Clean up apt cache to keep the image small
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --gid ${GID} appuser \
    && useradd --uid ${UID} --gid ${GID} -m appuser

# Copy the conda environment from the builder stage
# The destination path should match the source path for consistency.
COPY --from=cadquery_builder /opt/conda/envs/cadquery-runtime /opt/conda/envs/cadquery-runtime

# Also change ownership of the conda environment to the runtime user.
RUN chown -R ${UID}:${GID} /opt/conda/envs/cadquery-runtime

# Copy the model script that will be executed
COPY my_model.py .

# Copy the modular parts directory
COPY spacecraft_parts ./spacecraft_parts

# Create output dir and change ownership of the entire app directory to the runtime user.
# This ensures the user can write to the output dir and avoids other permission issues.
RUN mkdir -p /app/output && chown -R ${UID}:${GID} /app

USER ${UID}:${GID}

# Add the conda environment's bin directory to the PATH
ENV PATH="/opt/conda/envs/cadquery-runtime/bin:$PATH"

# Set the default command to run the script
CMD ["python", "my_model.py"]