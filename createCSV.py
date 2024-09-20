import csv
import xml.etree.ElementTree as ET

def extract_track_data(gpx_content, track_id):
    """
    Extract latitude, longitude, time, name, and description from a GPX content string.
    :param gpx_content: A string containing a GPX XML section.
    :param track_id: The identifier for the current GPX track.
    :return: A list of dictionaries with the extracted data.
    """
    gpx_tree = ET.ElementTree(ET.fromstring(gpx_content))
    root = gpx_tree.getroot()
    
    # Namespaces used in GPX files
    ns = {'gpx': 'http://www.topografix.com/GPX/1/0'}

    track_data = []

    # Extract name and description
    name = root.find('.//gpx:name', ns).text if root.find('.//gpx:name', ns) is not None else 'No Name'
    description = root.find('.//gpx:desc', ns).text if root.find('.//gpx:desc', ns) is not None else 'No Description'

    if name == 'No Name' and description == 'No Description':
        return []

    track_data.append({
            'track_id': track_id,
            'name': name,
            'description': description,
            'num_points': len(root.findall('.//gpx:trkpt', ns))
    })

    return track_data

def parse_gpx_file(input_file, output_file):
    """
    Parse the GPX file, extract information, and save it as a CSV.
    :param input_file: Path to the text file containing multiple GPX tracks.
    :param output_file: Path to the output CSV file.
    """
    with open(input_file, 'r') as f:
        gpx_content = f.read()

    gpx_sections = gpx_content.split('</gpx>\n')  # Split the text file into sections, assuming each GPX ends with </gpx>
    
    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = ['track_id', 'name', 'descriptison','num_points']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        track_id = 1
        for section in gpx_sections:
            if '<trk' in section:  # Only process sections that contain a GPX trace
                gpx_data = extract_track_data(section + '</gpx>', track_id)
                for row in gpx_data:
                    writer.writerow(row)
                track_id += 1

if __name__ == '__main__':
    input_file = './all_florida_gps_traces.txt'  # Replace with your input file path
    output_file = './gpx_tracks.csv'  # Replace with your desired output file path
    parse_gpx_file(input_file, output_file)
