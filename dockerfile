# Use an official Python runtime as a parent image
FROM python:3.13-slim

# Set the working directory in the container
WORKDIR /app

# Install Poetry
RUN pip install --no-cache-dir poetry

# Copy the current directory contents into the container at /app
COPY . /app

# Install dependencies using Poetry
RUN poetry install

# Run app.py when the container launches
CMD ["poetry", "run", "python", "./tribuz_populate/__main__.py"]