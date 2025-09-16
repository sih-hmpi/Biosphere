
import json
import numpy as np
import rasterio
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Dict, Optional, List

app = FastAPI(title="Environmental Impact API", description="Human Health & Aquatic Life Risk Assessment")

# Pydantic models for input validation (from previous response)
class Visualization(BaseModel):
    type: str
    attribute: str
    description: str

class ChemistryParameter(BaseModel):
    value: Optional[float]
    description: str
    deckgl_visualization: Optional[Visualization] = None

class AdditionalParameter(BaseModel):
    measured: bool
    description: str
    deckgl_visualization: Optional[Visualization] = None

class EcosystemIndicator(BaseModel):
    value: Optional[float]
    description: str
    impacts: Optional[str] = None
    deckgl_visualization: Optional[Visualization] = None

class GeospatialPoint(BaseModel):
    parameter: str
    value: Optional[float]
    deckgl_visualization: Visualization

class EnvironmentalData(BaseModel):
    location_id: str
    location_name: str
    latitude: float
    longitude: float
    water_body_type: str
    sample_date: str
    concentrations: Dict[str, float]
    chemistry: Dict[str, ChemistryParameter]
    additional_parameters: Dict[str, AdditionalParameter]
    ecosystem_indicators: Dict[str, EcosystemIndicator]
    geospatial_data_points: List[GeospatialPoint]

# Utility function to compute ecosystem indicators (from previous response)
def compute_ecosystem_indicators(data: dict) -> dict:
    concentrations = data['concentrations']
    chemistry = data['chemistry']
    
    ph = chemistry['pH']['value']
    organic_matter = chemistry['organic_matter']['value']
    do = chemistry['dissolved_oxygen']['value']
    temp = chemistry['temperature']['value']
    al = concentrations['Al']
    as_val = concentrations['As']
    pb = concentrations['Pb']
    cd = concentrations['Cd']
    hg = concentrations['Hg']
    cr = concentrations['Cr']
    ni = concentrations['Ni']
    cu = concentrations['Cu']
    zn = concentrations['Zn']
    fe = concentrations['Fe']
    
    indicators = data['ecosystem_indicators']
    indicators['potential_bioaccumulation_factor']['value'] = (hg + cd + as_val) * 10000
    indicators['soil_toxicity_index']['value'] = (pb + cd + cr + ni + cu + zn + fe) * 10 + (7 - ph) * 5 - organic_matter * 2
    indicators['nutrient_limitation_index']['value'] = 100 - organic_matter * 10
    indicators['acidification_potential']['value'] = (7 - ph) * 10 + (al + as_val + pb) * 50
    indicators['sediment_deposition_index']['value'] = fe * 20
    redox_placeholder = 200
    indicators['metal_mobility_index']['value'] = (pb + cd + hg) * 1000 + (300 - redox_placeholder)
    micro_metals = cu + zn + ni
    indicators['microbial_activity_suppression_index']['value'] = micro_metals * 100 + abs(ph - 7) * 5
    indicators['aquatic_plant_stress_index']['value'] = (8 - do) * 10 + (cr + hg) * 10000
    indicators['eutrophication_risk_index']['value'] = organic_matter * 15
    chlorides_placeholder = 0
    indicators['soil_structure_stability_index']['value'] = organic_matter * 10 - chlorides_placeholder * 2
    toxic_metals = cd + hg + as_val
    indicators['heavy_metal_toxicity_to_aquatic_life_index']['value'] = toxic_metals * 100000 + (6 - do) * 5
    indicators['plant_nutrient_availability_index']['value'] = organic_matter * 15 - abs(ph - 6.5) * 10
    indicators['oxygen_depletion_risk_index']['value'] = (8 - do) * 10 + (temp - 20) * 2 + organic_matter * 3
    soil_metals = pb + zn + cu
    indicators['metal_bioaccumulation_in_soil_organisms_index']['value'] = soil_metals * 100 + organic_matter * 5
    resilience_score = organic_matter * 10 + do * 5 - (pb + cd + hg) * 1000 - abs(ph - 7) * 3
    indicators['ecosystem_resilience_index']['value'] = max(0, resilience_score)
    
    for point in data['geospatial_data_points']:
        if point['parameter'] in indicators:
            point['value'] = indicators[point['parameter']]['value']
    
    return data

# Process raster data to GeoJSON
def raster_to_geojson(raster_file: str, sample_resolution: int = 10) -> Dict:
    with rasterio.open(raster_file) as src:
        data = src.read()  # Shape: (bands, height, width)
        transform = src.transform
        metals = ["As", "Pb", "Cd", "Cr", "Hg", "Ni", "Cu", "Zn", "Fe", "Se", "Al", "B", "Ba", "Ag", "Mo", "Sb"]
        
        features = []
        for i in range(0, src.height, sample_resolution):
            for j in range(0, src.width, sample_resolution):
                # Get coordinates
                lon, lat = rasterio.transform.xy(transform, i, j)
                # Get concentrations
                concentrations = {metals[b]: float(data[b, i, j]) for b in range(len(metals))}
                # Simulate indicator calculation for this point
                indicator_data = {
                    "location_id": f"point_{i}_{j}",
                    "location_name": "Sample Point",
                    "latitude": lat,
                    "longitude": lon,
                    "water_body_type": "Raster",
                    "sample_date": "2025-09-16",
                    "concentrations": concentrations,
                    "chemistry": {
                        "pH": {"value": 6.5, "description": "Placeholder"},
                        "temperature": {"value": 25.0, "description": "Placeholder"},
                        "dissolved_oxygen": {"value": 5.5, "description": "Placeholder"},
                        "organic_matter": {"value": 4.0, "description": "Placeholder"}
                    },
                    "additional_parameters": {},
                    "ecosystem_indicators": {
                        "potential_bioaccumulation_factor": {"value": null, "description": "Based on metals", "impacts": "Bioaccumulation"},
                        "soil_toxicity_index": {"value": null, "description": "Derived from metals, pH, OM", "impacts": "Soil toxicity"},
                        "nutrient_limitation_index": {"value": null, "description": "Based on N, P, OM", "impacts": "Nutrient constraints"},
                        "acidification_potential": {"value": null, "description": "Based on pH, Al, metals", "impacts": "Acidification risk"},
                        "sediment_deposition_index": {"value": null, "description": "Sediment deposition", "impacts": "Ecosystem impact"},
                        "metal_mobility_index": {"value": null, "description": "Metal mobility", "impacts": "Bioavailability"},
                        "microbial_activity_suppression_index": {"value": null, "description": "Microbial suppression", "impacts": "Soil fertility"},
                        "aquatic_plant_stress_index": {"value": null, "description": "Plant stress", "impacts": "Aquatic ecosystems"},
                        "eutrophication_risk_index": {"value": null, "description": "Eutrophication risk", "impacts": "Oxygen depletion"},
                        "soil_structure_stability_index": {"value": null, "description": "Soil stability", "impacts": "Plant growth"},
                        "heavy_metal_toxicity_to_aquatic_life_index": {"value": null, "description": "Aquatic toxicity", "impacts": "Biodiversity"},
                        "plant_nutrient_availability_index": {"value": null, "description": "Nutrient availability", "impacts": "Plant productivity"},
                        "oxygen_depletion_risk_index": {"value": null, "description": "Oxygen depletion", "impacts": "Aquatic life"},
                        "metal_bioaccumulation_in_soil_organisms_index": {"value": null, "description": "Soil organism bioaccumulation", "impacts": "Soil food webs"},
                        "ecosystem_resilience_index": {"value": null, "description": "Ecosystem resilience", "impacts": "Biodiversity"}
                    },
                    "geospatial_data_points": []
                }
                indicator_data = compute_ecosystem_indicators(indicator_data)
                features.append({
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [lon, lat]},
                    "properties": {
                        "concentrations": concentrations,
                        "indicators": {k: v["value"] for k, v in indicator_data["ecosystem_indicators"].items()}
                    }
                })
        
        return {"type": "FeatureCollection", "features": features}

# Existing endpoints (simplified for brevity)
@app.get("/")
def root():
    return {"message": "Welcome to the Environmental Impact API. Docs at /docs"}

@app.post("/compute-indicators", response_model=dict)
async def compute_indicators(data: EnvironmentalData):
    try:
        data_dict = data.dict()
        updated_data = compute_ecosystem_indicators(data_dict)
        return updated_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing data: {str(e)}")

# Updated raster-risk endpoint to process GeoTIFF
@app.post("/raster-risk", response_model=Dict)
async def raster_risk(raster_file: UploadFile = File(...), sample_resolution: int = Form(10)):
    try:
        # Save uploaded GeoTIFF temporarily
        with open("temp.tif", "wb") as f:
            f.write(await raster_file.read())
        # Process raster to GeoJSON
        geojson_data = raster_to_geojson("temp.tif", sample_resolution)
        return geojson_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Updated datapoints endpoint
@app.get("/datapoints", response_model=Dict)
def datapoints():
    try:
        # Use sample.tif for demo; in prod, use stored data
        return raster_to_geojson("sample.tif", sample_resolution=10)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Updated deckgl-map endpoint
@app.get("/deckgl-map", response_class=HTMLResponse)
def deckgl_map():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Environmental Impact Map</title>
        <script src="https://unpkg.com/deck.gl@latest/dist.min.js"></script>
        <script src="https://api.tiles.mapbox.com/mapbox-gl-js/v2.14.1/mapbox-gl.js"></script>
        <link href="https://api.tiles.mapbox.com/mapbox-gl-js/v2.14.1/mapbox-gl.css" rel="stylesheet" />
        <style>
            #tooltip {
                position: absolute;
                background: rgba(0, 0, 0, 0.8);
                color: white;
                padding: 8px;
                border-radius: 4px;
                pointer-events: none;
                display: none;
            }
        </style>
    </head>
    <body style="margin:0;">
        <div id="map" style="width:100vw; height:100vh;"></div>
        <div id="tooltip"></div>
        <script>
            const {DeckGL, ScatterplotLayer, GeoJsonLayer} = deck;
            const map = new mapboxgl.Map({
                container: 'map',
                style: 'mapbox://styles/mapbox/dark-v10',
                center: [-74.006, 40.7128],
                zoom: 10,
                accessToken: 'pk.eyJ1IjoiZGV2YXVyMDMiLCJhIjoiY21mbjJiZzM5MDhtaDJqc2pyOHBjcXMxYSJ9.BGdLe4hfbpFAEBmBve4McQ'
            });

            fetch('/datapoints')
                .then(res => res.json())
                .then(data => {
                    const deckgl = new DeckGL({
                        map: map,
                        initialViewState: {longitude: -74.006, latitude: 40.7128, zoom: 10},
                        controller: true,
                        layers: [
                            new GeoJsonLayer({
                                id: 'raster-points',
                                data: data,
                                getPosition: d => d.geometry.coordinates,
                                getFillColor: d => {
                                    const bioacc = d.properties.indicators.potential_bioaccumulation_factor || 0;
                                    return bioacc > 200 ? [255, 0, 0] : bioacc > 100 ? [255, 165, 0] : [0, 255, 0];
                                },
                                getRadius: d => {
                                    const tox = d.properties.indicators.soil_toxicity_index || 0;
                                    return Math.min(Math.max(tox * 2, 2), 20);
                                },
                                pickable: true,
                                onHover: ({object, x, y}) => {
                                    const tooltip = document.getElementById('tooltip');
                                    if (object) {
                                        const props = object.properties;
                                        tooltip.style.display = 'block';
                                        tooltip.style.left = x + 10 + 'px';
                                        tooltip.style.top = y + 10 + 'px';
                                        tooltip.innerHTML = `
                                            <b>Point</b><br>
                                            As: ${props.concentrations.As.toFixed(3)} mg/L<br>
                                            Pb: ${props.concentrations.Pb.toFixed(3)} mg/L<br>
                                            Bioaccumulation: ${props.indicators.potential_bioaccumulation_factor.toFixed(2)}<br>
                                            Soil Toxicity: ${props.indicators.soil_toxicity_index.toFixed(2)}
                                        `;
                                    } else {
                                        tooltip.style.display = 'none';
                                    }
                                }
                            }),
                            new ScatterplotLayer({
                                id: 'indicator-points',
                                data: '/compute-indicators',  // Fetch from compute-indicators
                                getPosition: d => [d.longitude, d.latitude],
                                getRadius: d => {
                                    const tox = d.ecosystem_indicators.soil_toxicity_index.value || 0;
                                    return Math.min(Math.max(tox * 2, 5), 50);
                                },
                                getFillColor: d => {
                                    const bioacc = d.ecosystem_indicators.potential_bioaccumulation_factor.value || 0;
                                    return bioacc > 200 ? [255, 0, 0, 200] : [0, 255, 0, 200];
                                },
                                radiusMinPixels: 5,
                                radiusMaxPixels: 50,
                                pickable: true,
                                onHover: ({object, x, y}) => {
                                    const tooltip = document.getElementById('tooltip');
                                    if (object) {
                                        tooltip.style.display = 'block';
                                        tooltip.style.left = x + 10 + 'px';
                                        tooltip.style.top = y + 10 + 'px';
                                        tooltip.innerHTML = `
                                            <b>${object.location_name}</b><br>
                                            Bioaccumulation: ${object.ecosystem_indicators.potential_bioaccumulation_factor.value.toFixed(2)}<br>
                                            Soil Toxicity: ${object.ecosystem_indicators.soil_toxicity_index.value.toFixed(2)}
                                        `;
                                    } else {
                                        tooltip.style.display = 'none';
                                    }
                                }
                            })
                        ]
                    });
                });
        </script>
    </body>
    </html>
    """