# Modrinth Collection Downloader

Script to download and update mods from a Modrinth Collection using a graphical user interface (GUI).

## Requirements
- If you are using the executable from the release files, Python is not required.
- If you are running the script directly, Python should be installed: [Download Python](https://www.python.org/downloads/)

## How to use

### Graphical User Interface

The script provides a graphical user interface (GUI) for ease of use. When you run the executable or `main.py`, a window will open where you can input the required parameters.

#### GUI Features:

- **Collection ID**: The ID of the Modrinth collection to download.
- **Minecraft Version**: The version of Minecraft (e.g., "1.21").
- **Loader**: The mod loader to use (e.g., "fabric", "forge", "quilt").
- **Directory**: The directory to download mods to (default is "mods").
- **Update existing mods**: A checkbox to indicate whether to update existing mods.

### Running the Program

#### Using the Executable

1. Download the executable from the [releases page](https://github.com/emc00073/modrinth-collection-downloader-easily-accessible/releases).
2. Run the executable file.

#### Using Python Script

To run the script, simply execute:

```sh
python main.py
```

This will open the GUI where you can input the required parameters and start the download process.

### Logging

The script logs its activities to a file named `modrinth_downloader.log`. You can view the log file to see detailed information about the download process, including any errors encountered.

To open the log file from the GUI, click the "Open Log" button that appears after the download process completes.

### Last Executed Arguments

The script saves the last executed arguments to a file named `last_args.json`. When you run the script again, it will pre-fill the input fields with the last used values.

### Directory Structure

The directory structure of the project is as follows:

```
.gitignore
last_args.json
main.py
modrinth_downloader.log
mods/
    bettercommandblockui-0.5.2a-1.21.8iQcgjQ2.jar
    carpet-extra-1.21-1.4.148.VX3TgwQh.jar
    carpet-tis-addition-v1.65.0-mc1.21.1.jE0SjGuf.jar
    dynamic-fps-3.7.7+minecraft-1.21.0-fabric.LQ3K71Q1.jar
    entityculling-fabric-1.7.2-mc1.21.NNAgCjsB.jar
    fabric-api-0.102.0+1.21.P7dR8mSH.jar
    fabric-carpet-1.21-1.4.147+v240613.TQTTVgYE.jar
    freecam-fabric-modrinth-1.3.0+mc1.21.XeEZ3fK2.jar
    iris-fabric-1.8.1+mc1.21.1.YL57xq9U.jar
    ...
README.md
```

### Example Log Entries

Here are some example log entries from `modrinth_downloader.log`:

```log
2024-12-25 21:17:21,291 - INFO - ==================================================
2024-12-25 21:17:21,291 - INFO - Execution Date: 2024-12-25 21:17:21
2024-12-25 21:17:21,291 - INFO - ==================================================
2024-12-25 21:17:26,655 - INFO - DOWNLOADING: bettercommandblockui-0.5.2-1.20.jar (Better Command Block UI)
2024-12-25 21:17:26,666 - ERROR - No version found for 1u6JkXh5 (WorldEdit) with MC_VERSION=1.20 and LOADER=fabric
2024-12-25 21:17:26,691 - INFO - DOWNLOADING: seethroughlava-4.0-1.20.jar (See Through Water/Lava)
...
2024-12-25 21:18:32,869 - INFO - --------------------------------------------------
2024-12-25 21:18:32,869 - INFO - Nº of mods downloaded: 19 / Nº of total mods: 22
2024-12-25 21:18:32,869 - INFO - --------------------------------------------------
```

### Notes

- Ensure that the `mods` directory exists or specify a different directory in the GUI.
- The script will attempt to download and update mods based on the provided collection ID, Minecraft version, and loader.
- If the "Update existing mods" checkbox is selected, the script will delete existing mods in the specified directory before downloading the new versions.

### Troubleshooting

If you encounter any issues, please check the `modrinth_downloader.log` file for detailed error messages and information about the download process.
