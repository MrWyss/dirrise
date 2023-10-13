import os
import re
import sys
import logging
import argparse
from apprise import AppriseConfig, Apprise
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

version = '0.0.3'

class AppriseNotifier:
    def __init__(self, apprise_url, notification_title, notification_body):
        self.apprise = Apprise()
        self.apprise.add(apprise_url)
        self.notification_title = notification_title
        self.notification_body = notification_body

    def notify(self, title, message):
        self.apprise.notify(title=title, body=message)

class FolderEventHandler(FileSystemEventHandler):
    def __init__(self, watch_folder, file_extension, logger, apprise_notifier):
        super().__init__()
        self.watch_folder = watch_folder
        self.file_extension = file_extension
        self.logger = logger
        self.apprise_notifier = apprise_notifier
        self.message_template = apprise_notifier.notification_body
        self.message_title = apprise_notifier.notification_title

    def replace_variables(self, input_string, **variables):
        return input_string.format(**variables)

    def send_notification(self, file_name, folder, subfolder_name, watch_folder):
        formatted_message = self.replace_variables(self.message_template, FILE=file_name, FOLDER=folder, SUBFOLDER=subfolder_name, WATCHFOLDER=watch_folder)
        self.logger.info(f"Notification title: {self.message_title}")
        self.logger.info(f"Notification message: {formatted_message}")
        # Uncomment the next line to send notifications
        self.apprise_notifier.notify(message=formatted_message, title=self.message_title)

    def on_created(self, event):
        if not event.is_directory:
            file_path = event.src_path
            relative_path = os.path.relpath(file_path, self.watch_folder)
            file_name = os.path.basename(file_path)

            if file_name.endswith(self.file_extension):
                subfolder_name = os.path.dirname(relative_path)
                folder = os.path.dirname(file_path)
                self.logger.info(f"Detected file {file_name} created in {folder}.")
                self.send_notification(file_name=file_name, folder=folder, subfolder_name=subfolder_name, watch_folder=self.watch_folder)
                

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
    parser.add_argument('--folder-path', type=validate_folder_path, help='Path to the folder to watch, like /home/user/watchdir or C:\\Users\\user\\watchdir')
    parser.add_argument('--file-extension', type=str, help='File extension to watch, like .txt')
    parser.add_argument('--apprise-url', type=str, help='Appriser URL like ntfys://user:password@ntfy.domain.org/watchdir')
    parser.add_argument('--notification-title', type=str, help='Notification title')
    parser.add_argument('--message-template', type=str, help='Available variables: FILE, SUBFOLDER, FOLDER, WATCHFOLDER. Use {variable} to replace the variable with the value. Use \\{variable} to escape the variable.')
    parser.add_argument('--recursive', action='store_true', default=argparse.SUPPRESS, help='Watch folder recursively')
    parser.add_argument('--version', action='version', version=f'%(prog)s {version}')

    
    args = parser.parse_args()



    # Check if required parameters are provided; if not, use environment variables
    folder_path = args.folder_path or os.environ.get('FOLDER_PATH')
    
    if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
        exit("Error: Missing required parameter --folder-path or environment variable FOLDER_PATH.")    

    file_extension = args.file_extension or os.environ.get('FILE_EXTENSION')
        
    apprise_url = args.apprise_url or os.environ.get('APPRISE_URL')
    notification_title = args.notification_title or os.environ.get('NOTIFICATION_TITLE', 'New file detected')
    message_template = args.message_template or os.environ.get('MESSAGE_TEMPLATE', 'New file "{FILE}" found in subfolder "{SUBFOLDER}" and folder "{FOLDER}" for the watch folder "{WATCHFOLDER}"')
    recursive = args.recursive if hasattr(args, 'recursive') else os.environ.get('RECURSIVE', 'True').lower() == 'true'

    # Check if required parameters are provided
    if not all([folder_path, file_extension, apprise_url]):
        print("Error: Missing required parameters.")
        return

    script_file_name = os.path.basename(__file__)
    redacted_url = re.sub(r"(://)([^:]+):([^@]+)@", r"\1[REDACTED_USER]:[REDACTED_PASSWORD]@", apprise_url)
    
    # Print header
    print(f"Running {script_file_name} version {version}\n")
    
    # Print command-line arguments
    print("Command-line arguments:")
    print(f"  Folder path:          {folder_path}")
    print(f"  File extension:       {file_extension}")
    print(f"  Apprise URL:          {redacted_url}")
    print(f"  Notification title:   {notification_title}")
    print(f"  Message template:     {message_template}")
    print(f"  Recursive:            {recursive}")

    # Apprise
    apprise_notifier = AppriseNotifier(apprise_url, notification_title, message_template)

    # Start the observer
    watch_folder = os.path.join(folder_path)
    file_extension = file_extension

    event_handler = FolderEventHandler(watch_folder, file_extension, logger, apprise_notifier)

    observer = Observer()
    observer.schedule(event_handler, path=watch_folder, recursive=recursive)


    try:
        # Print out all the arguments
        observer.start()
        observer.join()
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main()
