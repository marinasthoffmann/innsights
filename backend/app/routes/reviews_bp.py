from flask import Blueprint, request, jsonify, current_app
from pydantic import ValidationError
from schemas.review_schema import ReviewCreate, ReviewResponse
from services.reviews_service import ReviewService

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