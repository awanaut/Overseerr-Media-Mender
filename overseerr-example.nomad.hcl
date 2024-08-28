job "overseerr" {
  group "overseerr" {
    count = 1
    network {
      port "http" {
        to     = "5055"
        static = "5055"
      }
    }
    task "overseerr-docker" {
      driver = "docker"
      env {
        TZ        = "America/New_York"
      }
      resources {
        cpu    = 1500
        memory = 768
      }
      config {
        image       = "sctx/overseerr:latest"
        ports       = ["http"]
        dns_servers = ["1.1.1.1"]
        mount {
          type     = "bind"
          source   = "/volume1/nvme/nomad/overseerr"
          target   = "/app/config"
          readonly = false
        }
      }
      service {
        provider = "nomad"
        name     = "${JOB}"
        port     = "http"
        tags = [
          "traefik.enable=true",
          "traefik.http.routers.overseerr.tls=true",
          "traefik.http.routers.overseerr.rule=Host(`overseerr.example.com`)",
          "traefik.http.routers.overseerr.tls.domains[0].main=*.example.com",
          "traefik.http.routers.overseerr.tls.certresolver=letsencrypt",
        ]
      }
    }
    task "omm" {
      driver = "docker"
      env {
        INTERVAL          = 60 #seconds
        OVERSEERR_URL     = "https://your-overseerr-url "
        OVERSEERR_API_KEY = "yourapikey"
        RADARR_URL        = "http://your-radarr-url"
        RADARR_API_KEY    = "yourapikey"
        SONARR_URL        = "http://your-sonarr-url"
        SONARR_API_KEY    = "yourapikey"
      }
      config {
        image = "ghcr.io/awanaut/overseerr-media-mender:latest"
      }
      lifecycle {
        hook    = "poststart"
        sidecar = true
      }
    }
  }
}