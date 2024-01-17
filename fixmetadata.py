import os,sys
import json
import subprocess
import datetime

# Guarda el objeto original de stdout
original_stdout = sys.stdout
success_output = open('output_success.txt', 'w')
fail_output = open('output_fails.txt', 'w')
    
def write_success(file_name):
    success_output.write(file_name + "\n")

def write_fail(file_name, exception):
    fail_output.write(file_name + ": " + str(exception) + "\n")

def get_time_from_jsonfile(full_file_path):
    # JSON file of Google Photos
    timestamp = None
    json_file = f"{full_file_path}.json"
    try:
        with open(json_file, 'r') as json_file:
            json_data = json.load(json_file)
            photo_taken_time = json_data.get('photoTakenTime', {}).get('timestamp')
            creation_time = json_data.get('creationTime', {}).get('timestamp')
            
            # Convertir los timestamps a enteros
            photo_taken_time = int(photo_taken_time) if photo_taken_time else None
            creation_time = int(creation_time) if creation_time else None

            if photo_taken_time and creation_time:
                timestamp = min(photo_taken_time, creation_time)
            elif photo_taken_time:
                timestamp = photo_taken_time
            elif creation_time:
                timestamp = creation_time

    except (json.JSONDecodeError, FileNotFoundError):
        return None

    return timestamp

def get_metadata_from_file(full_file_path):
    # Metadata from image/video file
    command = ["exiftool", "-json", full_file_path]
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    exif_json = result.stdout
    exif_data = json.loads(exif_json)[0]
    return exif_data

def set_metadata(full_file_path, datetime):
    #print("timestamp: ", datetime)
    fecha_str = datetime.strftime("%Y:%m:%d %H:%M:%S%z")
    
    command = ["exiftool",
        "-overwrite_original",
        "-CreateDate=" + fecha_str, 
        "-ModifyDate=" + fecha_str, 
        "-DateTimeOriginal=" + fecha_str, 
        #"-MediaCreateDate=" + new_createdate_value, 
        #"-MediaModifyDate=" + new_createdate_value, 
        #"-TrackCreateDate=" + new_createdate_value, 
        #"-TrackModifyDate=" + new_createdate_value, 
        full_file_path
    ]
    subprocess.run(command, check=True)
    print(f"UPDATE: {fecha_str}")

def read_date(date):
    # Read date from string with differente patterns
    try:
        # 2024:01:16 14:53:19-03:00
        return datetime.datetime.strptime(date, "%Y:%m:%d %H:%M:%S%z").replace(tzinfo=None)
    except ValueError:
        try:
            # 1990:01:16 12:00:00
            return datetime.datetime.strptime(date, "%Y:%m:%d %H:%M:%S")
        except ValueError:
            try:
                # 2023:08:14 18:06:41.290
                return datetime.datetime.strptime(date, "%Y:%m:%d %H:%M:%S.%f")
            except ValueError:
                try:
                    # 2023:08:14 18:06:41.290-03:00
                    return datetime.datetime.strptime(date, "%Y:%m:%d %H:%M:%S.%f%z").replace(tzinfo=None)
                except:
                    return None

def min_date(full_file_path, exif_data, year):
    values = []
    
    # Get Date from Json Metadata (google)
    json_timestamp = get_time_from_jsonfile(full_file_path)
    json_date = datetime.datetime.fromtimestamp(json_timestamp) if json_timestamp is not None else None
    print(f"jsonvalue: {json_timestamp} {json_date}")
    if json_date: values.append(json_date)
    
    # Get Min Value of Year
    year_day = datetime.datetime(year, 12, 31, 23, 59, 59)
    print(f"year day: {year_day}")
    values.append(year_day)
    
    # Get Date from Exif Metadata (camera)
    fields = ["CreateDate","ModifyDate","DateTimeOriginal","TrackCreateDate","TrackModifyDate",
              "MediaCreateDate","MediaModifyDate","SubSecCreateDate","SubSecDateTimeOriginal","SubSecModifyDate"]
    for field in fields:
        print(field, exif_data.get(field))
        if exif_data.get(field): 
            val = read_date(exif_data.get(field))
            if val is not None:
                values.append(val)

    #print(values)
    return min(values)

def get_folder_year(folder):
    # Extract the last 4 characters from the string 'folder,' and if it is an integer, then return that integer (year)
    try:
        year = int(folder[-4:])
        return year
    except ValueError:
        return None

def process_file(full_file_path,year):
    # Get metadata from the file
    exif_data = get_metadata_from_file(full_file_path)
    minvalue = min_date(full_file_path, exif_data,year)
    set_metadata(full_file_path, minvalue)

##### MAIN PROGRAM
title = "#" * 100
with open('output.txt', 'w') as file:
    sys.stdout = file

    current_directory = os.getcwd()
    folders = [name for name in os.listdir(current_directory) if os.path.isdir(os.path.join(current_directory, name))]
    folders = sorted(folders)

    for folder in folders:
        year = get_folder_year(folder)
        print(f"\n{title}\nProcessing folder:{folder} (year:{year})\n")
        full_folder_path = os.path.join(current_directory, folder)
        
        files = os.listdir(full_folder_path)
        files = [file for file in files if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.mp4', '.3gp')) and not file.endswith('.json')]
        files = sorted(files)
        for file in files:
            print("\nProcessing file: ", file)
            full_file_path = os.path.join(full_folder_path, file)
            try:
                process_file(full_file_path,year)
                write_success(full_file_path)
            except Exception as e:
                write_fail(full_file_path, e)
            
        #files = os.listdir(full_folder_path)
        #files = [file for file in files if file.endswith(('.json', '.DS_Store'))]
        #for file in files:
        #    os.remove(os.path.join(full_folder_path, file))
    
    print("END!")
        
        
