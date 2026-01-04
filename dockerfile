# Base image
FROM alpine:3.18

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV NODE_VERSION=24.12.0
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=false

# Install system dependencies
RUN apk add --no-cache \
    bash \
    curl \
    wget \
    python3 \
    py3-pip \
    ffmpeg \
    nss \
    freetype \
    harfbuzz \
    ttf-freefont \
    font-noto \
    udev \
    build-base \
    libffi-dev \
    zlib-dev \
    xz-dev \
    git \
    && python3 -m ensurepip \
    && pip3 install --upgrade pip setuptools wheel

# Install Node.js manually
RUN wget https://nodejs.org/dist/v$NODE_VERSION/node-v$NODE_VERSION-linux-x64.tar.xz \
    && tar -xJf node-v$NODE_VERSION-linux-x64.tar.xz \
    && mv node-v$NODE_VERSION-linux-x64 /usr/local/node \
    && ln -s /usr/local/node/bin/node /usr/local/bin/node \
    && ln -s /usr/local/node/bin/npm /usr/local/bin/npm \
    && ln -s /usr/local/node/bin/npx /usr/local/bin/npx \
    && rm node-v$NODE_VERSION-linux-x64.tar.xz

# Set working directory
WORKDIR /app

# Copy Node.js dependencies first for caching
COPY package.json package-lock.json ./
RUN npm install --unsafe-perm

# Copy Python requirements and install
COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

# Default command to run both Python and Node.js
CMD ["bash", "-c", "python3 main.py & node Main.js"]
