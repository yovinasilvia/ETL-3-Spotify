FROM quay.io/astronomer/astro-runtime:12.1.1

# Install library
USER root
RUN apt-get update && apt-get install -y \
  build-essential \
  default-libmysqlclient-dev \
  && apt-get clean

# Switch to astro user and install python-dotenv
USER astro
RUN pip install python-dotenv
