import os
import re
import sys
import logging
import argparse
from apprise import AppriseConfig, Apprise
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class AppriseNotifier:
    def __init__(self, apprise_url, notification_title, notification_body):
        self.apprise = Apprise()
        self.apprise.add(apprise_url)
        self.notification_title = notification_title
        self.notification_body = notification_body

    def notify(self, title, message):
        self.apprise.notify(title=title, body=message)

class FolderEventHandler(FileSystemEventHandler):
    def __init__(self, folder_path, file_extension, message_template, logger, apprise_notifier):
        super().__init__()
        self.folder_path = folder_path
        self.file_extension = file_extension
        self.message_template = message_template
        self.logger = logger
        self.apprise_notifier = apprise_notifier

    def replace_variables(self, input_string, **variables):
        return input_string.format(**variables)

    def send_notification(self, file_name, folder, subfolder_name, watch_folder):
        result = self.replace_variables(self.message_template, FILE=file_name, FOLDER=folder, SUBFOLDER=subfolder_name, WATCHFOLDER=watch_folder)
        self.logger.info(result)
        # Uncomment the next line to send notifications
        self.apprise_notifier.notify(result, self.apprise_notifier.notification_title)

    def on_created(self, event):
        if not event.is_directory:
            file_path = event.src_path
            relative_path = os.path.relpath(file_path, self.folder_path)
            file_name = os.path.basename(file_path)

            if file_name.endswith(self.file_extension):
                subfolder_name = os.path.dirname(relative_path)
                folder = os.path.dirname(file_path)
                self.send_notification(file_name=file_name, folder=folder, subfolder_name=subfolder_name, watch_folder=self.folder_path)

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
        raise argparse.ArgumentTypeError(f"The specified folder {value} does not exist or is not a directory.")
    return value


def main():
    logger = setup_logging()

    # Parse arguments
    parser = argparse.ArgumentParser(description='Watch a folder for file creations and send notifications.')
    parser.add_argument('--folder-path', type=validate_folder_path, required=True, help='Path to the folder to watch, like /home/user/watchdir or C:\\Users\\user\\watchdir')
    parser.add_argument('--file-extension', type=str, required=True, help='File extension to watch, like .txt')
    parser.add_argument('--apprise-url', type=str, required=True, help='Appriser URL like ntfys://user:password@ntfy.domain.org/watchdir')
    parser.add_argument('--notification-title', type=str, default='New file detected', help='Notification title')
    parser.add_argument('--message-template', type=str, default='New file "{FILE}" found in subfolder "{SUBFOLDER}" and folder "{FOLDER}" for the watch folder "{WATCHFOLDER}', help='Available variables: FILE, SUBFOLDER, FOLDER, WATCHFOLDER. Use {variable} to replace the variable with the value. Use \\{variable} to escape the variable. Use {{variable}} to use the variable as a m')
    parser.add_argument('--recursive', action='store_true', help='Watch folder recursively', default=True)
    parser.add_argument('--version', action='version', version='%(prog)s 0.0.1')
    args = parser.parse_args()


    # Apprise
    apprise_notifier = AppriseNotifier(args.apprise_url, args.notification_title, args.message_template)

    # Start the observer
    folder_path = os.path.join(args.folder_path)
    file_extension = args.file_extension
    message_template = args.message_template

    event_handler = FolderEventHandler(folder_path, file_extension, message_template, logger, apprise_notifier)

    observer = Observer()
    observer.schedule(event_handler, path=folder_path, recursive=args.recursive)

    redacted_url = re.sub(r"(://)([^:]+):([^@]+)@", r"\1[REDACTED_USER]:[REDACTED_PASSWORD]@", args.apprise_url)

    try:
        # Print out all the arguments
        print("Command-line arguments:")
        for arg, value in vars(args).items():
            if arg == 'apprise_url':
                value = redacted_url
            print(f"  {arg.replace('_', '-')}:", value)
        observer.start()
        observer.join()
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main()
