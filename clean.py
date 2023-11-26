import os
import glob
import shutil
import datetime

# Define the parent directories where your CSV and JSON folders are stored
csv_parent_directory = "./collegeCourseData/csvFiles/"
json_parent_directory = "./collegeCourseData/jsonFiles/"


# Function to check if a file is older than 15 minutes
def is_file_old(file_path):
    now = datetime.datetime.now()
    file_creation_time = datetime.datetime.fromtimestamp(os.path.getctime(file_path))
    time_difference = now - file_creation_time
    return time_difference.total_seconds() > 900  # 900 seconds = 15 minutes


# Function to clean up files in a directory
def clean_directory(directory_path, file_extension):
    # Get a list of all files with the specified extension in the directory
    files = glob.glob(os.path.join(directory_path, f"*.{file_extension}"))

    if not files:
        print(f"No {file_extension.upper()} files found in {directory_path}.")
    else:
        # Sort the files by modification time (oldest first)
        files.sort(key=os.path.getmtime)

        # Keep the most recent file and delete the rest if they are older than 15 minutes
        for file_path in files[:-1]:
            if is_file_old(file_path):
                print(f"Deleting old {file_extension.upper()} file: {file_path}")
                os.remove(file_path)
            else:
                print(f"Keeping {file_extension.upper()} file: {file_path}")

        # Run your scraping script here
        # Replace the following line with your actual scraping logic
        print(f"Running scraping script for {directory_path}...")

        # Add your scraping logic here
        # For example, you can call another script or function to perform the scraping
        # Replace the following line with your actual scraping logic
        # os.system("python scrape.py")


# Process CSV files
for csv_directory in os.listdir(csv_parent_directory):
    csv_directory_path = os.path.join(csv_parent_directory, csv_directory)

    # Check if it's a directory
    if os.path.isdir(csv_directory_path):
        clean_directory(csv_directory_path, "csv")

# Process JSON files
for json_directory in os.listdir(json_parent_directory):
    json_directory_path = os.path.join(json_parent_directory, json_directory)

    # Check if it's a directory
    if os.path.isdir(json_directory_path):
        clean_directory(json_directory_path, "json")
