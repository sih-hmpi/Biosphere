Environmental Impact API
This project is a FastAPI-based application for processing environmental data, computing ecosystem indicators, and visualizing them on an interactive map using Deck.gl and Mapbox. It processes geospatial data from a GeoTIFF file (sample.tif) and JSON data (river_data.json) to assess environmental impacts, such as heavy metal concentrations and derived indicators like bioaccumulation and soil toxicity.
Features

Endpoints:
/compute-indicators (POST): Computes ecosystem indicators from JSON input (e.g., river_data.json).
/raster-risk (POST): Processes a GeoTIFF file to generate GeoJSON with computed indicators.
/datapoints (GET): Returns GeoJSON data for map visualization.
/deckgl-map (GET): Displays an interactive map with points colored by indicator values (e.g., bioaccumulation) and sized by soil toxicity.


Interactive Map:
Visualizes metal concentrations and ecosystem indicators.
Supports zoom, pan, tooltips, and a dropdown to select indicators.
Uses Mapbox for the base map and Deck.gl for geospatial layers.



Prerequisites

Python: 3.8 or higher
Virtual Environment: Recommended for dependency isolation
Mapbox Access Token: Obtain from Mapbox
Dependencies:
fastapi
uvicorn
pydantic
rasterio
numpy



Directory Structure
biosphere-main/
├── main.py              # FastAPI application
├── river_data.json      # Sample environmental data
├── sample.tif           # GeoTIFF with metal concentrations
├── generate_tif.py      # Script to generate sample.tif
├── venv/                # Virtual environment
├── README.md            # This file

Setup Instructions

Clone or Set Up the Project Directory

Ensure you're working in C:\Users\Kunal\Desktop\biosphere-main.
If files are in a nested biosphere-main\biosphere-main directory, move them up:mv C:\Users\Kunal\Desktop\biosphere-main\biosphere-main\* C:\Users\Kunal\Desktop\biosphere-main\
cd C:\Users\Kunal\Desktop\biosphere-main




Create and Activate Virtual Environment
python -m venv venv
.\venv\Scripts\Activate.ps1


Install Dependencies
pip install fastapi uvicorn pydantic rasterio numpy


If rasterio fails on Windows, download a precompiled wheel from Unofficial Windows Binaries (e.g., rasterio-1.3.10-cp310-cp310-win_amd64.whl) and install:pip install path\to\rasterio-1.3.10-cp310-cp310-win_amd64.whl




Set Up Files

Save main.py:
Copy the FastAPI code from the provided source (without <xaiArtifact> tags) into main.py.
Update the Mapbox token in the /deckgl-map endpoint:accessToken: 'your_mapbox_token_here'

Replace 'your_mapbox_token_here' with a valid token from Mapbox.


Save river_data.json:
Copy the provided JSON data (with location_id: "river_002", etc.) into river_data.json.
Validate it:python -c "import json; json.load(open('river_data.json'))"




Generate sample.tif:
Save the following as generate_tif.py:import rasterio
import numpy as np

metals = ["As", "Pb", "Cd", "Cr", "Hg", "Ni", "Cu", "Zn", "Fe", "Se", "Al", "B", "Ba", "Ag", "Mo", "Sb"]
height, width = 100, 100
bands = len(metals)
data = np.random.uniform(0, 0.1, size=(bands, height, width))
data[0] *= 0.5  # As
data[4] *= 0.01  # Hg
data[8] *= 10  # Fe
transform = rasterio.transform.from_origin(west=-74.1, north=40.8, xsize=0.001, ysize=0.001)
meta = {
    'driver': 'GTiff', 'height': height, 'width': width, 'count': bands,
    'dtype': 'float32', 'crs': 'EPSG:4326', 'transform': transform, 'nodata': -9999
}
with rasterio.open('sample.tif', 'w', **meta) as dst:
    for i in range(bands):
        dst.write(data[i], i+1)
        dst.set_band_description(i+1, metals[i])


Run:python generate_tif.py







Running the Application

Start the FastAPI Server
cd C:\Users\Kunal\Desktop\biosphere-main
uvicorn main:app --reload --port 8000


Expected output:INFO:     Will watch for changes in these directories: ['C:\\Users\\Kunal\\Desktop\\biosphere-main']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [...]
INFO:     Started server process [...]
INFO:     Waiting for application startup.
INFO:     Application startup complete.




View the Interactive Map

Open a browser and navigate to:http://127.0.0.1:8000/deckgl-map


Expected Visualization:
Mapbox dark map centered on NYC ([-74.006, 40.7128]).
Points from sample.tif showing metal concentrations and indicators.
Colors based on selected indicator (default: potential_bioaccumulation_factor):
Red (>200), orange (>100), green (low).


Point sizes scaled by soil_toxicity_index (2–20 pixels).
Tooltips on hover showing As, Pb, Bioaccumulation, Soil Toxicity, Acidification.
Dropdown to switch between indicators (e.g., Bioaccumulation, Soil Toxicity, Acidification Potential).





Testing Endpoints

Test /compute-indicators

Send river_data.json:curl -X POST "http://127.0.0.1:8000/compute-indicators" -H "Content-Type: application/json" -d @river_data.json -o response.json


Check response.json for computed indicators, e.g.:{
  "ecosystem_indicators": {
    "potential_bioaccumulation_factor": {"value": 208.0, ...},
    "soil_toxicity_index": {"value": 15.3, ...},
    ...
  }
}




Test /raster-risk

Upload sample.tif:# test_raster.py
import requests
url = "http://127.0.0.1:8000/raster-risk"
files = {"raster_file": open("sample.tif", "rb")}
data = {"sample_resolution": 10}
response = requests.post(url, files=files, data=data)
with open("raster_response.json", "w") as f:
    json.dump(response.json(), f, indent=2)
print(response.json()["features"][0]["properties"])

python test_raster.py


Expect GeoJSON with computed indicators.


Test /datapoints
curl http://127.0.0.1:8000/datapoints -o datapoints.json


Verify datapoints.json contains a FeatureCollection.



Troubleshooting

Server Fails to Start:
Verify main.py, river_data.json, and sample.tif are in C:\Users\Kunal\Desktop\biosphere-main.
Check for syntax errors:python -c "import main"


Ensure dependencies are installed.


Map Not Rendering:
Open browser console (F12) at http://127.0.0.1:8000/deckgl-map to check for errors (e.g., invalid Mapbox token).
Verify /datapoints works:curl http://127.0.0.1:8000/datapoints


Ensure sample.tif exists and is readable.


500 Error on /datapoints:
Check if sample.tif is in the correct directory.
Run with debug logging:uvicorn main:app --reload --port 8000 --log-level debug




405 Error on /compute-indicators:
This was fixed in the updated main.py by removing the incorrect GET request in /deckgl-map.



Notes

The application assumes sample.tif and river_data.json are in the project root.
Customize the map by modifying the /deckgl-map endpoint (e.g., add more indicators to the dropdown).
For production, store GeoJSON data in a database instead of processing sample.tif on each request.

License
MIT License
