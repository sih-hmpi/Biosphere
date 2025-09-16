from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import json
import os

app = FastAPI()

# Pydantic model for input validation
class WaterSample(BaseModel):
    location_id: str
    location_name: str
    latitude: float
    longitude: float
    water_body_type: str = "River"  # Optional with default
    sample_date: str
    concentrations: Dict[str, float]
    chemistry: Dict[str, Any]

# Load existing samples
def load_samples():
    if os.path.exists("water_samples.json"):
        with open("water_samples.json") as f:
            return json.load(f)
    return []

# Calculate derived indices for biosphere impact
def calculate_derived_indices(concentrations, chemistry):
    bioaccumulation_index = sum(concentrations.values()) / len(concentrations)
    soil_toxicity_index = (concentrations.get('Al', 0) + chemistry.get('organic_matter', 0)) / 10
    acidification_potential = (7 - chemistry.get('pH', 7)) + concentrations.get('Al', 0)
    nutrient_limitation_index = chemistry.get('organic_matter', 0) / 5
    return {
        "bioaccumulation_index": round(bioaccumulation_index, 3),
        "soil_toxicity_index": round(soil_toxicity_index, 3),
        "acidification_potential": round(acidification_potential, 3),
        "nutrient_limitation_index": round(nutrient_limitation_index, 3)
    }

# Generate visualization fields for deck.gl
def generate_visualization_fields(concentrations, chemistry, derived_indices):
    return {
        "As_color": "#ff0000" if concentrations.get('As', 0) > 0.01 else "#ffa07a",
        "Pb_color": "#ff4500" if concentrations.get('Pb', 0) > 0.02 else "#ffb347",
        "Cd_color": "#ff6347" if concentrations.get('Cd', 0) > 0.001 else "#ffc0cb",
        "Zn_height": int(concentrations.get('Zn', 0) * 1000),
        "Fe_height": int(concentrations.get('Fe', 0) * 100),
        "pH_color": "#32cd32" if 6 <= chemistry.get('pH', 7) <= 8 else "#ff6347",
        "DO_height": int(chemistry.get('dissolved_oxygen', 0) * 50),
        "Temp_color": "#1e90ff" if chemistry.get('temperature', 0) < 25 else "#ff8c00",
        "OrganicMatter_height": int(chemistry.get('organic_matter', 0) * 50),
        "Bioaccumulation_heat": int(derived_indices["bioaccumulation_index"] * 100),
        "SoilToxicity_heat": int(derived_indices["soil_toxicity_index"] * 100)
    }

# Process a single sample
def process_sample(sample):
    concentrations = sample["concentrations"]
    chemistry = sample["chemistry"]
    derived_indices = calculate_derived_indices(concentrations, chemistry)
    viz_fields = generate_visualization_fields(concentrations, chemistry, derived_indices)
    
    return {
        "location_id": sample["location_id"],
        "location_name": sample["location_name"],
        "latitude": sample["latitude"],
        "longitude": sample["longitude"],
        "water_body_type": sample.get("water_body_type", ""),
        "sample_date": sample["sample_date"],
        "concentrations": concentrations,
        "chemistry": chemistry,
        "derived_indices": derived_indices,
        "visualization_fields": viz_fields
    }

# Process all samples and save
def process_and_save_samples():
    samples = load_samples()
    processed_samples = [process_sample(sample) for sample in samples]
    with open("processed_water_samples.json", "w") as f:
        json.dump(processed_samples, f, indent=2)
    return processed_samples

# API Endpoints
@app.get("/samples")
def get_samples():
    processed_samples = process_and_save_samples()
    return processed_samples

@app.post("/samples")
def add_sample(new_sample: WaterSample):
    sample_dict = new_sample.dict()
    samples = load_samples()
    samples.append(sample_dict)
    with open("water_samples.json", "w") as f:
        json.dump(samples, f, indent=2)
    
    processed_samples = process_and_save_samples()
    return processed_samples

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)