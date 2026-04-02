from flask import Flask, render_template, request, jsonify
import pandas as pd
import os

app = Flask(__name__)

# Load the CSV file
csv_path = os.path.join(os.path.dirname(__file__), 'data.csv')
df = pd.read_csv(csv_path)

# Clean up the data: normalize numeric values and strip whitespace
df['Extended Length (in)'] = pd.to_numeric(df['Extended Length (in)'].astype(str).str.replace(',', '.'), errors='coerce')
df['Compressed Length (in)'] = pd.to_numeric(df['Compressed Length (in)'].astype(str).str.replace(',', '.'), errors='coerce')
df['Tube Dia (mm)'] = pd.to_numeric(df['Tube Dia (mm)'].astype(str).str.replace(',', '.').str.replace('"', ''), errors='coerce')
df['Rod Dia (mm)'] = pd.to_numeric(df['Rod Dia (mm)'].astype(str).str.replace(',', '.').str.replace(':', ''), errors='coerce')
df['Rod End Fitting'] = df['Rod End Fitting'].str.strip()
df['Tube End Fitting'] = df['Tube End Fitting'].str.strip()

# Drop rows with NaN values in key columns
df = df.dropna(subset=['Extended Length (in)', 'Compressed Length (in)', 'Tube Dia (mm)', 'Rod Dia (mm)'])

# Get unique values for each filter
extended_lengths = sorted(df['Extended Length (in)'].dropna().unique())
compressed_lengths = sorted(df['Compressed Length (in)'].dropna().unique())
tube_diameters = sorted(df['Tube Dia (mm)'].dropna().unique())
rod_diameters = sorted(df['Rod Dia (mm)'].dropna().unique())
rod_end_fittings = sorted(df['Rod End Fitting'].dropna().unique())
tube_end_fittings = sorted(df['Tube End Fitting'].dropna().unique())

@app.route('/')
def index():
    return render_template('index.html',
                         extended_lengths=extended_lengths,
                         compressed_lengths=compressed_lengths,
                         tube_diameters=tube_diameters,
                         rod_diameters=rod_diameters,
                         rod_end_fittings=rod_end_fittings,
                         tube_end_fittings=tube_end_fittings)

@app.route('/api/filter', methods=['POST'])
def filter_brands():
    data = request.get_json()
    
    # Start with the full dataframe
    filtered_df = df.copy()
    
    # Apply filters only if values are selected
    if data.get('extended_length') and data['extended_length'] != '':
        filtered_df = filtered_df[filtered_df['Extended Length (in)'] == float(data['extended_length'])]
    
    if data.get('compressed_length') and data['compressed_length'] != '':
        filtered_df = filtered_df[filtered_df['Compressed Length (in)'] == float(data['compressed_length'])]
    
    if data.get('tube_diameter') and data['tube_diameter'] != '':
        filtered_df = filtered_df[filtered_df['Tube Dia (mm)'] == float(data['tube_diameter'])]
    
    if data.get('rod_diameter') and data['rod_diameter'] != '':
        filtered_df = filtered_df[filtered_df['Rod Dia (mm)'] == float(data['rod_diameter'])]
    
    if data.get('rod_end_fitting') and data['rod_end_fitting'] != '':
        filtered_df = filtered_df[filtered_df['Rod End Fitting'] == data['rod_end_fitting']]
    
    if data.get('tube_end_fitting') and data['tube_end_fitting'] != '':
        filtered_df = filtered_df[filtered_df['Tube End Fitting'] == data['tube_end_fitting']]
    
    # Return Brand Numbers
    brand_numbers = filtered_df['Brand Number'].tolist()
    return jsonify({'brand_numbers': brand_numbers, 'count': len(brand_numbers)})

if __name__ == '__main__':
    app.run(debug=True)
