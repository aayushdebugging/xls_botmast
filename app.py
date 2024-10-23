import pandas as pd
import re
import streamlit as st
import json

def determine_room_count(unit_type):
    """
    Determine the room count based on keywords in the unit type.
    """
    if pd.isna(unit_type):
        return "Unknown"
    
    unit_type = str(unit_type).lower()

    # Define dynamic keywords for room count determination
    keyword_mapping = {
        'studio': '1', 
        '1 bed': '1', '1br': '1', '1 bhk': '1', '1 bedroom': '1', 'onebedroom': '1',
        '1.5 br': '1.5', '1.5 bhk': '1.5', '1.5 bed': '1.5',
        '2 bed': '2', '2br': '2', '2 bhk': '2', '2 bedroom': '2', 'twobedroom': '2',
        '2.5 br': '2.5', '2.5 bhk': '2.5',
        '3 bed': '3', '3br': '3', '3 bhk': '3', '3 bedroom': '3', 'threebedroom': '3',
        '4 bed': '4', '4br': '4', '4 bhk': '4', '4 bedroom': '4', 'fourbedroom': '4',
        '5 bed': '5', '5br': '5', '5 bhk': '5', '5 bedroom': '5',
        '6 bed': '6', '6br': '6', '6 bhk': '6', '6 bedroom': '6',
        'penthouse': '4', 'duplex': '3', 'executive': '1', 'premium one': '1', 'premium two': '2'
    }

    # Check for predefined keywords in unit_type
    for keyword, room_count in keyword_mapping.items():
        if keyword in unit_type:
            return room_count

    # Extract numerical values from the unit type text as a fallback
    match = re.search(r'(\d+(\.\d+)?)\s*br', unit_type)  # Match patterns like '1.5 BR', '2 BR'
    if match:
        return match.group(1)

    return "Unknown"

def group_by_project_csv(df):
    """
    Group the data based on the 'Project' column and display unique 'Unit Type' 
    with their corresponding room counts for each project.
    """
    # Check if 'Project' and 'Unit Type' columns exist
    if 'Project' not in df.columns or 'Unit Type' not in df.columns:
        raise ValueError("Both 'Project' and 'Unit Type' columns must be present in the input file.")
    
    # Create a dictionary to store the grouped results by 'Project'
    project_groups = {}

    # Iterate through each row and group by 'Project'
    for _, row in df.iterrows():
        project = row['Project']
        unit_type = row['Unit Type']
        room_count = determine_room_count(unit_type)

        if project not in project_groups:
            project_groups[project] = []
        
        # Add the unit type and room count if it's not already added
        if unit_type not in [unit['unit_type'] for unit in project_groups[project]]:
            project_groups[project].append({
                'unit_type': unit_type,
                'room_count': room_count
            })

    return project_groups

# Streamlit app
st.title("Project Room Count Analyzer")

# File uploader
uploaded_file = st.file_uploader("Upload your input CSV file", type="csv")

if uploaded_file:
    try:
        # Read the CSV file
        df = pd.read_csv(uploaded_file)

        # Group the data by 'Project'
        grouped_data = group_by_project_csv(df)

        # Display the grouped results
        for project, units in grouped_data.items():
            st.write(f'**Project: {project}**')
            for unit in units:
                st.write(f'("{unit["unit_type"]}", "{unit["room_count"]}"),')
            st.write('---')  # Add a separator for better readability

        # Prepare data for JSON download
        json_output = {}
        for project, units in grouped_data.items():
            json_output[project] = [(unit['unit_type'], unit['room_count']) for unit in units]

        # Convert the dictionary to JSON
        json_data = json.dumps(json_output, indent=4)

        # Download button for the JSON file
        st.download_button(
            label="Download JSON",
            data=json_data,
            file_name="grouped_projects.json",
            mime="application/json"
        )

    except Exception as e:
        st.error(f"Error: {e}")
