# Step 1: Start from an official base image
# We use the official Miniconda image, which has Conda pre-installed.
FROM continuumio/miniconda3:latest

# Step 2: Set a working directory inside the container
# This is where all our app files will live.
WORKDIR /app

# Step 3: Copy the environment/src files
# We only copy this file first to take advantage of Docker's layer caching.
# If the environment file doesn't change, Docker won't re-install all the
# packages every time, making builds much faster.
COPY environment.yml .
RUN conda env create -f environment.yml

COPY src/ ./src

# Step 4: Expose the port
# This tells Docker that your application will listen on port 8000.
EXPOSE 8000

# Step 5: Define the command to run your app
# This is the "entrypoint" for your container.
# It activates the Conda environment and runs the exact uvicorn
# command we used to run the server.
CMD ["conda", "run", "-n", "portfolio-guard", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--app-dir", "src/"]
