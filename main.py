import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import os
import re
import logging
from urllib import request, error
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import webbrowser
from datetime import datetime

class ModrinthClient:

    def __init__(self):
        self.base_url = "https://api.modrinth.com"

    def get(self, url):
        try:
            with request.urlopen(self.base_url + url) as response:
                return json.loads(response.read())
        except error.URLError as e:
            logging.error(f"Network error: {e}")
            return None

    def download_file(self, url, filename):
        try:
            request.urlretrieve(url, filename)
        except error.URLError as e:
            logging.error(f"Failed to download file: {e}")

    def get_mod_version(self, mod_id):
        return self.get(f"/v2/project/{mod_id}/version")

    def get_collection(self, collection_id):
        return self.get(f"/v3/collection/{collection_id}")

    def get_mod_name(self, mod_id):
        mod_details = self.get(f"/v2/project/{mod_id}")
        if mod_details:
            return mod_details.get("title", "Unknown Mod")
        return "Unknown Mod"


modrinth_client = ModrinthClient()


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Download and update mods from a Modrinth collection."
    )
    parser.add_argument(
        "-c",
        "--collection",
        required=True,
        help="ID of the collection to download. Can be obtained from the collection URL (for https://modrinth.com/collection/5OBQuutT collection_id is 5OBQuutT).",
    )
    parser.add_argument(
        "-v", "--version", required=True, help='Minecraft version ("1.20.4", "1.21").'
    )
    parser.add_argument(
        "-l",
        "--loader",
        required=True,
        help='Loader to use ("fabric", "forge", "quilt" etc).',
    )
    parser.add_argument(
        "-d",
        "--directory",
        default="./mods",
        help='Directory to download mods to. Default: "mods"',
    )
    parser.add_argument(
        "-u",
        "--update",
        default=False,
        action="store_true",
        help="Download and update existing mods. Default: false",
    )
    return parser.parse_args()


def get_existing_mods(directory) -> list[dict]:
    file_names = os.listdir(directory)
    return [
        {"id": file_name.split(".")[-2], "filename": file_name}
        for file_name in file_names
    ]


def get_latest_version(mod_id, version, loader):
    mod_versions_data = modrinth_client.get_mod_version(mod_id)
    mod_name = modrinth_client.get_mod_name(mod_id)
    if not mod_versions_data:
        logging.error(f"No version found for {mod_id} ({mod_name}) with MC_VERSION={version} and LOADER={loader}")
        return None

    mod_version_to_download = next(
        (
            mod_version
            for mod_version in mod_versions_data
            if version in mod_version["game_versions"]
            and loader in mod_version["loaders"]
        ),
        None,
    )
    return mod_version_to_download


def download_mod(mod_id, version, loader, directory, update, existing_mods=[]):
    try:
        mod_name = modrinth_client.get_mod_name(mod_id)
        existing_mod = next((mod for mod in existing_mods if mod["id"] == mod_id), None)

        if not update and existing_mod:
            logging.info(f"{mod_id} ({mod_name}) already exists, skipping...")
            return False

        latest_mod = get_latest_version(mod_id, version, loader)
        if not latest_mod:
            logging.error(
                f"No version found for {mod_id} ({mod_name}) with MC_VERSION={version} and LOADER={loader}"
            )
            return False

        file_to_download: dict | None = next(
            (file for file in latest_mod["files"] if file["primary"] == True), None
        )
        if not file_to_download:
            logging.error(f"Couldn't find a file to download for {mod_id} ({mod_name})")
            return False
        filename: str = file_to_download["filename"]
        filename_with_version = f"{mod_name}-{version}"
        if loader == "iris":
            filename_with_version += ".zip"
        else:
            filename_with_version += ".jar"

        if existing_mod and existing_mod["filename"] == filename_with_version:
            logging.info(f"{filename_with_version} latest version already exists.")
            return False

        logging.info(
            f"{'UPDATING' if existing_mod else 'DOWNLOADING'}: {file_to_download['filename']} ({mod_name})"
        )
        modrinth_client.download_file(
            file_to_download["url"], f"{directory}/{filename_with_version}"
        )

        if existing_mod:
            logging.info(f"REMOVING previous version: {existing_mod['filename']} ({mod_name})")
            os.remove(f"{directory}/{existing_mod['filename']}")
        return True
    except Exception as e:
        logging.error(f"Failed to download {mod_id} ({mod_name}): {e}")
        return False


def main(collection, version, loader, directory, update):
    if directory:
        if not os.path.exists(directory):
            os.mkdir(directory)

    if update:
        # Delete all .jar files in the directory
        for file_name in os.listdir(directory):
            if file_name.endswith(".jar"):
                os.remove(os.path.join(directory, file_name))

    collection_details = modrinth_client.get_collection(collection)
    if not collection_details:
        logging.error(f"Collection id={collection} not found")
        return
    mods: str = collection_details["projects"]
    logging.info("Mods in collection: ", mods)
    existing_mods = get_existing_mods(directory)

    downloaded_mods = 0
    with ThreadPoolExecutor(max_workers=5) as executor:
        for result in executor.map(lambda mod_id: download_mod(mod_id, version, loader, directory, update, existing_mods), mods):
            if result:
                downloaded_mods += 1

    # Log the summary
    logging.info("-" * 50)
    logging.info(f"Nº of mods downloaded: {downloaded_mods} / Nº of total mods: {len(mods)}")
    logging.info("-" * 50)

    # Show the button to open the log file
    open_log_button.grid(column=2, row=5, padx=10, pady=10)


def run_from_gui():
    collection = collection_entry.get()
    version = version_entry.get()
    loader = loader_var.get()
    directory = directory_entry.get()
    update = update_var.get()

    # Validate collection
    if not collection:
        messagebox.showerror("Error", "Collection ID is required.")
        return

    # Validate version
    if not re.match(r"^1\.\d{1,2}(\.\d{1,2})?$", version):
        messagebox.showerror("Error", "Invalid Minecraft version format. Use 1.X.X, 1.XX.X, or 1.XX.")
        return

    # Validate directory
    if not os.path.exists(directory):
        os.makedirs(directory)

    collection_details = modrinth_client.get_collection(collection)
    if not collection_details:
        messagebox.showerror("Error", f"Collection id={collection} not found")
        return

    # Save last executable args
    last_args = {
        "collection": collection,
        "version": version,
        "loader": loader,
        "directory": directory,
        "update": update
    }
    with open("last_args.json", "w") as f:
        json.dump(last_args, f)

    main(collection, version, loader, directory, update)


def select_directory():
    directory = filedialog.askdirectory()
    if directory:
        directory_entry.delete(0, tk.END)
        directory_entry.insert(0, directory)


def open_log_file():
    log_file_path = "modrinth_downloader.log"
    webbrowser.open(log_file_path)


# Setup logging
logging.basicConfig(filename='modrinth_downloader.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filemode='w')

# Add date line at the beginning of the log file
logging.info("=" * 50)
logging.info(f"Execution Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
logging.info("=" * 50)

# GUI setup
root = tk.Tk()
root.resizable(False, False)
root.title("Modrinth Collection Downloader")

ttk.Label(root, text="Collection ID (required):").grid(column=0, row=0, padx=10, pady=5)
collection_entry = ttk.Entry(root)
collection_entry.grid(column=1, row=0, padx=10, pady=5)

ttk.Label(root, text="Minecraft Version (required):").grid(column=0, row=1, padx=10, pady=5)
version_entry = ttk.Entry(root)
version_entry.grid(column=1, row=1, padx=10, pady=5)

ttk.Label(root, text="Loader (required):").grid(column=0, row=2, padx=10, pady=5)
loader_var = tk.StringVar()
loader_menu = ttk.Combobox(root, textvariable=loader_var, width=17)
loader_menu['values'] = ("fabric", "forge", "quilt", "iris")
loader_menu.grid(column=1, row=2, padx=10, pady=5)
loader_menu.current(0)

ttk.Label(root, text="Directory (optional):").grid(column=0, row=3, padx=10, pady=5)
directory_entry = ttk.Entry(root)
directory_entry.grid(column=1, row=3, padx=10, pady=5)
ttk.Button(root, text="Browse", command=select_directory).grid(column=2, row=3, padx=10, pady=5)

update_var = tk.BooleanVar()
ttk.Checkbutton(root, text="Update existing mods", variable=update_var).grid(column=0, row=4, columnspan=2, padx=10, pady=5)

ttk.Button(root, text="Run", command=run_from_gui).grid(column=0, row=5, columnspan=3, padx=10, pady=10)

open_log_button = ttk.Button(root, text="Open Log", command=open_log_file)
open_log_button.grid_forget()  # Hide the button initially

# Load last executable args
if os.path.exists("last_args.json"):
    with open("last_args.json", "r") as f:
        last_args = json.load(f)
        collection_entry.insert(0, last_args.get("collection", ""))
        version_entry.insert(0, last_args.get("version", ""))
        loader_var.set(last_args.get("loader", "fabric"))
        directory_entry.insert(0, last_args.get("directory", "./mods"))
        update_var.set(last_args.get("update", False))

root.mainloop()
