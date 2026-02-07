# Media Artwork Downloader
    Version: 1.0.0


## Description
The Media Artwork Downloader is a Python script that downloads fanart posters, thumbnails, and backgrounds for local movie and TV show media. The tool uses YAML code selected from Mediux to automatically retrieve images. These images are downloaded to a local storage location, renamed for easy human identification at a glance, then copied to their appropriate root folders in the media library. 











## File Naming
The file naming scheme follows current metadata naming conventions for the Jellyfin media server. Posters are tagged with "-poster" at the end of the file name. Season posters are tagged with "-S##-poster" to specify the season it belongs to. Episodes are tagged with "-S##E##-thumb" to specify the episode number and that it is a thumbnail. The backgrounds are simply tagged with "-background". This naming scheme allows the script to parse file names and identify the appropriate media folders to copy over to.

movie poster 		>> "Title (Year) [tmdb-####]-poster.jpg"
show poster  		>> "Title (Year) [tvdb-####]-poster.jpg"
show season poster 	>> "Title (Year) [tvdb-####]-S01-poster.jpg"
show episode 		>> "Title (Year) [tvdb-####]-S01E02-thumb.jpg"
background   		>> "Title (Year) [t?db-####]-background.jpg"

The names of poster and background files are simplified when copied to the media library. For example, a poster will be renamed to "poster.jpg" and placed in the appropriate root directory (movie, tv show, season), and a background will be renamed to "background.jpg" and placed in its appropriate root directory, as well. The episode thumbnails, however, are renamed to match the episode media file names with a "-thumb" at the end. The placement of these image files, coupled with the naming scheme, allow Jellyfin to automatically import the images to the server when performing routine library scans.








## Requirements
- TVDB API Key
- TMDB API Key
- Python 3.8
- YAML package for Python
    - Run `pip install pyyaml` on the machine the script will be running from







## Running the Script
1. Create a config.json file...

```
{
  "download_path": "/path/to/downloaded_images/directory",
  "tmdb_api_key": "<TMDB API KEY HERE>",
  "tvdb_api_key": "<TVDB API KEY HERE>",
  "tvdb_pin": "(Optional)",
  "shows_directory": "/path/to/show_media/directory",
  "movies_directory": "/path/to/movie_media/directory",
  "download_list_location": "/path/to/download_list.yaml"
}
```

Replace the values in the JSON pairings and save the file to the same directory as the Python script.




2. Create a download_list.yaml file...


3. 







## Acknowledgements
This project was inspired by and built off of emonhoque's [Mediux YAML Downloader](https://github.com/emonhoque/mediux-yaml-downloader).







----old----

The YAML code provided by Mediux into the 'download_list.yaml' file. This YAML code can be found at the desired fanart page. The script downloads the fanart files listed in 'download_collection.yaml' and saves them to a local storage location before copying them to their appropriate locations in the media library. The script follows a Jellyfin compatible naming scheme for media artwork (e.g., poster.jpg, background.jpg).