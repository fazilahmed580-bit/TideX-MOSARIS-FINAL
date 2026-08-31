"""
TideX P1 — Geospatial output: mask → polygon → GeoJSON + metadata.

Converts a binary pixel mask into georeferenced polygons using the
source GeoTIFF's CRS and affine transform, reprojects to EPSG:4326,
and exports GeoJSON + a metadata JSON for P3/P5.
"""

import json
from pathlib import Path

import numpy as np
import geopandas as gpd
import rasterio
import rasterio.features
from pyproj import Transformer
from shapely.geometry import shape, mapping
from shapely.ops import unary_union

from src.config import OUTPUT_CRS


def mask_to_polygons(
    binary_mask: np.ndarray,
    transform: rasterio.Affine,
    crs,
) -> gpd.GeoDataFrame:
    """
    Vectorize a binary mask into polygons using rasterio.features.shapes.

    Parameters
    ----------
    binary_mask : (H, W) uint8 array with {0, 1}
    transform : rasterio Affine transform from the source GeoTIFF
    crs : CRS of the source GeoTIFF

    Returns
    -------
    GeoDataFrame in the source CRS with oil-spill polygons
    """
    # Vectorize — only extract regions where mask == 1
    shapes_gen = rasterio.features.shapes(
        binary_mask.astype(np.uint8),
        mask=binary_mask == 1,
        transform=transform,
    )

    polygons = []
    for geom, value in shapes_gen:
        if value == 1:
            polygons.append(shape(geom))

    if not polygons:
        print("No oil-spill polygons found in mask.")
        return gpd.GeoDataFrame(columns=["geometry"], crs=str(crs))

    print(f"Vectorized {len(polygons)} polygon(s) from mask")

    gdf = gpd.GeoDataFrame(
        {"geometry": polygons, "spill_id": range(1, len(polygons) + 1)},
        crs=str(crs),
    )

    return gdf


def reproject_to_wgs84(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Reproject GeoDataFrame to EPSG:4326 (WGS84)."""
    if gdf.empty:
        return gdf

    gdf_wgs = gdf.to_crs(OUTPUT_CRS)
    print(f"Reprojected to {OUTPUT_CRS}")
    return gdf_wgs


def compute_area_km2(gdf_wgs84: gpd.GeoDataFrame) -> float:
    """
    Compute total area of all polygons in km².
    Uses a temporary UTM projection for accurate area calculation.
    """
    if gdf_wgs84.empty:
        return 0.0

    # Get centroid for choosing a UTM zone
    centroid = gdf_wgs84.geometry.unary_union.centroid
    lon = centroid.x

    # Choose UTM zone
    utm_zone = int((lon + 180) / 6) + 1
    hemisphere = "north" if centroid.y >= 0 else "south"
    epsg = 32600 + utm_zone if hemisphere == "north" else 32700 + utm_zone

    gdf_utm = gdf_wgs84.to_crs(epsg=epsg)
    total_area_m2 = gdf_utm.geometry.area.sum()
    total_area_km2 = total_area_m2 / 1e6

    return total_area_km2


def compute_centroid(gdf_wgs84: gpd.GeoDataFrame) -> dict:
    """Compute centroid of all polygons in WGS84."""
    if gdf_wgs84.empty:
        return {"lat": None, "lon": None}

    centroid = gdf_wgs84.geometry.unary_union.centroid
    return {"lat": round(centroid.y, 6), "lon": round(centroid.x, 6)}


def compute_confidence(prob_map: np.ndarray, binary_mask: np.ndarray) -> float:
    """
    Compute average probability within the detected oil region.
    This serves as a rough confidence measure.
    """
    if binary_mask.sum() == 0:
        return 0.0

    return float(np.mean(prob_map[binary_mask == 1]))


def export_geojson(
    gdf_wgs84: gpd.GeoDataFrame,
    output_path: str | Path,
):
    """Save GeoDataFrame as GeoJSON."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    gdf_wgs84.to_file(output_path, driver="GeoJSON")
    print(f"GeoJSON saved: {output_path}")


def export_metadata(
    spill_detected: bool,
    confidence: float,
    area_km2: float,
    centroid: dict,
    polygon_file: str,
    source_image: str,
    output_path: str | Path,
    n_polygons: int = 0,
):
    """Save metadata JSON for P3/P5 consumption."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    metadata = {
        "spill_detected": spill_detected,
        "confidence": round(confidence, 4),
        "area_km2": round(area_km2, 4),
        "centroid": centroid,
        "n_polygons": n_polygons,
        "polygon_file": str(polygon_file),
        "crs": OUTPUT_CRS,
        "source_image": str(source_image),
    }

    with open(output_path, "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"Metadata saved: {output_path}")
    return metadata


def create_geospatial_output(
    binary_mask: np.ndarray,
    prob_map: np.ndarray,
    meta: dict,
    source_image: str,
    geojson_path: str | Path,
    metadata_path: str | Path,
) -> dict:
    """
    Full geospatial pipeline:
        mask → polygons → reproject → area/centroid → GeoJSON + metadata.

    Parameters
    ----------
    binary_mask : (H, W) uint8 cleaned mask
    prob_map : (H, W) float32 probability map
    meta : dict from inference containing 'transform', 'crs'
    source_image : original SAR image filename
    geojson_path : output path for GeoJSON
    metadata_path : output path for metadata JSON

    Returns
    -------
    metadata dict
    """
    print()
    print("=" * 50)
    print("GEOSPATIAL OUTPUT")
    print("=" * 50)

    transform = meta["transform"]
    crs = meta["crs"]

    # Vectorize
    gdf = mask_to_polygons(binary_mask, transform, crs)

    # Reproject
    gdf_wgs = reproject_to_wgs84(gdf)

    spill_detected = not gdf_wgs.empty

    if spill_detected:
        area_km2 = compute_area_km2(gdf_wgs)
        centroid = compute_centroid(gdf_wgs)
        confidence = compute_confidence(prob_map, binary_mask)
        n_polygons = len(gdf_wgs)

        export_geojson(gdf_wgs, geojson_path)
    else:
        area_km2 = 0.0
        centroid = {"lat": None, "lon": None}
        confidence = 0.0
        n_polygons = 0

        # Write an empty GeoJSON
        export_geojson(gdf_wgs, geojson_path)

    metadata = export_metadata(
        spill_detected=spill_detected,
        confidence=confidence,
        area_km2=area_km2,
        centroid=centroid,
        polygon_file=Path(geojson_path).name,
        source_image=Path(source_image).name,
        output_path=metadata_path,
        n_polygons=n_polygons,
    )

    print()
    print("Summary:")
    print(f"  Spill detected : {spill_detected}")
    print(f"  Confidence     : {confidence:.4f}")
    print(f"  Area           : {area_km2:.4f} km²")
    print(f"  Centroid       : {centroid}")
    print(f"  Polygons       : {n_polygons}")

    return metadata
