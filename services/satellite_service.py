"""
Satellite Remote Sensing Data Service
Provides satellite-derived water quality proxies (NDTI, Turbidity Proxy, River Surface Extent).
Includes demo data generation & dataset ingestion methods.
"""

from datetime import datetime, timedelta
import random

def get_satellite_summary(station_id=None):
    """
    Returns satellite remote sensing metadata and configuration status.
    """
    return {
        "status": "Demonstration / Local Dataset Mode",
        "data_source": "Sentinel-2 MSIL2A / Landsat-9 Remote Sensing Proxies",
        "spatial_resolution": "10 meters",
        "revisit_time": "5 Days",
        "bands_used": "B4 (Red), B8 (NIR), B11 (SWIR-1)",
        "active_satellites": ["Sentinel-2A", "Sentinel-2B", "Landsat-9"],
        "disclaimer": "Satellite values represent Earth Observation proxy indices generated for academic prototype evaluation."
    }

def calculate_ndti(red_band, green_band):
    """
    Calculate Normalized Difference Turbidity Index (NDTI).
    NDTI = (Red - Green) / (Red + Green)
    """
    if red_band + green_band == 0:
        return 0.0
    return (red_band - green_band) / (red_band + green_band)

def generate_satellite_observation(station_id, lat, lng, in_situ_turbidity=None):
    """
    Generates realistic satellite observation parameters aligned with station location.
    """
    if in_situ_turbidity is not None:
        # Proxy turbidity aligns with in-situ measurement with slight remote sensing noise
        turbidity_proxy = max(1.0, in_situ_turbidity + random.uniform(-3.5, 4.2))
    else:
        turbidity_proxy = round(random.uniform(5.0, 65.0), 2)
        
    satellite_ndti = round((turbidity_proxy - 15.0) / (turbidity_proxy + 40.0), 4)
    water_extent = round(random.uniform(1.2, 4.8), 2) # River width/extent km2
    ndvi_water = round(random.uniform(-0.35, 0.15), 4) # Water Index / Algal Proxy

    return {
        "station_id": station_id,
        "observation_date": datetime.utcnow().strftime("%Y-%m-%d"),
        "latitude": lat,
        "longitude": lng,
        "satellite_index": satellite_ndti,
        "turbidity_proxy": round(turbidity_proxy, 2),
        "water_extent": water_extent,
        "ndvi_water": ndvi_water,
        "raw_source": "Sentinel-2 MSI Level-2A (Demo Proxy)"
    }
