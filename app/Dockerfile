FROM python:3.8-buster

# Create project directory
RUN mkdir -p /mb9k/staticfiles && \
    mkdir -p /mb9k/mediafiles
WORKDIR /mb9k

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install dependencies
RUN apt-get update && \
    apt-get install -y \
        ffmpeg \
        python3-dev \
        python-opencv \
        postgresql \
        cmake \
        netcat \
        vim && \
    rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy django application
COPY . .

ENTRYPOINT ["/mb9k/entrypoint.sh"]

