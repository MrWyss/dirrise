# dirrise

[![Publish Docker image](https://github.com/MrWyss/dirrise/actions/workflows/publish_docker_image.yml/badge.svg)](https://github.com/MrWyss/dirrise/actions/workflows/publish_docker_image.yml)
[![Image Tag](https://ghcr-badge.egpl.dev/mrwyss/dirrise/tags?color=%2344cc11&ignore=&n=3&label=image+tags&trim=)](https://github.com/MrWyss/dirrise/pkgs/container/dirrise)
[![Image Size](https://ghcr-badge.egpl.dev/mrwyss/dirrise/size?color=%2344cc11&tag=latest&label=image+size&trim=)](https://github.com/MrWyss/dirrise/pkgs/container/dirrise)

Watches a folder for new files with a given extension and sends a notification via apprise.

## Help

```text
usage: dirrise.py [-h] --folder-path FOLDER_PATH --file-extension FILE_EXTENSION --apprise-url APPRISE_URL [--notification-title NOTIFICATION_TITLE] [--message-template MESSAGE_TEMPLATE] [--recursive] [--version]

Watch a folder for file creations and send notifications.

options:
  -h, --help            show this help message and exit
  --folder-path FOLDER_PATH
                        Path to the folder to watch, like /home/user/watchdir or C:\Users\user\watchdir
  --file-extension FILE_EXTENSION
                        File extension to watch, like .txt
  --apprise-url APPRISE_URL
                        Appriser URL like ntfys://user:password@ntfy.domain.org/watchdir
  --notification-title NOTIFICATION_TITLE
                        Notification title
  --message-template MESSAGE_TEMPLATE
                        Available variables: FILE, SUBFOLDER, FOLDER, WATCHFOLDER. Use {variable} to replace the variable with the value. Use \{variable} to escape the variable. Use {{variable}} to use the variable as a m
  --recursive           Watch folder recursively
  --version             show program's version number and exit
```

## Usage

```bash
docker run -d \
  --name "dirrise_containername"                                   `# Create unique container name if you run multiple instances` \
  -v "/home/username/hostdir:/mnt/watchdir"                        `# Host:Container mapping, the container path can by anything but has to match with --folder-path` \
  -it ghcr.io/mrwyss/dirrise:latest python ./dirrise.py            `# No change reguired` \
  --folder-path "/mnt/watchdir"                                    `# Must match with container path above` \
  --file-extension ".txt"                                          `# File extension with dot` \
  --apprise-url 'ntfys://user:password@ntfy.domain.org/topic'      `# Regular apprise Url `
```
