import os
from typing import Dict, Any, Optional, Tuple
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

def dms_to_decimal(dms: Tuple, ref: str) -> float:
    # Convert degrees, minutes, seconds tuple/rational to decimal degrees
    def to_float(val):
        if hasattr(val, "numerator") and hasattr(val, "denominator"):
            return float(val.numerator) / float(val.denominator) if val.denominator != 0 else 0.0
        return float(val)

    deg = to_float(dms[0])
    minutes = to_float(dms[1])
    sec = to_float(dms[2])

    decimal = deg + (minutes / 60.0) + (sec / 3600.0)
    if ref in ['S', 'W']:
        decimal = -decimal
    return round(decimal, 6)

def extract_image_metadata(file_path: str) -> Dict[str, Any]:
    metadata: Dict[str, Any] = {
        "width": 0,
        "height": 0,
        "format": "",
        "has_gps": False,
        "latitude": None,
        "longitude": None,
        "camera_make": None,
        "camera_model": None,
        "date_time": None
    }

    if not os.path.exists(file_path):
        return metadata

    try:
        with Image.open(file_path) as img:
            metadata["width"] = img.width
            metadata["height"] = img.height
            metadata["format"] = img.format or ""

            exif_raw = img.getexif()
            if not exif_raw:
                return metadata

            gps_info = {}
            for tag_id, value in exif_raw.items():
                tag_name = TAGS.get(tag_id, tag_id)
                if tag_name == "Make":
                    metadata["camera_make"] = str(value)
                elif tag_name == "Model":
                    metadata["camera_model"] = str(value)
                elif tag_name == "DateTime":
                    metadata["date_time"] = str(value)
                elif tag_name == "GPSInfo":
                    # Parse GPS Sub-IFD
                    if hasattr(exif_raw, "get_ifd"):
                        gps_info = exif_raw.get_ifd(tag_id)
                    elif isinstance(value, dict):
                        gps_info = value

            if gps_info:
                parsed_gps = {}
                for key, val in gps_info.items():
                    sub_tag = GPSTAGS.get(key, key)
                    parsed_gps[sub_tag] = val

                lat_dms = parsed_gps.get("GPSLatitude")
                lat_ref = parsed_gps.get("GPSLatitudeRef")
                lon_dms = parsed_gps.get("GPSLongitude")
                lon_ref = parsed_gps.get("GPSLongitudeRef")

                if lat_dms and lat_ref and lon_dms and lon_ref:
                    try:
                        metadata["latitude"] = dms_to_decimal(lat_dms, lat_ref)
                        metadata["longitude"] = dms_to_decimal(lon_dms, lon_ref)
                        metadata["has_gps"] = True
                    except Exception:
                        pass
    except Exception:
        pass

    return metadata
