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
}

build {
  name = "overseerr-media-mender"
  sources = [
    "source.docker.python"
  ]

  provisioner "file" {
    source      = "../src"
    destination = "/app"
  }

  provisioner "shell" {
    inline = [
      "cd /app",
      "pip install --no-cache-dir -r requirements.txt"
    ]
  }

  post-processor "docker-tag" {
    repository = "ghcr.io/${var.github_username}/overseerr-media-mender"
    tags       = ["latest", "${var.image_version}"]
  }
}

variable "github_username" {
  type    = string
  default = "awanaut"
}

variable "image_version" {
  type    = string
  default = "0.1"
}