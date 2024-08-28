# Overseerr Media Mender

Overseerr Media Mender is a python script designed to manage and resolve issues reported in Overseerr by interfacing with Radarr and Sonarr. Overseerr does not have this functionality built it and with their teams busy life and giant backlog of PR's, I doubt we'll see it integrated any time soon. In the meantime I wrote this script as a stop gap. It's overall pretty basic and meets my needs. I hope it helps you!

## Features

- Checks for issues reported in Overseerr at a set interval
- Deletes movie files in Radarr and tv show episode files in Sonarr
- Triggers a search 
- Resolves the issue in Overseerr

## Limitation
Sonarr's API does not have an easy way to add a release to a block list unless it's currently stuck in the queue. You may run the risk of Sonarr regrabbing the same release. This can be a problem if it's a fully borked release instead of a half imported media item.

I have not tested this on Jellyseer, but I imagine since the API's are the same, it should work.

## Prerequisites

- Docker 
- Nomad (Optional)
- Overseerr 
- Radarr 
- Sonarr

## Docker Usage
I personally run it as a sidecar to Overseerr in Nomad, however you can run this as a standalone container if you'd like. 

1. Create a `.env` file. Use the example one in the repo if needed.
2. docker run --env-file .env ghcr.io/awanaut/overseerr-media-mender:latest

## Nomad Usage
Use the example Nomad job file which includes [Traefik](https://doc.traefik.io/traefik/routing/providers/nomad/) (just delete the Traefik tags if you don't want it) or add the following task to your Overseerr job file:

```less secure option
task "omm" {
      driver = "docker"
      env {
        INTERVAL          = 60
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
```
Adjust the URLs and API keys according to your setup. The `INTERVAL` is in seconds and determines how often the script checks for issues (default is 1 hour).

If you want to store your API key's as an encrypted variable, follow this tutorial: (https://developer.hashicorp.com/nomad/tutorials/variables/variables-tasks)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Disclaimer

This tool is not officially associated with Overseerr, Radarr, or Sonarr. Use at your own risk.