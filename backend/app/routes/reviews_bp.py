from flask import Blueprint, request, jsonify, current_app
from pydantic import ValidationError
from schemas.review_schema import ReviewCreate, ReviewResponse, ReviewListResponse
from services.reviews_service import ReviewService
from models.review import ReviewStatus

reviews_bp = Blueprint('reviews', __name__)

@reviews_bp.route('', methods=['POST'])
def create_review():
    """
    Create a new review.
    
    Request Body:
        JSON with review data (see ReviewCreate schema)
    
    Returns:
        201: JSON response with created review
        400: Validation error or invalid data
        500: Internal server error
    """
    try:
        review_data = ReviewCreate(**request.json)
        
        service = ReviewService()
        review = service.create_review(review_data.model_dump())
        
        response = ReviewResponse.model_validate(review)
        return jsonify(response.model_dump()), 201
        
    except ValidationError as error:
        return jsonify({
            'error': 'Validation error',
            'details': error.errors()
        }), 400
    except ValueError as error:
        return jsonify({'error': str(error)}), 400
    except Exception as error:
        current_app.logger.error(f"Error creating review: {error}")
        return jsonify({'error': 'Internal server error'}), 500
    
@reviews_bp.route('', methods=['GET'])
def list_reviews():
    """
    List all reviews with pagination and filters.
    
    Query Parameters:
        page (int): Page number (default: 1)
        page_size (int): Items per page (default: 20)
        status (str): Filter by status (pending/processing/completed/failed)
    
    Returns:
        200: JSON response with paginated review list
        400: Invalid query parameters
        500: Internal server error
    """
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', current_app.config['DEFAULT_PAGE_SIZE']))
        status_str = request.args.get('status')

        if page < 1:
            return jsonify({'error': 'Page must be >= 1'}), 400
        
        page_size = min(page_size, current_app.config['MAX_PAGE_SIZE'])

        status = None
        if status_str:
            try:
                status = ReviewStatus(status_str.lower())
            except ValueError:
                return jsonify({
                    'error': f'Invalid status: {status_str}',
                    'valid_statuses': [s.value for s in ReviewStatus]
                }), 400

        service = ReviewService()
        reviews, total, total_pages = service.list_reviews(
            page=page,
            page_size=page_size,
            status=status
        )

        response = ReviewListResponse(
            items=[ReviewResponse.model_validate(review) for review in reviews],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
        
        return jsonify(response.model_dump()), 200
        
    except Exception as error:
        current_app.logger.error(f"Error listing reviews: {error}")
        return jsonify({'error': 'Internal server error'}), 500
    
@reviews_bp.route('/<int:review_id>', methods=['GET'])
def get_review(review_id: int):
    """
    Get a specific review by ID.
    
    Args:
        review_id: Review ID
    
    Returns:
        200: JSON response with review details
        404: Review not found
        500: Internal server error
    """
    try:
        service = ReviewService()
        review = service.get_review(review_id, with_hotel=True)
        
        if not review:
            return jsonify({'error': 'Review not found'}), 404
        
        response = ReviewResponse.model_validate(review)
        return jsonify(response.model_dump()), 200
        
    except Exception as error:
        current_app.logger.error(f"Error getting review {review_id}: {error}")
        return jsonify({'error': 'Internal server error'}), 500
    
@reviews_bp.route('/hotels/<int:hotel_id>', methods=['GET'])
def list_hotel_reviews(hotel_id: int):
    """
    List reviews for a specific hotel.
    
    Args:
        hotel_id: Hotel ID
    
    Query Parameters:
        page (int): Page number (default: 1)
        page_size (int): Items per page (default: 20)
        status (str): Filter by status
    
    Returns:
        200: JSON response with paginated reviews for the hotel
        400: Invalid parameters
        404: Hotel not found
        500: Internal server error
    """
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', current_app.config['DEFAULT_PAGE_SIZE']))
        status_str = request.args.get('status')

        if page < 1:
            return jsonify({'error': 'Page must be >= 1'}), 400
        
        page_size = min(page_size, current_app.config['MAX_PAGE_SIZE'])

        status = None
        if status_str:
            try:
                status = ReviewStatus(status_str.lower())
            except ValueError:
                return jsonify({
                    'error': f'Invalid status: {status_str}',
                    'valid_statuses': [s.value for s in ReviewStatus]
                }), 400

        service = ReviewService()
        reviews, total, total_pages = service.list_hotel_reviews(
            hotel_id=hotel_id,
            page=page,
            page_size=page_size,
            status=status
        )

        response = ReviewListResponse(
            items=[ReviewResponse.model_validate(review) for review in reviews],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
        
        return jsonify(response.model_dump()), 200
        
    except ValueError as error:
        return jsonify({'error': str(error)}), 404
    except Exception as error:
        current_app.logger.error(f"Error listing hotel reviews: {error}")
        return jsonify({'error': 'Internal server error'}), 500