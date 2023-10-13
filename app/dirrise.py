import os
import re
import sys
import logging
import argparse
from argparse import RawTextHelpFormatter
from apprise import AppriseConfig, Apprise
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

version = '0.0.3'

class AppriseNotifier:
    def __init__(self, apprise_url):

        self.apprise = Apprise()
        self.apprise.add(apprise_url)

    def notify(self, title, message):
        self.apprise.notify(title=title, body=message)

class FolderEventHandler(FileSystemEventHandler):
    def __init__(self, watch_folder, file_extension, logger, apprise_notifier, title_template, message_template):
        super().__init__()
        self.watch_folder = watch_folder
        self.file_extension = file_extension
        self.logger = logger
        self.apprise_notifier = apprise_notifier
        self.title_template = title_template
        self.message_template = message_template

    def on_created(self, event):
        if not event.is_directory:
            file_path = event.src_path                                  
            watch_folder = self.watch_folder                            
            relative_path = os.path.relpath(file_path, watch_folder)    
            file = os.path.basename(file_path)                     
            subfolder_name = os.path.dirname(relative_path)             
            folder = os.path.dirname(file_path)                         

            file_info = {
                "FILE_PATH": file_path,             #  e.g /home/user/watchdir/subdir/file.txt
                "FILE": file,                       #  e.g. file.txt
                "SUBFOLDER_NAME": subfolder_name,   #  e.g. subdir
                "FOLDER": folder,                   # e.g. /home/user/watchdir/subdir
                "WATCH_FOLDER": watch_folder,       # e.g. /home/user/watchdir
                "RELATIVE_PATH": relative_path      # e.g. subdir/file.txt
            }

            if file.endswith(self.file_extension):
                self.logger.info(f"Detected file {file} created in {folder}.")
                
                # Template variables

                formatted_message = self.message_template.format(**file_info)
                formatted_title = self.title_template.format(**file_info)

                self.logger.info(f"Notification title: {formatted_title}")
                self.logger.info(f"Notification message: {formatted_message}")

                # Send notification
                self.apprise_notifier.notify(message=formatted_message, title=formatted_title)           

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


    # region Parse arguments
    parser = argparse.ArgumentParser(description='Watch a folder for file creations and send notifications.', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--folder-path', type=validate_folder_path, help='path to the folder to watch, like /home/user/watchdir or C:\\Users\\user\\watchdir')
    parser.add_argument('--file-extension', type=str, help='file extension to watch, like .txt')
    parser.add_argument('--apprise-url', type=str, help='appriser URL like ntfys://user:password@ntfy.domain.org/watchdir')
    parser.add_argument('--title-template', type=str, help="notification title template, use {VARIABLE} to replace the variables with the values.\n"
                                                           "available variables: FILE, FILE_PATH, FOLDER, SUBFOLDER_NAME, WATCH_FOLDER, RELATIVE_PATH")
    parser.add_argument('--message-template', type=str, help="notification message template, use {VARIABLE} to replace the variables with the values.\n"
                                                             "available variables: FILE, FILE_PATH, FOLDER, SUBFOLDER_NAME, WATCH_FOLDER, RELATIVE_PATH")
    parser.add_argument('--recursive', action='store_true', default=argparse.SUPPRESS, help='watch folder recursively')
    parser.add_argument('--version', action='version', version=f'%(prog)s {version}')
    args = parser.parse_args()
    # endregion

    # region set and validate arguments
    # Folder path, raise error if not provided
    folder_path = args.folder_path or os.environ.get('FOLDER_PATH')
    if not os.path.exists(folder_path) or not os.path.isdir(folder_path): 
        exit("Error: Missing required parameter --folder-path or environment variable FOLDER_PATH.")    

    # File extension
    file_extension = args.file_extension or os.environ.get('FILE_EXTENSION')
    
    # Apprise URL
    apprise_url = args.apprise_url or os.environ.get('APPRISE_URL')

    # Notification title, if not set, use empty string
    title_template = args.title_template or os.environ.get('TITLE_TEMPLATE')
    if not title_template:
        title_template = ""
    
    # Message template
    message_template = args.message_template or os.environ.get('MESSAGE_TEMPLATE', 'New file "{FILE}" found in subfolder "{SUBFOLDER}" and folder "{FOLDER}" for the watch folder "{WATCH_FOLDER}"')
    recursive = args.recursive if hasattr(args, 'recursive') else os.environ.get('RECURSIVE', 'True').lower() == 'true'

    # Check if required parameters are provided
    if not all([folder_path, file_extension, apprise_url]):
        print("Error: Missing required parameters.")
        return
    # endregion

    # Print header
    script_file_name = os.path.basename(__file__)
    redacted_url = re.sub(r"(://)([^:]+):([^@]+)@", r"\1[REDACTED_USER]:[REDACTED_PASSWORD]@", apprise_url)  
    
    print(f"Running {script_file_name} version {version}\n")
    
    # Print command-line arguments
    print("Command-line arguments:")
    print(f"  Folder path:          {folder_path}")
    print(f"  File extension:       {file_extension}")
    print(f"  Apprise URL:          {redacted_url}")
    print(f"  Title template:       {title_template}")
    print(f"  Message template:     {message_template}")
    print(f"  Recursive:            {recursive}")

    # Apprise
    apprise_notifier = AppriseNotifier(apprise_url)

    # Start the observer
    watch_folder = os.path.join(folder_path)

    event_handler = FolderEventHandler(watch_folder, file_extension, logger, apprise_notifier, title_template, message_template)

    observer = Observer()
    observer.schedule(event_handler, path=watch_folder, recursive=recursive)

    try:
        observer.start()
        observer.join()
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main()
