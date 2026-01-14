FROM python:3.12-slim

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . .

# Describes which ports the server is listening on
EXPOSE 5000

# Update apt (while building the image, not when running the container)
RUN apt-get update -y \
# Upgrade pip (while building the image, not when running the container)
&& pip install --no-cache-dir --upgrade pip \
# Install the dependencies (while building the image, not when running the container)
&& pip install --no-cache-dir -r requirements.txt \
&& chmod +x start.sh

CMD ["./start.sh"]

