FROM python:3.9-bullseye

# wxPython dependencies
RUN apt-get update && apt install -y \
    libgstreamer-plugins-base1.0-0 \
    dpkg-dev \
    build-essential \
    libjpeg-dev \
    libtiff-dev \
    libsdl1.2-dev \
    libnotify-dev \
    freeglut3-dev \
    libsm-dev \
    libgtk-3-dev \
    libwebkit2gtk-4.0-dev \
    libxtst-dev \
    libgl1-mesa-dev \
    libglu1-mesa-dev \
    libgstreamer-plugins-base1.0-dev \
    libnotify-dev \
    libpng-dev \
    libsdl2-dev \
    libunwind-dev \
    libgtk2.0-dev

# Copying libretro_finder, installing poetry and adding it to PATH
WORKDIR /app
COPY . /app
ENV POETRY_HOME=/opt/poetry
RUN python3 -m venv $POETRY_HOME && $POETRY_HOME/bin/pip install poetry
ENV PATH="/opt/poetry/bin:${PATH}"

# Installing libretro_finder's deps
#RUN poetry config installer.max-workers 10
#RUN poetry install

# Default start
CMD ["/bin/bash"]