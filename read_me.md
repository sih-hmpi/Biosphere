=== dataset ===
from hmpi engine or other engines.

=== input: ===
"location_id": "river_002", "location_name": "Blue River", "latitude": 40.7128, "longitude": -74.0060, "water_body_type": "River", "sample_date": "2025-09-16", "concentrations": { "As": 0.02, "Pb": 0.03, "Cd": 0.001, "Cr": 0.015, "Hg": 0.0008, "Ni": 0.1, "Cu": 0.01, "Zn": 0.08, "Fe": 1.5, "Se": 0.01, "Al": 0.2, "B": 0.8, "Ba": 1.2, "Ag": 0.002, "Mo": 0.05, "Sb": 0.04 }, "chemistry": { "pH": 6.5, "temperature": 25.0, "dissolved_oxygen": 5.5, "organic_matter": 4.0 },17. pH – influences nutrient availability for plants, microbial activity
18. Temperature – affects enzyme activity in plants and microorganisms
19. Dissolved oxygen – low DO affects soil-aquatic organism interaction and plant root health
20. Organic matter – influences soil fertility and microbial diversity
21. Electrical conductivity / salinity (if measured) – affects plant osmotic balance
22. Turbidity (if measured) – impacts sunlight penetration for aquatic plants
23. Nitrogen compounds (Nitrate/Nitrite/Ammonia) – if measured, impacts algae, microbes, and plants
24. Phosphorus (if measured) – affects plant growth and eutrophication
25. Total suspended solids – affects soil sedimentation and plant photosynthesis
26. Redox potential (Eh) – influences metal solubility and microbial activity
27. Heavy metal bioavailability fraction – indicates how easily metals enter plants/soil
28. Chlorides – can affect soil structure and plant osmotic balance

=== output: ===

**A. Heavy metal contamination (toxic effects on plants, soil organisms, and aquatic life indirectly)**

> Metals can affect soil microbial communities, plant growth, and bioaccumulate in terrestrial and aquatic food webs.

**B. Water chemistry and physical properties (impacting ecosystems, soil, and vegetation indirectly)**

#### **C. Derived/Combined Ecosystem Indicators**

29. Potential bioaccumulation factor (based on metals)
30. Soil toxicity index (metal + pH + organic matter)
31. Nutrient limitation index (N, P, organic matter)
32. Acidification potential (pH + Al + heavy metals)
33. Sediment deposition index (if available)

> These are indirect indicators affecting plants, soil microbes, and terrestrial/aquatic food webs.

This gives you **>20 points impacting the biosphere** beyond humans and fish.

---

### **Step 2: 10+ visualizable geospatial data points for deck.gl**

For **deck.gl visualizations**, you want points that make sense on a map with meaningful sizes/colors. Examples:

2. 
5. 
6. **Dissolved oxygen** – size or elevation
7. 
8. **Organic matter** – color intensity or elevation
9. 
12. **Bioaccumulation potential index** – heatmap
13. **Soil toxicity index** – polygon layer for zones

> For deck.gl: Use **HexagonLayer or ScatterplotLayer** for concentrations and **ColumnLayer** for elevation/height representations.

=