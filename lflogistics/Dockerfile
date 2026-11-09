# Learn Fast — Freight & Logistics workbench
#
# An EMPTY environment: the libraries this track needs, and none of the course notebooks.
# You write your own notebooks in work/ — that folder is what you submit for the drill.
FROM quay.io/jupyter/minimal-notebook:python-3.12

# NOTE: the user is renamed jovyan -> learnfast at RUN time (see docker-compose.yml), never here:
# upstream's start.sh calls `id -u jovyan` under `set -e`, so renaming in the image makes the
# container exit 1 on startup with no error message.

# minimal-notebook ships JupyterLab and nothing else, so every library this track uses is
# listed explicitly. No torch, no GPU: the language model runs in Ollama on YOUR machine, outside
# this container (see docker-compose.yml and the README).
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
