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
    source      = "src/requirements.txt"
    destination = "/app/requirements.txt"
  }

  provisioner "shell" {
    inline = [
      "pip install --no-cache-dir -r /app/requirements.txt"
    ]
  }

  post-processor "docker-tag" {
    repository = "ghcr.io/yourusername/overseerr-media-mender"
    tags       = ["latest"]
  }
}