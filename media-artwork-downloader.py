import os
import yaml
import requests
import json
import argparse
from shutil import copy


VERSION = "1.0.2"
CONFIG_FILE = "config.json"

def load_config():
    try:
        with open(CONFIG_FILE, 'r') as file:
            return json.load(file)
    except:
        return {}

config = load_config()
DOWNLOADS_DIRECTORY = config.get("download_path", f"{os.path.expanduser('~user')}")
TMDB_API_KEY = config.get("tmdb_api_key", "")
TVDB_API_KEY = config.get("tvdb_api_key", "")
TVDB_PIN = config.get("tvdb_pin", "")
SHOWS_DIRECTORY = config.get("shows_directory", "")
MOVIES_DIRECTORY = config.get("movies_directory", "")
DOWNLOAD_LIST_LOCATION = config.get("download_list_location", "")
TOKEN = None









def download_image(args, url, dest_path):
    try:
        r = requests.get(url, stream=True, timeout=10)
        if r.status_code == 200:
            with open(dest_path, 'wb') as f:
                for chunk in r.iter_content(1024):
                    f.write(chunk)
        if (args.verbose):
            print(f"    - Downloaded: {dest_path}")
    except Exception as e:
        if (args.verbose):
            print(f"    > An error occurred: {e}")

def import_image(args, src_path, dest_path):
    try:
        if (os.path.isfile(dest_path)):
            if (args.overwrite):
                copy(src_path, dest_path)
                if (args.verbose):
                    print(f"    - Overwritten")
            else:
                if (args.verbose):
                    print(f"    - Already exists (skipped)")
        else:
            copy(src_path, dest_path)
            if (args.verbose):
                print(f"    - Synced")
    except Exception as e:
        if (args.verbose):
            print(f"    > Failed to sync: {e}")

def get_title_year_from_filename(filename):
    base_name = os.path.splitext(filename)[0]
    if '(' in base_name and ')' in base_name:
        title = base_name.rsplit(' (', 1)[0].strip()
        year = base_name.rsplit(' (', 1)[1].rstrip(')').strip()
        if year.isdigit() and len(year) == 4:
            return title, year
    return None, None









##### TVDB Section #####
### Bearer token is only valid for a month
def authenticate_tvdb():
    global TOKEN
    payload = {"apikey": TVDB_API_KEY}
    if TVDB_PIN:
        payload["pin"] = TVDB_PIN
    resp = requests.post("https://api4.thetvdb.com/v4/login", json=payload)
    if resp.ok:
        TOKEN = resp.json()["data"]["token"]
    else:
        raise Exception("TVDB Authentication failed.")

def get_headers():
    global TOKEN
    if not TOKEN:
        authenticate_tvdb()
    return {"Authorization": f"Bearer {TOKEN}"}

def get_show_info(tvdb_id):
    resp = requests.get(f"https://api4.thetvdb.com/v4/series/{tvdb_id}", headers=get_headers())
    if resp.ok:
        data = resp.json()["data"]
        title = data.get("name", "Unknown Title").replace(":", " -")
        year = data.get("firstAired", "0000")[:4]
        return title, year
    return None, None

def get_episode_titles(data_id, season_number):
    result = {}
    page = 0
    while True:
        resp = requests.get(
            f"https://api4.thetvdb.com/v4/series/{data_id}/episodes/default",
            headers=get_headers(),
            params={"page": page}
        )
        if not resp.ok:
            break
        data = resp.json()
        episodes = data.get("data", {}).get("episodes", []) if isinstance(data.get("data"), dict) else data.get("data", [])
        for ep in episodes:
            if ep.get("seasonNumber") == season_number:
                ep_num = str(ep.get("number"))
                ep_title = ep.get("name", "").strip()
                if ep_num and ep_title:
                    result[ep_num] = ep_title
        if not data.get("links", {}).get("next"):
            break
        page += 1
    return result

def get_movie_info(tmdb_id):
    url = f"https://api.themoviedb.org/3/movie/{tmdb_id}?api_key={TMDB_API_KEY}"
    resp = requests.get(url)
    if resp.ok:
        data = resp.json()
        title = data["original_title"].replace(":", " -")
        year = data["release_date"][:4]
        return title, year
    return None, None

# process yaml file
def process_yaml(file, args):
    # try to parse the yaml data
    try:
        parsed_yaml = yaml.safe_load(file)
    except Exception as e:
        print(f"Failed to parse YAML: {e}")
        return
    
    # iterate through each item in the yaml
    for data_id, data in parsed_yaml.items():
        if data.get("seasons"):
            if args.movies_only:
                continue
            title, year = get_show_info(data_id)
            if not title or not year:
                print(f"Could not get TV show title/year for {data_id}")
                continue
            local_file_name = f"{title} ({year}) [tvdb-{data_id}]"
        else:
            if args.shows_only:
                continue
            title, year = get_movie_info(data_id)
            if not title or not year:
                print(f"Could not get movie title/year for {data_id}")
                continue
            local_file_name = f"{title} ({year}) [tmdb-{data_id}]"
        
        print(f"\n{title} ({year})")

        # grab any posters and backgrounds
        poster_url = data.get("url_poster")
        background_url = data.get("url_background")
        if poster_url:
            file_ext = os.path.splitext(poster_url)[1] or ".jpg"
            local_poster_dest = os.path.join(DOWNLOADS_DIRECTORY, f"{local_file_name}-poster{file_ext}")
            if args.overwrite or not os.path.isfile(local_poster_dest):
                download_image(args, poster_url, local_poster_dest)
            else:
                if (args.verbose):
                    print(f"    - A poster exists (skipped)")
        
        if background_url:
            file_ext = os.path.splitext(background_url)[1] or ".jpg"
            local_background_dest = os.path.join(DOWNLOADS_DIRECTORY, f"{local_file_name}-background{file_ext}")
            if args.overwrite or not os.path.isfile(local_background_dest):
                download_image(args, background_url, local_background_dest)
            else:
                if (args.verbose):
                    print(f"    - A background exists (skipped)")
            


        # grab any season posters and episodes
        for season_num, season_data in data.get("seasons", {}).items():
            season_poster_url = season_data.get("url_poster")
            if season_poster_url:
                file_ext = os.path.splitext(season_poster_url)[1] or ".jpg"
                season_poster_name = f"{local_file_name}-S{int(season_num):02}-poster{file_ext}"
                local_destination = os.path.join(DOWNLOADS_DIRECTORY, season_poster_name)
                if args.overwrite or not os.path.isfile(local_destination):
                    download_image(args, season_poster_url, local_destination)
                else:
                    if (args.verbose):
                        print(f"    - A poster exists (skipped)")

            for episode_num, ep_data in season_data.get("episodes", {}).items():
                ep_url = ep_data.get("url_poster")
                if ep_url:
                    episode_file_name = f"{local_file_name}-S{int(season_num):02}E{int(episode_num):02}-thumb.jpg"
                    local_destination = os.path.join(DOWNLOADS_DIRECTORY, episode_file_name)
                    if args.overwrite or not os.path.isfile(local_destination):
                        download_image(args, ep_url, local_destination)
                    else:
                        if (args.verbose):
                            print(f"    - A thumbnail exists (skipped)")

    print("Downloads complete.")



def sync_library(args):
    print(f"Beginning library sync...")
    for root, files in os.walk(DOWNLOADS_DIRECTORY):
        for file in files:
            if file.endswith(('.jpg', '.png', '.jpeg')):
                file_ext = os.path.splitext(file)[1] or ".jpg"
                src_path = os.path.join(root, file)
                # Determine if it's a movie or TV show based on filename
                if '[tmdb-' in file:
                    # Movie
                    if (args.shows_only):
                        continue
                    title_year = file.rsplit(' [tmdb-', 1)[0]
                    title_year_cleaned = title_year.replace(" - ", " ", 1)
                    media_folder = os.path.join(MOVIES_DIRECTORY, title_year)
                    media_folder_cleaned = os.path.join(MOVIES_DIRECTORY, title_year_cleaned)
                elif '[tvdb-' in file:
                    # TV Show
                    if (args.movies_only):
                        continue
                    title_year = file.rsplit(' [tvdb-', 1)[0]
                    title_year_cleaned = title_year.replace(" - ", " ", 1)
                    media_folder = os.path.join(SHOWS_DIRECTORY, title_year)
                    media_folder_cleaned = os.path.join(SHOWS_DIRECTORY, title_year_cleaned)
                else:
                    continue  # Not a recognized format

                print(f"- {file}...")

                
                if not os.path.isdir(media_folder):
                    if (args.verbose):
                        print(f"    > Media folder does not exist: [{title_year}]")
                    if ' - ' in title_year:
                        if (args.verbose):
                            print(f"    > Attempting alternate title format...")
                        if not os.path.isdir(media_folder_cleaned):
                            if (args.verbose):
                                print(f"    > Media folder does not exist: [{media_folder_cleaned}]")
                            continue  # Alternate media folder also doesn't exist; skip
                        else:
                            media_folder = media_folder_cleaned
                    else:
                        continue  # Media folder doesn't exist; skip

                # Determine destination path
                if '-poster' in file:
                    if ']-S' in file:
                        # Season poster
                        season_part = file.rsplit(']-S', 1)[1]
                        season_number = season_part.split('-')[0]
                        season_folder = os.path.join(media_folder, f"Season {int(season_number):02}")
                        if not os.path.isdir(season_folder):
                            if (args.verbose):
                                print(f"    > Season folder does not exist: [{season_folder}]")
                            continue  # Season folder doesn't exist; skip
                        dest_path = os.path.join(season_folder, f"poster{file_ext}")
                    else:
                        dest_path = os.path.join(media_folder, f"poster{file_ext}")
                elif '-background' in file:
                    dest_path = os.path.join(media_folder, f"background{file_ext}")
                elif '-thumb' in file:
                    # Episode thumbnail
                    thumb_part = file.rsplit('-thumb', 1)[0]
                    # if ']-S' in thumb_part and 'E' in thumb_part:
                    season_episode_part = thumb_part.rsplit(']-S', 1)[1]
                    season_number = season_episode_part.split('E')[0]
                    episode_number = season_episode_part.split('E')[1]
                    season_folder = os.path.join(media_folder, f"Season {int(season_number):02}")
                    if not os.path.isdir(season_folder):
                        if (args.verbose):
                            print(f"    > Season folder does not exist: [{season_folder}]")
                        continue  # Season folder doesn't exist; skip
                    # Find the corresponding video file
                    for item in os.listdir(season_folder):
                        file_name_no_ext = os.path.splitext(item)[0]
                        if os.path.splitext(item)[1] == ".mkv" and f" - S{int(season_number):02}E{int(episode_number):02} - " in file_name_no_ext:
                            dest_path = os.path.join(season_folder, f"{file_name_no_ext}.jpg")
                            break
                    else:
                        if (args.verbose):
                                print(f"    > No matching episode media file found: [{thumb_part}]")
                        continue  # No matching video file found; skip
                else:
                    continue  # Not a poster, background, or thumbnail

                import_image(args, src_path, dest_path)
        
    print(f"Syncing complete.")







def main():
    parser = argparse.ArgumentParser(description="Download media images based on YAML configuration.")

    parser.add_argument('mode', choices=['full', 'pull', 'sync'])
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    parser.add_argument('-o', '--overwrite', action='store_true', help='Overwrites any local files that already exist')
    parser.add_argument('-s', '--shows-only', action='store_true', help='Only process TV shows')
    parser.add_argument('-m', '--movies-only', action='store_true', help='Only process movies')

    args = parser.parse_args()

    if (args.mode != 'sync'):
        with open(DOWNLOAD_LIST_LOCATION, "r") as file:
            process_yaml(file, args)

    if (args.mode != 'pull'):
        sync_library(args)




if __name__ == "__main__":
    main()
