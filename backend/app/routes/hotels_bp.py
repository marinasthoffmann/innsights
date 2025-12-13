from flask import Blueprint, request, current_app, jsonify
from services.hotels_service import HotelService
from schemas.hotel_schema import HotelListResponse, HotelResponse, HotelCreate, HotelUpdate
from pydantic import ValidationError


hotels_bp = Blueprint('hotels', __name__)

@hotels_bp.route('', methods=['GET'])
def get_hotels():
    """
    List all hotels with pagination and filters.
    
    Query Parameters:
        page (int): Page number (default: 1)
        page_size (int): Items per page (default: 20, max: 100)
        city (str): Filter by city
        country (str): Filter by country
        min_rating (float): Minimum star rating
    
    Returns:
        200: JSON response with paginated hotel list
        400: Invalid query parameters
        500: Internal server error
    """
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', current_app.config['DEFAULT_PAGE_SIZE']))
        city = request.args.get('city')
        country = request.args.get('country')
        min_rating = request.args.get('min_rating')
        
        # Validate pagination
        if page < 1:
            return jsonify({'error': 'Page must be >= 1'}), 400
        
        page_size = min(page_size, current_app.config['MAX_PAGE_SIZE'])
        
        # Parse min_rating if provided
        if min_rating:
            try:
                min_rating = float(min_rating)
                if not (1 <= min_rating <= 5):
                    return jsonify({'error': 'min_rating must be between 1 and 5'}), 400
            except ValueError:
                return jsonify({'error': 'min_rating must be a number'}), 400
        
        # Get hotels
        service = HotelService()
        hotels, total, total_pages = service.list_hotels(
            page=page,
            page_size=page_size,
            city=city,
            country=country,
            min_rating=min_rating
        )
        
        # Serialize response
        response = HotelListResponse(
            items=[HotelResponse.model_validate(hotel) for hotel in hotels],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
        
        return jsonify(response.model_dump()), 200
        
    except Exception as error:
        current_app.logger.error(f"Error listing hotels: {error}")
        return jsonify({'error': 'Internal server error'}), 500
    
@hotels_bp.route('/<int:hotel_id>', methods=['GET'])
def get_hotel(hotel_id: int):
    """
    Get a specific hotel by ID.
    
    Args:
        hotel_id: Hotel ID
    
    Returns:
        200: JSON response with hotel details
        404: Hotel not found
        500: Internal server error
    """
    try:
        service = HotelService()
        hotel = service.get_hotel(hotel_id)
        
        if not hotel:
            return jsonify({'error': 'Hotel not found'}), 404
        
        response = HotelResponse.model_validate(hotel)
        return jsonify(response.model_dump()), 200
        
    except Exception as error:
        current_app.logger.error(f"Error getting hotel {hotel_id}: {error}")
        return jsonify({'error': 'Internal server error'}), 500
    
@hotels_bp.route('', methods=['POST'])
def create_hotel():
    """
    Create a new hotel.
    
    Request Body:
        JSON with hotel data (HotelCreate schema)
    
    Returns:
        201: JSON response with created hotel
        400: Validation error or invalid data
        500: Internal server error
    """
    try:
        hotel_data = HotelCreate(**request.json)
        
        service = HotelService()
        hotel = service.create_hotel(hotel_data.model_dump())
        
        response = HotelResponse.model_validate(hotel)
        return jsonify(response.model_dump()), 201
        
    except ValidationError as error:
        return jsonify({
            'error': 'Validation error',
            'details': error.errors()
        }), 400
    except ValueError as error:
        return jsonify({'error': str(error)}), 400
    except Exception as error:
        current_app.logger.error(f"Error creating hotel: {error}")
        return jsonify({'error': 'Internal server error'}), 500
    
@hotels_bp.route('/<int:hotel_id>', methods=['PUT'])
def update_hotel(hotel_id: int):
    """
    Update a hotel.
    
    Args:
        hotel_id: Hotel ID
    
    Request Body:
        JSON with fields to update (see HotelUpdate schema)
    
    Returns:
        200: JSON response with updated hotel
        400: Validation error
        404: Hotel not found
        500: Internal server error
    """
    try:
        update_data = HotelUpdate(**request.json)
        
        service = HotelService()
        hotel = service.update_hotel(hotel_id, update_data.model_dump(exclude_none=True))
        
        if not hotel:
            return jsonify({'error': 'Hotel not found'}), 404
        
        response = HotelResponse.model_validate(hotel)
        return jsonify(response.model_dump()), 200
        
    except ValidationError as error:
        return jsonify({
            'error': 'Validation error',
            'details': error.errors()
        }), 400
    except ValueError as error:
        return jsonify({'error': str(error)}), 400
    except Exception as error:
        current_app.logger.error(f"Error updating hotel {hotel_id}: {error}")
        return jsonify({'error': 'Internal server error'}), 500
    
@hotels_bp.route('/<int:hotel_id>', methods=['DELETE'])
def delete_hotel(hotel_id: int):
    """
    Delete a hotel.
    
    Args:
        hotel_id: Hotel ID
    
    Returns:
        204: No content (success)
        404: Hotel not found
        500: Internal server error
    """
    try:
        service = HotelService()
        deleted = service.delete_hotel(hotel_id)
        
        if not deleted:
            return jsonify({'error': 'Hotel not found'}), 404
        
        return '', 204
        
    except Exception as error:
        current_app.logger.error(f"Error deleting hotel {hotel_id}: {error}")
        return jsonify({'error': 'Internal server error'}), 500

