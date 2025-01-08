import tkinter as tk                            # GUI library framework
from tkinterdnd2 import TkinterDnD, DND_FILES   # Drag-n-drop features for GUI library
import os                                       # Operating System interaction library
import csv                                      # CSV interaction library


# Main function to process and manipulate imported CSV of GNSS Data 
def process_csv(file_path):
    try:
        # Create empty array for CSV
        raw_data = []

        # Open the imported CSV
        with open(file_path) as csvFile:
            csvFile = csv.reader(csvFile)
            # Go through each row and insert the first 5 columns of the row into the raw_data list
            for i in csvFile:
                raw_data.append(i[0:6])
        
        # Delete original CSV headers (First Row)
        del raw_data[0]

        # For each point, remove the "Code" column (2nd) which is empty by default
        for i in raw_data:
            del i[1]

        # Sort array by point identifiers in alphabetical order
        sorted_data = sorted(raw_data, key=lambda x: x[0])
        length = len(sorted_data)

        # Function to average GNSS coordinates for each pair of observations
        # This creates a new point by averaging Easting, Northing, and Height values and assigns a unique identifier.
        def average_gps(identifier, easting_1, northing_1, height_1, easting_2, northing_2, height_2, code):
            new_point = []

            # Set the new point name to the original observation, removing last character and adding '-GPS' (i.e. PM143A becomes PM143-GPS)
            gps_point_name = identifier[0:-1] + "-GPS"
            
            # Calculate averages and round to 3 decimal places
            average_easting = round(float((easting_1 + easting_2) / 2), 3)
            average_northing = round(float((northing_1 + northing_2) / 2), 3)
            average_height = round(float((height_1 + height_2) / 2), 3)

            # Combine averages and new point name into one point
            new_point.extend([gps_point_name, average_easting, average_northing, average_height, code])
            
            return new_point

        new_set = []
        
        # Creates a new point for every pair of GPS observations (since each point is observed twice)
        # It will use the 1st, 3rd, 5th... points as master points and use the direct subsequent point (2nd, 4th, 6th...) for averaging 
        for i in range(0, length, 2):
            new_set.append(average_gps(
                sorted_data[i][0],
                float(sorted_data[i][1]),
                float(sorted_data[i][2]),
                float(sorted_data[i][3]),
                float(sorted_data[i + 1][1]),
                float(sorted_data[i + 1][2]),
                float(sorted_data[i + 1][3]),
                str(sorted_data[i + 1][4])
            ))

        # Add the new averaged GPS points to sorted data
        for i in range(len(new_set)):
            sorted_data.append(new_set[i])

        # Final formatting and sorting of original observations and averaged points
        finished = sorted(sorted_data, key=lambda x: x[0][0])

        # Create new header format and insert into sorted final points
        headers = ['Name', 'Easting', 'Northing', 'Elevation', 'Code']
        finished.insert(0, headers)

        # Create new CSV file name 
        output_path = os.path.splitext(file_path)[0] + '-GPS-Import.csv'
        
        # Open output path with 
        with open(output_path, 'w', newline='') as csvfile:
            # 
            csv_writer = csv.writer(csvfile)
            # Write a new row for each list in the `finished` row
            for row in finished:
                csv_writer.writerow(row)

        # Output status label in window notifying user of new file location
        status_label.config(text=f'Success: File saved to {output_path}')

    except Exception as e:
        status_label.config(text=f'Error: {str(e)}')


# Function to handle a CSV file that has been drag-n-dropped into the window
def on_drop(event):

    file_path = event.data.strip()
    
    if file_path.endswith('.csv'):
        status_label.config(text=f'Processing file: {file_path}')
        process_csv(file_path)
    
    else:
        status_label.config(text='Error: Please drop a CSV file.')

# Initialise the main drag-n-drop enabled window
root = TkinterDnD.Tk()

# Set window/taskbar icon, title and size
root.iconbitmap("./GNSS-Reducer-Icon.ico")
root.title("GNSS Reducer")
root.geometry("500x200")

# Instructions label
instructions_label = tk.Label(root, text="Drag and drop a CSV file into this window to process GNSS data.")
instructions_label.pack(pady=30)

# Status label to show within window at open
status_label = tk.Label(root, text="Status: Waiting for file drop.", wraplength=400)
status_label.pack(pady=20)

# Enable drag and drop and link to on_drop event function
root.drop_target_register(DND_FILES)
root.dnd_bind('<<Drop>>', on_drop)

# Run the GUI event loop
root.mainloop()