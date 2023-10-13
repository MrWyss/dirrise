# dirrise

[![Publish Docker image](https://github.com/MrWyss/dirrise/actions/workflows/publish_docker_image.yml/badge.svg)](https://github.com/MrWyss/dirrise/actions/workflows/publish_docker_image.yml)
[![Image Tag](https://ghcr-badge.egpl.dev/mrwyss/dirrise/tags?color=%2344cc11&ignore=&n=1&label=latest+image&trim=)](https://github.com/MrWyss/dirrise/pkgs/container/dirrise)

Watches a folder for new files with a given extension and sends a notification via apprise.

## Help

```text
usage: dirrise.py [-h] [--folder-path FOLDER_PATH] [--file-extension FILE_EXTENSION] [--apprise-url APPRISE_URL] [--title-template TITLE_TEMPLATE] [--message-template MESSAGE_TEMPLATE] [--recursive] [--version]

Watch a folder for file creations and send notifications.

optional arguments:
  -h, --help            show this help message and exit
  --folder-path FOLDER_PATH
                        path to the folder to watch, like /home/user/watchdir or C:\Users\user\watchdir
  --file-extension FILE_EXTENSION
                        file extension to watch, like .txt
  --apprise-url APPRISE_URL
                        appriser URL like ntfys://user:password@ntfy.domain.org/watchdir
  --title-template TITLE_TEMPLATE
                        notification title template, use {VARIABLE} to replace the variables with the values.
                        available variables: FILE, FILE_PATH, FOLDER, SUBFOLDER_NAME, WATCH_FOLDER, RELATIVE_PATH
  --message-template MESSAGE_TEMPLATE
                        notification message template, use {VARIABLE} to replace the variables with the values.
                        available variables: FILE, FILE_PATH, FOLDER, SUBFOLDER_NAME, WATCH_FOLDER, RELATIVE_PATH
  --recursive           watch folder recursively
  --version             show program's version number and exit
```

## Usage

### With parameters

```bash
docker run -d \
  --name "dirrise_containername"                                   `# Create unique container name if you run multiple instances` \
  -v "/home/username/hostdir:/mnt/watchdir"                        `# Host:Container mapping, the container path can by anything but has to match with --folder-path` \
  -it ghcr.io/mrwyss/dirrise:latest python ./dirrise.py            `# No change reguired` \
  --folder-path "/mnt/watchdir"                                    `# Must match with container path above` \
  --file-extension ".txt"                                          `# File extension with dot` \
  --apprise-url 'ntfys://user:password@ntfy.domain.org/topic'      `# Regular apprise Url `
```

### With environment variables

```bash
docker run -it -d --name "dirrise_containername" \
-v "/home/username/hostdir:/mnt/watchdir" \
-e FOLDER_PATH=/mnt/watchdir \
-e FILE_EXTENSION=.txt \
-e APPRISE_URL=ntfys://user:password@ntfydomainorg/topic \
-e TITLE_TEMPLATE="New file" \
-e MESSAGE_TEMPLATE="New file {FILE} in {FOLDER}" \
-e RECURSIVE=true \
ghcr.io/mrwyss/dirrise:latest
```

### With Environment file

.env file:

```bash
FOLDER_PATH=/mnt/watchdir
FILE_EXTENSION=.txt
APPRISE_URL=ntfys://user:password@ntfydomainorg/topic
TITLE_TEMPLATE="New file"
MESSAGE_TEMPLATE="New file {FILE} in {FOLDER}"
RECURSIVE=true
```

run command:

```bash
docker run -it -d --name "dirrise_containername" \
-v "/home/username/hostdir:/mnt/watchdir" \
--env-file .env \
ghcr.io/mrwyss/dirrise:latest
```

### Templating

The message template can be used to create a custom message. The following variables are available:

MESSAGE_TEMPLATE

- **FILE** e.g. file.txt
- **FILE_PATH** e.g. /home/user/watchdir/subdir/file.txt
- **FOLDER** e.g. /home/user/watchdir/subdir
- **SUBFOLDER_NAME** e.g. subdir
- **WATCH_FOLDER** e.g. /home/user/watchdir
- **RELATIVE_PATH** e.g. subdir/file.txt

## Contributions

- please do, I'm happy to accept PRs.  
