# Python Script to go into "submissions.zip" downloaded from Canvas and pull out the DataLogger files from each of the submissions.  
# The script also checks for failed submissions and moves them into a "failed_submissions" folder.

# This script was written usng ChatGPT.

# February 13, 2024

import os
import csv
import re
import shutil
import zipfile

# Function to read CanvasID_studentNumber_key.csv and create a mapping dictionary
def read_key_csv(csv_file):
    key_mapping = {}
    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header
        for row in reader:
            canvas_id = row[1]  # Second column contains Canvas ID
            student_number = row[2]  # Third column contains Student Number
            key_mapping[canvas_id] = student_number
    return key_mapping

# Function to extract PHYS121_DataLogger.txt from a zip file
def extract_data_logger(zip_file_path, key_mapping, passed_submissions_folder):
    zip_file_name = os.path.basename(zip_file_path)
    match = re.search(r'_(\d{6,7})_', zip_file_name)
    if match:
        canvas_id = match.group(1)
        student_number = key_mapping.get(canvas_id)
        if student_number:
            try:
                with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                    # Check if PHYS121_DataLogger.txt exists in the zip file
                    if 'PHYS121_DataLogger.txt' in zip_ref.namelist():
                        extracted_file_name = f"{student_number}_PHYS121_DataLogger.txt"
                        zip_ref.extract('PHYS121_DataLogger.txt', path="temp_extracted_folder")
                        os.rename(os.path.join("temp_extracted_folder", 'PHYS121_DataLogger.txt'), os.path.join("temp_extracted_folder", extracted_file_name))
                        print(f"Extracted PHYS121_DataLogger.txt from {zip_file_name} as {extracted_file_name}")
                        shutil.move(zip_file_path, os.path.join(passed_submissions_folder, zip_file_name))  # Move the zip file to passed_submissions_folder
                    else:
                        print(f"PHYS121_DataLogger.txt not found in {zip_file_name}")
            except Exception as e:
                print(f"Error occurred while processing {zip_file_name}: {e}")
        else:
            print(f"No matching student number found for Canvas ID {canvas_id}")
    else:
        print(f"No 6 or 7 digit number found in the name of {zip_file_name}")

# Function to process all zip files in a directory
def process_zip_files(directory, key_mapping):
    failed_submission_folder = "failed_submissions"
    passed_submissions_folder = "passed_submissions"
    os.makedirs(failed_submission_folder, exist_ok=True)
    os.makedirs(passed_submissions_folder, exist_ok=True)
    for file_name in os.listdir(directory):
        file_path = os.path.join(directory, file_name)
        if zipfile.is_zipfile(file_path):
            extract_data_logger(file_path, key_mapping, passed_submissions_folder)
        else:
            print(f"{file_name} is not a zip file, moving to failed_submissions folder")
            shutil.move(file_path, os.path.join(failed_submission_folder, file_name))

# Main function
def main():
    submissions_zip_path = "submissions.zip"
    key_csv_path = "CanvasID_studentNumber_key.csv"
    if zipfile.is_zipfile(submissions_zip_path) and os.path.isfile(key_csv_path):
        key_mapping = read_key_csv(key_csv_path)
        with zipfile.ZipFile(submissions_zip_path, 'r') as submissions_zip:
            submissions_zip.extractall("submissions")  # Extract all files from submissions.zip to a folder named "submissions"
        process_zip_files("submissions", key_mapping)
        # Clean up extracted files and folder
        for file_name in os.listdir("submissions"):
            os.remove(os.path.join("submissions", file_name))
        os.rmdir("submissions")
    else:
        print("submissions.zip not found or is not a valid zip file, or CanvasID_studentNumber_key.csv not found")

if __name__ == "__main__":
    main()