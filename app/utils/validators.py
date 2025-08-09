"""
Input validation utilities.
"""
import re
from typing import Dict, Any


def validate_plate(plate: str) -> Dict[str, Any]:
    """
    Validate Mexican license plate format.
    
    Args:
        plate: License plate string
        
    Returns:
        Dictionary with validation result
    """
    if not plate:
        return {'valid': False, 'message': 'Plate cannot be empty'}
    
    # Clean the plate
    clean_plate = plate.strip().upper().replace(" ", "")
    
    # Check length (Mexican plates are typically 6-7 characters)
    if len(clean_plate) < 6 or len(clean_plate) > 8:
        return {'valid': False, 'message': 'Plate must be 6-8 characters long'}
    
    # Basic format validation (letters and numbers)
    if not re.match(r'^[A-Z0-9]+$', clean_plate):
        return {'valid': False, 'message': 'Plate can only contain letters and numbers'}
    
    return {'valid': True, 'cleaned': clean_plate}


def validate_vin(vin: str) -> Dict[str, Any]:
    """
    Validate Vehicle Identification Number (VIN).
    
    Args:
        vin: VIN string
        
    Returns:
        Dictionary with validation result
    """
    if not vin:
        return {'valid': False, 'message': 'VIN cannot be empty'}
    
    # Clean the VIN
    clean_vin = vin.strip().upper().replace(" ", "")
    
    # Check length (VINs are typically 17 characters, but some older ones may vary)
    if len(clean_vin) < 11 or len(clean_vin) > 17:
        return {'valid': False, 'message': 'VIN must be 11-17 characters long'}
    
    # Basic format validation (letters and numbers, no I, O, Q)
    if not re.match(r'^[A-HJ-NPR-Z0-9]+$', clean_vin):
        return {'valid': False, 'message': 'VIN contains invalid characters (no I, O, Q allowed)'}
    
    return {'valid': True, 'cleaned': clean_vin}


def validate_request_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate complete request data.
    
    Args:
        data: Dictionary with request data
        
    Returns:
        Dictionary with validation result
    """
    errors = []
    
    # Validate plate
    if 'plate' in data:
        plate_result = validate_plate(data['plate'])
        if not plate_result['valid']:
            errors.append(f"Plate: {plate_result['message']}")
    else:
        errors.append("Plate is required")
    
    # Validate VIN
    if 'vin' in data:
        vin_result = validate_vin(data['vin'])
        if not vin_result['valid']:
            errors.append(f"VIN: {vin_result['message']}")
    else:
        errors.append("VIN is required")
    
    if errors:
        return {'valid': False, 'errors': errors}
    
    return {'valid': True}