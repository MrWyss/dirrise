# dirrise
<p align="center">
  <img alt="ai generated dirrise logo" src="docs/assets/aigenlogo.png" width="300">
</p>

---

***<p style="text-align: center;">«Watches a folder for new files. If they match with the given pattern, it sends a notification via [apprise](https://github.com/caronc/apprise).»</p>***

---

![demo dirrise](docs/assets/demo_dirrise.gif)

---

## Python Usage

```text
usage: dirrise.py [-h] [-f FOLDER_PATH] [-p FILE_PATTERN] [-u APPRISE_URL]
                  [-t TITLE_TEMPLATE] [-m MESSAGE_TEMPLATE] [-r] [-v]

Watch a folder for file creations and send notifications.

optional arguments:
  -h, --help            show this help message and exit
  -f FOLDER_PATH, --folder-path FOLDER_PATH
                        path to the folder to watch.
                        Can also be set with environment Variable FOLDER_PATH
                          e.g. /home/user/watchdir or C:\Users\user\watchdir
  -p FILE_PATTERN, --file-pattern FILE_PATTERN
                        regular expression pattern to match file names
                        can also be set with environment Variable FILE_PATTERN
                          e.g. \.txt$
  -u APPRISE_URL, --apprise-url APPRISE_URL
                        apprise url
                        can also be set with environment Variable APPRISE_URL
                          e.g. ntfys://user:password@ntfy.domain.org/watchdir
  -t TITLE_TEMPLATE, --title-template TITLE_TEMPLATE
                        notification title template
                        can also be set with environment Variable TITLE_TEMPLATE
                          e.g. New file {FILE} found in subfolder {SUBFOLDER_NAME} and folder {FOLDER} for the watch folder {WATCH_FOLDER}
                        available variables: FILE, FILE_PATH, FOLDER, SUBFOLDER_NAME, WATCH_FOLDER, RELATIVE_PATH
  -m MESSAGE_TEMPLATE, --message-template MESSAGE_TEMPLATE
                        notification message template
                        can also be set with environment Variable MESSAGE_TEMPLATE
                          e.g. New file {FILE} found in subfolder {SUBFOLDER_NAME} and folder {FOLDER} for the watch folder {WATCH_FOLDER}
                        available variables: FILE, FILE_PATH, FOLDER, SUBFOLDER_NAME, WATCH_FOLDER, RELATIVE_PATH
  -r, --recursive       watch folder recursively
                        can also be set with environment Variable RECURSIVE
                          e.g. True or False
  -v, --version         show program's version number and exit
```

## Docker Usage

[![Publish Docker image](https://github.com/MrWyss/dirrise/actions/workflows/publish_docker_image.yml/badge.svg)](https://github.com/MrWyss/dirrise/actions/workflows/publish_docker_image.yml)
[![Image Tag](https://ghcr-badge.egpl.dev/mrwyss/dirrise/tags?color=%2344cc11&ignore=&n=1&label=latest+image&trim=)](https://github.com/MrWyss/dirrise/pkgs/container/dirrise)

### With parameters

```bash
docker run -d \
  --name "dirrise_containername"                                   `# Create unique container name if you run multiple instances` \
  -v "/home/username/hostdir:/mnt/watchdir"                        `# Host:Container mapping, the container path can by anything but has to match with --folder-path` \
  -it ghcr.io/mrwyss/dirrise:latest python ./dirrise.py            `# No change reguired` \
  --folder-path "/mnt/watchdir"                                    `# Must match with container path above` \
  --file-pattern "\.txt$"                                          `# regular expression pattern to match file names, like \.txt$` \
  --apprise-url "ntfys://user:pa\$\$sword@ntfy.domain.org/topic"   `# Regular apprise Url, you may have to escape special characters` \
```

### With environment variables

```bash
docker run -it -d --name "dirrise_containername" \
-v "/home/username/hostdir:/mnt/watchdir" \
-e FOLDER_PATH="/mnt/watchdir" \
-e FILE_PATTERN="\.txt$" \
-e APPRISE_URL="ntfys://user:password@ntfydomainorg/topic" \
-e TITLE_TEMPLATE="Changes in {WATCH_FOLDER}" \
-e MESSAGE_TEMPLATE="New file {FILE} in {FOLDER}" \
-e RECURSIVE=true \
ghcr.io/mrwyss/dirrise:latest
```

### With Environment file

.env file:

```bash
FOLDER_PATH=/mnt/watchdir
FILE_PATTERN=\.txt$
APPRISE_URL=ntfys://user:password@ntfydomainorg/topic
TITLE_TEMPLATE=Changes in {WATCH_FOLDER}
MESSAGE_TEMPLATE=New file {FILE} in {FOLDER}
RECURSIVE=true
```

run command:

```bash
docker run -it -d --name "dirrise_containername" \
-v "/home/username/hostdir:/mnt/watchdir" \
--env-file .env \
ghcr.io/mrwyss/dirrise:latest
```

## Templating

The **message** and **title** can be templated with the following variables:

- **{FILE}** --> file.txt
- **{FILE_PATH}** --> /home/user/watchdir/subdir/file.txt
- **{FOLDER}** --> /home/user/watchdir/subdir
- **{SUBFOLDER_NAME}** --> subdir
- **{WATCH_FOLDER}** --> /home/user/watchdir
- **{RELATIVE_PATH}** --> subdir/file.txt

## Contributions

- please do, I'm happy to accept PRs.  
