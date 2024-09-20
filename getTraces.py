import requests
import time
import os
import xml.etree.ElementTree as ET

# Log messages to file in case of crashing
def log_to_file(message, log_file="gps_traces_log.txt"):
    with open(log_file, "a") as f:
        f.write(f"{message}\n")

# Function to construct the OSM API URL for GPS traces given a bounding box and page
def construct_osm_url(min_lon, min_lat, max_lon, max_lat, page=0):
    return f"https://api.openstreetmap.org/api/0.6/trackpoints?bbox={min_lon},{min_lat},{max_lon},{max_lat}&page={page}"

# Function to fetch GPS traces from OSM within a bounding box, handling pagination
def fetch_gps_traces(bbox, page=0, max_retries=5):
    time.sleep(1)
    url = construct_osm_url(*bbox, page)
    attempts = 0

    while attempts < max_retries:
        try:
            response = requests.get(url, timeout=60)  # Set a timeout of 60 seconds
            if response.status_code == 200:
                return response.content, response.headers.get('Content-Length', len(response.content)), response
            elif response.status_code == 429:
                log_to_file(f"Error: HTTP {response.status_code} (HIT REQUEST LIMIT) for bbox {bbox} page {page}")
                time.sleep(10)
                attempts += 1
                continue
            else:
                log_to_file(f"Error: HTTP {response.status_code} for bbox {bbox} page {page}")
                attempts += 1
                continue
        except requests.exceptions.Timeout:
            log_to_file(f"Timeout occurred for bbox {bbox} page {page}. Retrying... (Attempt {attempts + 1}/{max_retries})")
        except requests.exceptions.RequestException as e:
            log_to_file(f"An error occurred: {e}. Retrying... (Attempt {attempts + 1}/{max_retries})")
        except Exception as e:
            log_to_file(f"Unexpected error: {e}. Retrying... (Attempt {attempts + 1}/{max_retries})")

        attempts += 1
        time.sleep(2)  # Wait for 2 seconds before retrying

    log_to_file(f"Max retries reached for bbox {bbox} page {page}.")
    return None, 0, None

# Function to save the GPX traces to a file
def save_traces_to_file(content, file_name):
    with open(file_name, "ab") as file:
        file.write(content)

# Function to generate bounding boxes for the given region
def generate_bounding_boxes(min_lon, min_lat, max_lon, max_lat, step=0.25):
    lon = min_lon
    while lon < max_lon:
        lat = min_lat
        while lat < max_lat:
            yield (lon, lat, lon + step, lat + step)
            lat += step
        lon += step

# Function to handle a single request for GPS traces, with pagination
def handle_gps_traces_request(bbox, file_name):

    page = 0
    while True:
        log_to_file(f"Fetching GPS traces for bbox: {bbox}, page: {page}")
        
        # Fetch traces with pagination
        content, content_length, response = fetch_gps_traces(bbox, page)

        # If response is okay
        if response != None and content != None:
            # Handle pagination and no track points
            if b"trkpt" not in content:
                log_to_file(f"No traces for bbox: {bbox}, page {page}\n")
                break
            else:
                save_traces_to_file(content, file_name)
                log_to_file(f"Saved traces for bbox: {bbox}, page: {page} ({content_length} bytes) to {file_name}")
        # If response is not okay
        else:
            break
        
        # Go to the next page
        page += 1        

# Function to create a folder with an incremented name if it already exists
def create_unique_folder(base_folder_name):
    folder_name = base_folder_name
    counter = 1
    while os.path.exists(folder_name):
        folder_name = f"{base_folder_name}({counter})"
        counter += 1
    os.makedirs(folder_name)
    return folder_name

# Main function to pull GPS traces and save to a file
def pull_gps_traces():

    # Define bounding box. Currently set for Florida
    min_lon, min_lat = -87.6349, 24.3963
    max_lon, max_lat = -79.9743, 31.0009

    # Generate all 0.25x0.25 degree bounding boxes for seleced area
    bounding_boxes = generate_bounding_boxes(min_lon, min_lat, max_lon, max_lat, step=0.25)
    
    # Set file name for where raw GPS traces will end up
    folder_name = create_unique_folder("gps_traces")

    # Loop through each bounding box and fetch traces
    for bbox in bounding_boxes:
        # Generate a unique file name for each bounding box and save it to the folder
        file_name = os.path.join(folder_name, f"gps_traces_{bbox[0]}_{bbox[1]}_{bbox[2]}_{bbox[3]}.txt")
        handle_gps_traces_request(bbox, file_name)

if __name__ == "__main__":
    pull_gps_traces()
    log_to_file("Completed pulling all traces")