# Learn Fast — AI Tour workbench
#
# An EMPTY environment: the libraries the seven tour drills use, and none of the course notebooks.
# You write your own notebooks in work/.
FROM quay.io/jupyter/minimal-notebook:python-3.12

# NOTE: the user is renamed jovyan -> learnfast at RUN time (see docker-compose.yml), never here:
# upstream's start.sh calls `id -u jovyan` under `set -e`, so renaming in the image makes the
# container exit 1 on startup with no error message.

# CPU-only torch: the default PyPI wheels drag in the CUDA runtime, which is gigabytes of
# download for a course that is deliberately GPU-free.
RUN pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cpu \
      torch==2.14.1

# minimal-notebook ships JupyterLab and nothing else, so every library the drills use is listed
# explicitly, at the versions the notebooks were run against.
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
