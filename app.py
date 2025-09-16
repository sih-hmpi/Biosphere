import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional
from uuid import uuid4

app = FastAPI(title="Environmental Data API", description="API to process environmental data and compute ecosystem indicators")

# Pydantic models for input validation
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
    geospatial_data_points: list[GeospatialPoint]

# Utility function to compute ecosystem indicators
def compute_ecosystem_indicators(data: dict) -> dict:
    concentrations = data['concentrations']
    chemistry = data['chemistry']
    
    # Extract input values
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
    
    # Compute indicators with simple formulas
    indicators = data['ecosystem_indicators']
    
    # 29. Potential bioaccumulation factor
    indicators['potential_bioaccumulation_factor']['value'] = (hg + cd + as_val) * 10000
    
    # 30. Soil toxicity index
    metal_tox = pb + cd + cr + ni + cu + zn + fe
    indicators['soil_toxicity_index']['value'] = (metal_tox * 10) + (7 - ph) * 5 - organic_matter * 2
    
    # 31. Nutrient limitation index
    indicators['nutrient_limitation_index']['value'] = 100 - organic_matter * 10
    
    # 32. Acidification potential
    acid_metals = al + as_val + pb
    indicators['acidification_potential']['value'] = (7 - ph) * 10 + acid_metals * 50
    
    # 33. Sediment deposition index
    indicators['sediment_deposition_index']['value'] = fe * 20
    
    # Additional indicators
    redox_placeholder = 200  # Assume neutral redox
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
    
    # Update geospatial points
    for point in data['geospatial_data_points']:
        if point['parameter'] in indicators:
            point['value'] = indicators[point['parameter']]['value']
    
    return data

# FastAPI endpoint
@app.post("/compute-indicators", response_model=dict)
async def compute_indicators(data: EnvironmentalData):
    try:
        # Convert Pydantic model to dict for processing
        data_dict = data.dict()
        
        # Compute indicators
        updated_data = compute_ecosystem_indicators(data_dict)
        
        return updated_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing data: {str(e)}")

# Root endpoint for basic info
@app.get("/")
async def root():
    return {
        "message": "Environmental Data API",
        "description": "Post environmental data to /compute-indicators to calculate ecosystem indicators",
        "example_input": "See documentation for EnvironmentalData schema"
    }