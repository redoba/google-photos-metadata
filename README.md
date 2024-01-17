# Google Photos Metadata Fixer
## Overview
When transferring photos from Google Photos, missing creation date metadata can disrupt the order when uploaded elsewhere. This script addresses the issue by assigning consistent creation dates to all photos, ensuring proper sorting, especially when moved to platforms like OneDrive.

## Prerequisites

- Python installed
- ExifTool installed

## Usage
Download Google Photos in a zip file, selecting albums organized by dates (e.g., "Photos from 2015").
Place the script in the same location as the folders.
Run the script with `python3 fixmetadata.py`.

## Functionality
The script attempts to obtain the creation date from various metadata sources in the photo or video, including:

- CreateDate
- ModifyDate
- DateTimeOriginal
- TrackCreateDate
- TrackModifyDate
- MediaCreateDate
- MediaModifyDate
- SubSecCreateDate
- SubSecDateTimeOriginal
- SubSecModifyDate

It also searches for dates in the Google Photos JSON file, including:

- creationTime.timestamp
- photoTakenTime.timestamp

Additionally, it reads the date from the folder name (e.g., "Photos from 2015").

The script compares these dates and assigns the earliest one. If no metadata is available, it assumes the date is from the folder, setting it to the last day of that year.

## Output
The script generates three files:

- output.txt: Displays the process for each photo, showing found data and the updated date.
- output_fails.txt: Lists files with processing failures. Review each one individually.
- output_success.txt: Lists files processed successfully.

The script filters files with extensions: '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.mp4', '.3gp'. Add more extensions if needed.
