# Media Artwork Downloader
Version: 1.0.0


## Description
The Media Artwork Downloader is a Python script that downloads fanart posters, thumbnails, and backgrounds for local movie and TV show media. The tool uses YAML code selected from Mediux to automatically retrieve images. These images are downloaded to a local storage location, renamed for easy human identification at a glance, then copied to their appropriate root folders in the media library. 


## File Naming
The file naming scheme follows current metadata naming conventions for the Jellyfin media server. Posters are tagged with "-poster" at the end of the file name. Season posters are tagged with "-S##-poster" to specify the season it belongs to. Episodes are tagged with "-S##E##-thumb" to specify the episode number and that it is a thumbnail. The backgrounds are simply tagged with "-background". This naming scheme allows the script to parse file names and identify the appropriate media folders to copy over to.

| Image Type | Naming Scheme |
| ---------- | ------------- |
| Movie Poster | "Title (Year) [tmdb-####]-poster.jpg" |
| Show Poster | "Title (Year) [tvdb-####]-poster.jpg" |
| Season Poster | "Title (Year) [tvdb-####]-S01-poster.jpg" |
| Episode Thumbnail | "Title (Year) [tvdb-####]-S01E02-thumb.jpg" |
| Background | "Title (Year) [t?db-####]-background.jpg" |

The names of poster and background files are simplified when copied to the media library. For example, a poster will be renamed to "poster.jpg" and placed in the appropriate root directory (movie, tv show, season), and a background will be renamed to "background.jpg" and placed in its appropriate root directory, as well. The episode thumbnails, however, are renamed to match the episode media file names with a "-thumb" at the end. The placement of these image files, coupled with the naming scheme, allow Jellyfin to automatically import the images to the server when performing routine library scans.


## Requirements
- TVDB API Key
- TMDB API Key
- Python 3.8
- YAML package for Python
    - Run `pip install pyyaml` on the machine the script will be running from


## Running the Script
### 1. Create a _config.json_ file

Below is a template for the `config.json` file. Simply replace the values in the JSON entries, and then save the file in the same directory as the Python script. 

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

### 2. Create a _download_list.yaml_ file

YAML data can be found for any fanart on the Mediux website. When selecting an image or image set, a YAML button and a Download button can be found under the media title. Click the YAML button, copy the data in the popup, and paste the data into your 'download_list.yaml' file. 

The 'download_list.yaml' file is structured exactly how it's copied from Mediux. Here is an example with the YAML structure often found for movie titles:

```
  #####: # Title (Year) Poster by Author on MediUX. Reference URL
    url_poster: https://example.url.com
    url_background: https://example.url.com
```

Here is an example with the YAML structure often found for TV shows:

```
  #####: # TVDB id for Title. Set by Author on MediUX. Reference URL
    url_poster: https://example.url.com
    url_background: https://example.url.com
    seasons:
      1:
        url_poster: https://example.url.com
        episodes:
          1:
            url_poster: https://example.url.com
          2:
            url_poster: https://example.url.com
          3:
            url_poster: https://example.url.com
          4:
            url_poster: https://example.url.com
          5:
            url_poster: https://example.url.com
          6:
            url_poster: https://example.url.com
      2:
        url_poster: https://example.url.com
        episodes:
          1:
            url_poster: https://example.url.com
          2:
            url_poster: https://example.url.com
          3:
            url_poster: https://example.url.com
          4:
            url_poster: https://example.url.com
          5:
            url_poster: https://example.url.com
          6:
            url_poster: https://example.url.com
```

This structure allows the file is be expandable, easily adding items to the list of downloads. It also allows the data to be configurable, so the user can mix the artists of any item within a title's set. For example, the season posters from one artist can be added to the file, and then inside those seasons the episode thumbnails can be from another artist. This can be achieved by simply replacing the appropriate URLs with new ones from the Mediux YAML data.

Additionally, the file does not have to be named 'download_list.yaml'. It can be renamed to anything, but it is important to match the name provided in the 'download_list_location' entry value of the 'config.json'.

### 3. Run the script

CLI arguments for the script:

| Command | Description |
| ----- | ----- |
| --help, -h | Displays information about runnning the script |
| --verbose, -v | Enables more detailed output |
| --overwrite, -o | Enables overwriting already existing image files |
| full | Required arg option #1 - Performs both ***pull*** and ***sync*** functions |
| pull | Required arg option #2 - Performs a download of images, does not sync to media library |
| sync | Required arg option #3 - Performs a sync of downloaded images to media library. Does not download new images |

### 4. Update the image metadata

Run a Jellyfin library scan to load the new images into the server.


# Future Development (:crossed_fingers:)
- Functionality to collect fanart for the music side of the Jellyfin server
- User controlled file naming for local storage
- Support downloading from multiple fanart sites
- Support for multiple backgrounds for a single item
- Better verbose output
- And more...


## Acknowledgements
This project was inspired by and built off of emonhoque's [Mediux YAML Downloader](https://github.com/emonhoque/mediux-yaml-downloader).

