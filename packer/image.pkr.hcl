packer {
  required_plugins {
    docker = {
      version = "~> 1"
      source  = "github.com/hashicorp/docker"
    }
  }
}
variable "registry" {
  type    = string
  default = "ghcr.io"
}

variable "image_name" {
  type    = string
  default = "awanaut/overseerr-media-mender"
}
source "docker" "python" {
  image  = "python:3.9-slim"
  commit = true
  changes = [
    "WORKDIR /app",
    "ENV RUN_INTERVAL=3600",
    "ENV PYTHONUNBUFFERED=1",
    "CMD [\"python\", \"-u\", \"omm.py\"]"
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
    repository = "${var.registry}/${var.image_name}"
    tags       = ["latest"]
  }
}