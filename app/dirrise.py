import os
import re
import sys
import logging
import argparse
from argparse import RawTextHelpFormatter
from apprise import AppriseConfig, Apprise
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

version = '1.0.3'


class CustomArgumentParser(argparse.ArgumentParser):
    class _CustomHelpFormatter(argparse.ArgumentDefaultsHelpFormatter):
        def _get_help_string(self, action):
            help = super()._get_help_string(action)
            if action.dest != 'help':
                help += ' [env: {}]'.format(action.dest.upper())
            return help

    def __init__(self, *, formatter_class=_CustomHelpFormatter, **kwargs):
        super().__init__(formatter_class=formatter_class, **kwargs)

    def _add_action(self, action):
        action.default = os.environ.get(action.dest.upper(), action.default)
        return super()._add_action(action)


class AppriseNotifier:
    def __init__(self, apprise_url):
        self.apprise = Apprise()
        self.apprise.add(apprise_url)

    def notify(self, title, message):
        self.apprise.notify(title=title, body=message)


class Watcher:
    def __init__(self, event_handler, path, recursive):
        self.observer = Observer()
        self.event_handler = event_handler
        self.path = path
        self.recursive = recursive

    def start(self):
        self.observer.schedule(
            self.event_handler, path=self.path, recursive=self.recursive)
        try:
            self.observer.start()
            self.observer.join()
        except KeyboardInterrupt:
            self.observer.stop()
        self.observer.join()

    def stop(self):
        self.observer.stop()
        self.observer.join()


class FolderEventHandler(FileSystemEventHandler):
    def __init__(self, watch_folder, file_pattern, logger, apprise_notifier, title_template, message_template):
        super().__init__()
        self.watch_folder = watch_folder
        self.file_pattern = file_pattern
        self.logger = logger
        self.apprise_notifier = apprise_notifier
        self.title_template = title_template
        self.message_template = message_template

    def on_created(self, event):
        if not event.is_directory:
            file_path = event.src_path
            file_info = get_file_info(file_path, self.watch_folder)

            match = re.search(self.file_pattern, file_info['FILE'])
            if match:
                self.logger.info(
                    f"------------------ New match with pattern: {self.file_pattern} ------------------")
                # Color the matched file name
                colored_match = re.sub(match.group(
                    0), '\033[91m' + match.group(0) + '\033[0m', file_path)
                self.logger.info(f"Detected file        : {colored_match}.")

                # Template variables
                formatted_message = self.message_template.format(**file_info)
                formatted_title = self.title_template.format(**file_info)

                self.logger.info(f"Notification title   : {formatted_title}")
                self.logger.info(f"Notification message : {formatted_message}")

                # Send notification
                self.apprise_notifier.notify(
                    message=formatted_message, title=formatted_title)


def get_webdav_normalized(path):
    # Remove .DAV and __db
    replaced_path = re.sub(r'\.DAV|__db.', '', path)

    # Replace consecutive slashes with a single slash - linux
    replaced_path = re.sub(r'/{2,}', '/', replaced_path)

    # Replace double backslashes with a single backslash - windows
    replaced_path = re.sub(r'\\\\', '\\\\', replaced_path)

    return replaced_path


def get_file_info(file_path, watch_folder):
    # WebDAV normalize
    file_path = get_webdav_normalized(file_path)
    watch_folder = watch_folder
    relative_path = os.path.relpath(file_path, watch_folder)
    file = os.path.basename(file_path)
    subfolder_name = os.path.dirname(relative_path)
    folder = os.path.dirname(file_path)
    file_info = {
        "FILE_PATH": file_path,             # e.g /home/user/watchdir/subdir/file.txt
        "FILE": file,                       # e.g. file.txt
        "SUBFOLDER_NAME": subfolder_name,   # e.g. subdir
        "FOLDER": folder,                   # e.g. /home/user/watchdir/subdir
        "WATCH_FOLDER": watch_folder,       # e.g. /home/user/watchdir
        "RELATIVE_PATH": relative_path      # e.g. subdir/file.txt
    }
    return file_info


def setup_logging():
    logging.basicConfig(
        stream=sys.stdout,
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    return logging.getLogger()


def validate_folder_path(value):
    if not os.path.exists(value) or not os.path.isdir(value):
        raise argparse.ArgumentTypeError(
            f"The specified folder {value} does not exist or is not a directory.")
    return value


def main():
    logger = setup_logging()

    # region Parse arguments
    parser = CustomArgumentParser(
        description='Watch a folder for file creations and send notifications.', formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('-f', '--folder-path',
                        required=False,
                        type=validate_folder_path,
                        help="path to the folder to watch.\n"
                             "Can also be set with environment Variable FOLDER_PATH\n"
                             "  e.g. /home/user/watchdir or C:\\Users\\user\\watchdir\n")

    parser.add_argument('-p', '--file-pattern',
                        required=False,
                        type=str,
                        help="regular expression pattern to match file names\n"
                             "can also be set with environment Variable FILE_PATTERN\n"
                             "  e.g. \\.txt$")

    parser.add_argument('-u', '--apprise-url',
                        required=False,
                        type=str,
                        help="apprise url\n"
                             "can also be set with environment Variable APPRISE_URL\n"
                             "  e.g. ntfys://user:password@ntfy.domain.org/watchdir")

    parser.add_argument('-t', '--title-template',
                        required=False,
                        default="",
                        type=str,
                        help="notification title template\n"
                             "can also be set with environment Variable TITLE_TEMPLATE\n"
                             "  e.g. New file {FILE} found in subfolder {SUBFOLDER_NAME} and folder {FOLDER} for the watch folder {WATCH_FOLDER}\n"
                             "available variables: FILE, FILE_PATH, FOLDER, SUBFOLDER_NAME, WATCH_FOLDER, RELATIVE_PATH")

    parser.add_argument('-m', '--message-template',
                        required=False,
                        default='New file "{FILE}" found in subfolder "{SUBFOLDER_NAME}" and folder "{FOLDER}" for the watch folder "{WATCH_FOLDER}"',
                        type=str,
                        help="notification message template\n"
                             "can also be set with environment Variable MESSAGE_TEMPLATE\n"
                             "  e.g. New file {FILE} found in subfolder {SUBFOLDER_NAME} and folder {FOLDER} for the watch folder {WATCH_FOLDER}\n"
                             "available variables: FILE, FILE_PATH, FOLDER, SUBFOLDER_NAME, WATCH_FOLDER, RELATIVE_PATH")
    parser.add_argument('-r', '--recursive',
                        action='store_true',
                        help="watch folder recursively\n"
                             "can also be set with environment Variable RECURSIVE\n"
                             "  e.g. True or False")

    parser.add_argument('-v', '--version', action='version',
                        version=f'%(prog)s {version}')
    args = parser.parse_args()

    # Check if required parameters are set, if not print help
    required_params = ['--folder-path', '--file-pattern', '--apprise-url']
    missing_params = [param for param in required_params if getattr(
        args, param.replace('--', '').replace('-', '_')) is None]
    if missing_params:
        print("Missing required parameters:")
        for param in missing_params:
            print(parser._option_string_actions[param].option_strings)
            print(parser._option_string_actions[param].help, end='\n\n')
        sys.exit(1)
    # endregion

    # Check if args.recursive is a string and convert to boolean
    if isinstance(args.recursive, str):
        args.recursive = args.recursive.lower() == 'true'

    # Print header
    script_file_name = os.path.basename(__file__)
    redacted_url = re.sub(
        r"(://)([^:]+):([^@]+)@", r"\1[REDACTED_USER]:[REDACTED_PASSWORD]@", args.apprise_url)

    print(f"Running {script_file_name} version {version}\n")

    # Print command-line arguments
    print("Command-line arguments:")
    print(f"  Folder path:          {args.folder_path}")
    print(f"  File pattern:         {args.file_pattern}")
    print(f"  Apprise URL:          {redacted_url}")
    print(f"  Title template:       {args.title_template}")
    print(f"  Message template:     {args.message_template}")
    print(f"  Recursive:            {args.recursive}")

    # Apprise
    apprise_notifier = AppriseNotifier(args.apprise_url)

    # Start the observer
    watch_folder = os.path.join(args.folder_path)

    event_handler = FolderEventHandler(
        watch_folder, args.file_pattern, logger, apprise_notifier, args.title_template, args.message_template)

    watcher = Watcher(event_handler, path=watch_folder,
                      recursive=args.recursive)
    watcher.start()


if __name__ == "__main__":
    main()
