packer {
  required_plugins {
    docker = {
      version = "~> 1"
      source  = "github.com/hashicorp/docker"
    }
  }
}
source "docker" "python" {
  image  = "python:3.9-slim"
  commit = true
  changes = [
    "WORKDIR /app",
    "COPY . /app",
    "RUN pip install --no-cache-dir -r requirements.txt",
    "CMD [\"python\", \"omm.py\"]"
  ]
}

build {
  name = "overseerr-media-mender"
  sources = [
    "source.docker.python"
  ]

  provisioner "file" {
    source      = "src/"
    destination = "/app/"
  }

  provisioner "file" {
    source      = "requirements.txt"
    destination = "/app/requirements.txt"
  }

  post-processor "docker-tag" {
    repository = "ghcr.io/awanaut/overseerr-media-mender"
    tags       = ["latest"]
  }
}