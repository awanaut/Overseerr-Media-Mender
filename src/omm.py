import requests
import os
import time
import signal
import sys
from dotenv import load_dotenv
from colorama import init, Fore, Back, Style

init(autoreset=True)

load_dotenv()

OVERSEERR_URL = os.getenv('OVERSEERR_URL')
OVERSEERR_API_KEY = os.getenv('OVERSEERR_API_KEY')
RADARR_URL = os.getenv('RADARR_URL')
RADARR_API_KEY = os.getenv('RADARR_API_KEY')
SONARR_URL = os.getenv('SONARR_URL')
SONARR_API_KEY = os.getenv('SONARR_API_KEY')

def print_header(text):
    print(f"\n{Fore.CYAN}{Style.BRIGHT}{text}")
    print(f"{Fore.CYAN}{'-' * len(text)}{Style.RESET_ALL}")

def print_success(text):
    print(f"{Fore.GREEN}✔ {text}{Style.RESET_ALL}")

def print_warning(text):
    print(f"{Fore.YELLOW}⚠ {text}{Style.RESET_ALL}")

def print_error(text):
    print(f"{Fore.RED}✘ {text}{Style.RESET_ALL}")

def get_overseerr_issues():
    url = f"{OVERSEERR_URL}/api/v1/issue"
    headers = {"X-Api-Key": OVERSEERR_API_KEY}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()['results']

def get_overseerr_media_details(issue_id):
    url = f"{OVERSEERR_URL}/api/v1/issue/{issue_id}"
    headers = {"X-Api-Key": OVERSEERR_API_KEY}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def find_radarr_movie(tmdb_id):
    url = f"{RADARR_URL}/api/v3/movie"
    params = {"apikey": RADARR_API_KEY, "tmdbId": tmdb_id}
    response = requests.get(url, params=params)
    response.raise_for_status()
    movies = response.json()
    return movies[0] if movies else None

def find_sonarr_series(tvdb_id):
    url = f"{SONARR_URL}/api/v3/series"
    params = {"apikey": SONARR_API_KEY, "tvdbId": tvdb_id}
    response = requests.get(url, params=params)
    response.raise_for_status()
    series_list = response.json()
    return series_list[0] if series_list else None

def get_sonarr_episodes(series_id, season_number):
    url = f"{SONARR_URL}/api/v3/episode"
    params = {
        "apikey": SONARR_API_KEY,
        "seriesId": series_id,
        "seasonNumber": season_number
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def delete_radarr_movie_file(movie_file_id):
    url = f"{RADARR_URL}/api/v3/moviefile/{movie_file_id}"
    params = {"apikey": RADARR_API_KEY}
    response = requests.delete(url, params=params)
    response.raise_for_status()
    print(f"Deleted movie file")

def delete_sonarr_episode_file(episode_file_id):
    url = f"{SONARR_URL}/api/v3/episodefile/{episode_file_id}"
    params = {"apikey": SONARR_API_KEY}
    response = requests.delete(url, params=params)
    response.raise_for_status()
    print(f"Deleted episode file")

def search_radarr_movie(movie_id):
    url = f"{RADARR_URL}/api/v3/command"
    params = {"apikey": RADARR_API_KEY}
    data = {
        "name": "MoviesSearch",
        "movieIds": [movie_id]
    }
    response = requests.post(url, json=data, params=params)
    response.raise_for_status()
    print(f"Triggered search for movie")

def search_sonarr_series(series_id):
    url = f"{SONARR_URL}/api/v3/command"
    params = {"apikey": SONARR_API_KEY}
    data = {
        "name": "SeriesSearch",
        "seriesId": series_id
    }
    response = requests.post(url, json=data, params=params)
    response.raise_for_status()
    print(f"Triggered search for series")

def update_overseerr_issue_status(issue_id, status):
    url = f"{OVERSEERR_URL}/api/v1/issue/{issue_id}/{status}"
    headers = {"X-Api-Key": OVERSEERR_API_KEY}
    response = requests.post(url, headers=headers)
    response.raise_for_status()
    print(f"Updated Overseerr issue to status: {status}")

def main():
    issues = get_overseerr_issues()
       
    for issue in issues:
        issue_details = get_overseerr_media_details(issue['id'])
        media = issue_details.get('media', {})
        media_type = media.get('mediaType', 'unknown')

        if media_type == 'movie':
            radarr_movie = find_radarr_movie(media.get('tmdbId'))
            
            if radarr_movie:
                print_header(f"Processing Movie: {radarr_movie['title']}")
                
                if radarr_movie.get('hasFile'):
                    print_warning(f"Attempting to delete file for movie: {radarr_movie['title']}")
                    delete_radarr_movie_file(radarr_movie['movieFile']['id'])
                else:
                    print_warning(f"No file to delete for movie: {radarr_movie['title']}")
                
                search_radarr_movie(radarr_movie['id'])
            else:
                print_error(f"Movie not found in Radarr: {media.get('title', 'Unknown')}")
        
        elif media_type == 'tv':
            sonarr_series = find_sonarr_series(media.get('tvdbId'))
            
            if sonarr_series:
                print_header(f"Processing TV Show: {sonarr_series['title']}")
                
                season_number = issue_details.get('problemSeason')
                episode_number = issue_details.get('problemEpisode')
                
                print(f"Reported issue: Season {season_number}, Episode {episode_number}")
                
                if season_number is not None and episode_number is not None:
                    episodes = get_sonarr_episodes(sonarr_series['id'], season_number)
                    
                    for episode in episodes:
                        if episode.get('episodeNumber') == episode_number:
                            if episode.get('episodeFileId'):
                                print_warning(f"Attempting to delete file for {sonarr_series['title']} S{season_number:02d}E{episode_number:02d}")
                                delete_sonarr_episode_file(episode['episodeFileId'])
                            else:
                                print_warning(f"No file found for {sonarr_series['title']} S{season_number:02d}E{episode_number:02d}")
                            break
                    else:
                        print_error(f"Episode {episode_number} of season {season_number} not found")
                else:
                    print_error(f"Season or episode number not provided for issue")
                
                search_sonarr_series(sonarr_series['id'])
            else:
                print_error(f"TV series not found in Sonarr: {media.get('title', 'Unknown')}")
        
        else:
            print_error(f"Unknown media type: {media_type}")
        
        update_overseerr_issue_status(issue['id'], 'resolved')
        print_success(f"Updated Overseerr issues to resolved.")
        

def run_periodically(interval=3600):  # Run every hour by default
    while True:
        print(f"{Fore.CYAN}Running Overseerr Media Mender...{Style.RESET_ALL}")
        main()
        print(f"{Fore.CYAN}Sleeping for {interval} seconds...{Style.RESET_ALL}")
        time.sleep(interval)

def signal_handler(sig, frame):
    print(f"{Fore.YELLOW}Received shutdown signal. Exiting...{Style.RESET_ALL}")
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    interval = int(os.getenv('RUN_INTERVAL', 3600))  # Allow interval to be set via environment variable
    run_periodically(interval)