import boto3
import webbrowser
import os

def getContentsOfFolder(bucket_name, folder_key):
    """
    Gets the contents of specified folder from specified s3 bucket.
    Returns contents in a list file keys or None value if nothing exists 

    bucket_name: s3 bucket name
    folder_keu: name of folder, in this case @timestamp value
    """
    s3 = boto3.client('s3')
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=folder_key, Delimiter='/')

    #checks for subfolders in specified folder (schematic-testing)
    if 'CommonPrefixes' not in response:
        return None

    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=folder_key)

    #checks for content of subfolder (@timestamp)
    if 'Contents' not in response:
        return None

    return [file['Key'] for file in response['Contents']]

def downLoadS3Bucket(bucket_name, file_key, local_filename):
    """
    Downloads the contents of the file_key from a s3 bucket to a local location

    bucket_name: s3 bucket name
    file_key: invidual file key for kicad/altium png
    local_filename: location to store downloaded object of file_key
    """
    s3 = boto3.client('s3')
    try:
        s3.download_file(bucket_name, file_key, local_filename)
        print(f"File downloaded: {local_filename}")
    except Exception as e:
        print(f"Error downloading file: {e}")

def addToS3Bucket(local_file_path, bucket_name, desired_object_key):
    """
    Adds a local_file (kicad/altium png) to a s3 bucket and gives it a file_key_name

    local_file_path: location of png file to upload to s3 bucket
    bucket_name: s3 bucket name
    desired_object_key: name of png ex. kicad1.kicad_sch
    """
    s3_client = boto3.client('s3')
    try:
        s3_client.upload_file(local_file_path, bucket_name, desired_object_key)
        print(f"File uploaded: {desired_object_key}")
    except Exception as e:
        print(f"Error uploading file: {e}")

def downloadAndCreateHTML(bucket_name, folder_key):
    """
    Downloads desired s3 bucket contents using getContentsOfFile
        to get the file_keys and downLoadS3Bucket() to download them
    Creates HTML file to with .png images to open in a webrowser

    bucket_name: s3 bucket name
    folder_key: @timestamp folder with .png contents
    """
    image_width=600
    image_height=450
    file_keys = getContentsOfFolder(bucket_name, folder_key)
    reordered_fileKeys = file_keys[:3] + file_keys[6:9] + file_keys[3:6] + file_keys[9:]
    if file_keys:
        for file in file_keys:
            downLoadS3Bucket(bucket_name, file, f"schematic_cv_test/data/data_from_s3/{os.path.basename(file)}")
    else:
        print("No files found in the folder or bucket.")

    html_content = f"<html><head><style>img {{ width: {image_width}px; height: {image_height}px; }}</style></head><body>"
    for file in reordered_fileKeys:
        html_content += f"<img src='schematic_cv_test/data/data_from_s3/{os.path.basename(file)}'>"
    html_content += "</body></html>"

    html_file_path = "html_generated_data.html"
    with open(html_file_path, 'w') as f:
        f.write(html_content)
    webbrowser.open(html_file_path)
