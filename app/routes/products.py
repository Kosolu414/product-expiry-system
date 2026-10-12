from datetime import datetime
from flask import Blueprint, request, jsonify
from app.models import db, Product
from app.utils.auth_middleware import token_required, role_required

products_bp = Blueprint('products', __name__, url_prefix='/api/products')


@products_bp.route('', methods=['GET'])
@token_required
def get_products(current_user):
    """Retrieve products with optional status or category filtering."""
    status_filter = request.args.get('status')
    category_filter = request.args.get('category')

    query = Product.query

    if status_filter:
        query = query.filter_by(status=status_filter)
    if category_filter:
        query = query.filter_by(category=category_filter)

    products = query.all()

    # Recalculate status dynamically on retrieve
    for product in products:
        product.update_status()
    db.session.commit()

    return jsonify({
        'count': len(products),
        'products': [p.to_dict() for p in products]
    }), 200


@products_bp.route('', methods=['POST'])
@token_required
@role_required(['Admin', 'Manager'])
def create_product(current_user):
    """Add a new inventory product (Restricted to Admin & Manager)."""
    data = request.get_json() or {}

    required_fields = ['product_name', 'batch_number', 'quantity', 'expiry_date']
    for field in required_fields:
        if field not in data:
            return jsonify({'message': f'Missing required field: {field}'}), 400

    try:
        expiry_date = datetime.strptime(data['expiry_date'], '%Y-%m-%d').date()
        manufacture_date = datetime.strptime(data['manufacture_date'], '%Y-%m-%d').date() if data.get('manufacture_date') else None
    except ValueError:
        return jsonify({'message': 'Invalid date format. Use YYYY-MM-DD'}), 400

    new_product = Product(
        product_name=data['product_name'],
        category=data.get('category'),
        batch_number=data['batch_number'],
        quantity=data['quantity'],
        manufacture_date=manufacture_date,
        expiry_date=expiry_date
    )
    new_product.update_status()

    db.session.add(new_product)
    db.session.commit()

    return jsonify({'message': 'Product added successfully', 'product': new_product.to_dict()}), 201


@products_bp.route('/<int:product_id>', methods=['PUT'])
@token_required
@role_required(['Admin', 'Manager'])
def update_product(current_user, product_id):
    """Update existing product details."""
    product = Product.query.get_or_404(product_id)
    data = request.get_json() or {}

    if 'product_name' in data:
        product.product_name = data['product_name']
    if 'category' in data:
        product.category = data['category']
    if 'batch_number' in data:
        product.batch_number = data['batch_number']
    if 'quantity' in data:
        product.quantity = data['quantity']
    if 'expiry_date' in data:
        try:
            product.expiry_date = datetime.strptime(data['expiry_date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'message': 'Invalid date format for expiry_date. Use YYYY-MM-DD'}), 400

    product.update_status()
    db.session.commit()

    return jsonify({'message': 'Product updated successfully', 'product': product.to_dict()}), 200


@products_bp.route('/<int:product_id>', methods=['DELETE'])
@token_required
@role_required(['Admin'])
def delete_product(current_user, product_id):
    """Delete a product record (Admin only)."""
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()

    return jsonify({'message': 'Product deleted successfully'}), 200