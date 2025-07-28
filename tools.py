from livekit.agents.llm import function_tool
from typing import Optional, List, Dict, Any
import asyncio
import json
import logging
from datetime import datetime

from database import TwiddlesDatabase

logger = logging.getLogger(__name__)

_db_instance: Optional[TwiddlesDatabase] = None

async def get_database() -> TwiddlesDatabase:
    """Get or create database instance."""
    global _db_instance
    if _db_instance is None:
        _db_instance = TwiddlesDatabase()
        await _db_instance.connect()
    return _db_instance

@function_tool
async def get_all_products() -> str:
    """
    Retrieve all products from the Twiddles database.
    
    Returns:
        str: JSON string containing all products with their details including name, price, 
             description, ingredients, stock status, and ratings
             
    Example:
        products = await get_all_products()
    """
    try:
        db = await get_database()
        
        # Now using async database operations
        products = await db.get_all_products()
        
        if products is None:
            return "Error: Unable to retrieve products from database"
        
        if not products:
            return "No products found in the database"
        
        # Convert ObjectId to string for JSON serialization
        for product in products:
            if '_id' in product:
                product['_id'] = str(product['_id'])
        
        return json.dumps(products, indent=2, default=str)
        
    except Exception as e:
        logger.error(f"Error in get_all_products: {e}")
        return f"Error occurred while retrieving products: {str(e)}"

# @function_tool
# async def search_products(category: Optional[str] = None, 
#                          in_stock: Optional[bool] = None,
#                          max_price: Optional[float] = None,
#                          brand: Optional[str] = None) -> str:
#     """
#     Search for products based on specific criteria.
    
#     Args:
#         category (Optional[str]): Product category (e.g., "Spreads", "Bites", "Combo")
#         in_stock (Optional[bool]): Filter by stock availability (True/False)
#         max_price (Optional[float]): Maximum price filter
#         brand (Optional[str]): Brand name filter
        
#     Returns:
#         str: JSON string containing filtered products matching the criteria
        
#     Example:
#         products = await search_products(category="Spreads", in_stock=True, max_price=300)
#     """
#     try:
#         db = get_database()
        
#         # Build filter dictionary
#         filter_dict = {}
#         if category:
#             filter_dict['category'] = category
#         if in_stock is not None:
#             filter_dict['in_stock'] = in_stock
#         if max_price is not None:
#             filter_dict['price'] = {'$lte': max_price}
#         if brand:
#             filter_dict['brand'] = brand
        
#         loop = asyncio.get_event_loop()
#         products = await loop.run_in_executor(None, db.get_products_by_filter, filter_dict)
        
#         if products is None:
#             return "Error: Unable to search products in database"
        
#         if not products:
#             return f"No products found matching the criteria: {filter_dict}"
        
#         # Convert ObjectId to string for JSON serialization
#         for product in products:
#             if '_id' in product:
#                 product['_id'] = str(product['_id'])
        
#         return json.dumps({
#             'filter_applied': filter_dict,
#             'products_found': len(products),
#             'products': products
#         }, indent=2, default=str)
        
#     except Exception as e:
#         logger.error(f"Error in search_products: {e}")
#         return f"Error occurred while searching products: {str(e)}"

@function_tool
async def get_user_wishlist(user_id: str) -> str:
    """
    Retrieve a user's wishlist items.
    
    Args:
        user_id (str): Unique identifier for the user (e.g., "user001")
        
    Returns:
        str: JSON string containing the user's wishlist items with product details,
             priority, notes, and notification preferences
             
    Example:
        wishlist = await get_user_wishlist("user001")
    """
    try:
        if not user_id:
            return "Error: User ID is required"
        
        db = await get_database()
        
        # Now using async database operations
        wishlist = await db.get_user_wishlist(user_id)
        
        if wishlist is None:
            return f"Error: Unable to retrieve wishlist for user {user_id}"
        
        if not wishlist:
            return f"No wishlist items found for user {user_id}"
        
        # Convert ObjectId to string for JSON serialization
        for item in wishlist:
            if '_id' in item:
                item['_id'] = str(item['_id'])
        
        return json.dumps({
            'user_id': user_id,
            'wishlist_count': len(wishlist),
            'wishlist_items': wishlist
        }, indent=2, default=str)
        
    except Exception as e:
        logger.error(f"Error in get_user_wishlist: {e}")
        return f"Error occurred while retrieving wishlist for user {user_id}: {str(e)}"

# @function_tool
# async def add_items_to_wishlist(user_id: str, product_id: str, 
#                                priority: str = "medium",
#                                notes: str = "",
#                                quantity_desired: int = 1,
#                                notification_on_stock: bool = True,
#                                notification_on_price_drop: bool = False) -> str:
#     """
#     Add an item to user's wishlist.
    
#     Args:
#         user_id (str): Unique identifier for the user
#         product_id (str): Product ID to add to wishlist
#         priority (str): Priority level ("high", "medium", "low")
#         notes (str): Optional notes about the product
#         quantity_desired (int): Desired quantity
#         notification_on_stock (bool): Enable stock notifications
#         notification_on_price_drop (bool): Enable price drop notifications
        
#     Returns:
#         str: Success message with the added item ID or error message
        
#     Example:
#         result = await add_items_to_wishlist("user001", "TW-BT-001", "high", "For birthday gift", 2)
#     """
#     try:
#         if not user_id or not product_id:
#             return "Error: User ID and Product ID are required"
        
#         if priority not in ["high", "medium", "low"]:
#             return "Error: Priority must be 'high', 'medium', or 'low'"
        
#         db = get_database()
        
#         # Create wishlist item
#         wishlist_item = {
#             "product_id": product_id,
#             "added_date": datetime.utcnow(),
#             "priority": priority,
#             "notes": notes,
#             "quantity_desired": quantity_desired,
#             "notification_on_stock": notification_on_stock,
#             "notification_on_price_drop": notification_on_price_drop
#         }
        
#         loop = asyncio.get_event_loop()
#         item_ids = await loop.run_in_executor(None, db.add_to_wishlist, user_id, [wishlist_item])
        
#         if item_ids is None:
#             return f"Error: Unable to add item to wishlist for user {user_id}"
        
#         return json.dumps({
#             'status': 'success',
#             'message': f'Item added to wishlist for user {user_id}',
#             'item_id': item_ids[0],
#             'product_id': product_id,
#             'added_item': wishlist_item
#         }, indent=2, default=str)
        
#     except Exception as e:
#         logger.error(f"Error in add_items_to_wishlist: {e}")
#         return f"Error occurred while adding item to wishlist: {str(e)}"

@function_tool
async def create_product_order(user_id: str, 
                              items: str,
                              shipping_address: str,
                              payment_method: str = "online",
                              special_instructions: str = "") -> str:
    """
    Create a new order for products for the user.
    
    Args:
        user_id (str): User id which was mention in the session data
        items (str): JSON string of items with product_id and quantity
                    Example: '[{"product_id": "TW-BT-001", "quantity": 2}]'
        shipping_address (str): Delivery address which is mention in the session data
        payment_method (str): Payment method ("online", "cod") which is mention in the session data if not default online
        special_instructions (str): Any special delivery instructions
        
    Returns:
        str: JSON string with order confirmation details and order ID
        
    Example:
        order = await create_product_order("user001", 
                                         '[{"product_id": "TW-BT-001", "quantity": 2}]',
                                         "123 Main St, City")
    """
    try:
        if not user_id or not items or not shipping_address:
            return "Error: User ID, items, and shipping address are required"
        
        # Parse items from JSON string
        try:
            parsed_items = json.loads(items)
        except json.JSONDecodeError as e:
            return f"Error: Invalid JSON format for items. Expected format: '[{{\"product_id\": \"TW-BT-001\", \"quantity\": 2}}]'. Error: {str(e)}"
        
        # Validate parsed items
        if not isinstance(parsed_items, list) or not parsed_items:
            return "Error: Items must be a non-empty list after parsing JSON"
        
        # Validate each item structure
        for i, item in enumerate(parsed_items):
            if not isinstance(item, dict):
                return f"Error: Item {i+1} must be a dictionary with product_id and quantity"
            if "product_id" not in item or "quantity" not in item:
                return f"Error: Item {i+1} must contain both 'product_id' and 'quantity' fields"
            if not isinstance(item.get("quantity"), (int, float)) or item.get("quantity") <= 0:
                return f"Error: Item {i+1} quantity must be a positive number"
        
        db = await get_database()
        
        order_data = {
            "user_id": user_id,
            "items": parsed_items,  # Use parsed items list
            "shipping_address": shipping_address,
            "payment_method": payment_method,
            "special_instructions": special_instructions if special_instructions else None,
            "order_status": "pending",
            "created_at": datetime.utcnow()
        }
        
        order_id = await db.create_order(order_data)
        
        if order_id is None:
            return "Error: Unable to create order"
        
        return json.dumps({
            'status': 'success',
            'message': 'Order created successfully',
            'order_id': order_id,
            'order_details': {
                'user_id': user_id,
                'items': parsed_items,
                'shipping_address': shipping_address,
                'payment_method': payment_method,
                'special_instructions': special_instructions,
                'order_status': 'pending'
            }
        }, indent=2, default=str)
        
    except Exception as e:
        logger.error(f"Error in create_product_order: {e}")
        return f"Error occurred while creating order: {str(e)}"
@function_tool
async def submit_product_feedback(user_id: str,
                                 product_id: str,
                                 rating: str,
                                 review_text: str,
                                 order_id: Optional[str] = None) -> str:
    """
    Submit feedback/review for a product.
    
    Args:
        user_id (str): Unique identifier for the user
        product_id (str): Product ID being reviewed
        rating (str): Rating from 1.0 to 5.0 (as string)
        review_text (str): Written review/feedback
        order_id (Optional[str]): Related order ID if applicable this can also be None
        
    Returns:
        str: JSON string with feedback submission confirmation
        
    Example:
        feedback = await submit_product_feedback("user001", "TW-BT-001", "4.5", 
                                               "Great taste and quality!")
    """
    try:
        if not user_id or not product_id or not review_text:
            return "Error: User ID, Product ID, and review text are required"
        
        # Convert rating string to float for validation
        try:
            rating_float = float(rating)
        except ValueError:
            return "Error: Rating must be a valid number"
        
        if not (1.0 <= rating_float <= 5.0):
            return "Error: Rating must be between 1.0 and 5.0"
        
        db = await get_database()
        
        # Create feedback data
        feedback_data = {
            "user_id": user_id,
            "product_id": product_id,
            "rating": rating_float,  # Use the converted float value
            "review_text": review_text,
            "order_id": order_id,
            "created_at": datetime.utcnow(),
            "verified_purchase": order_id is not None
        }
        
        # Now using async database operations
        feedback_id = await db.add_feedback(feedback_data)
        
        if feedback_id is None:
            return "Error: Unable to submit feedback"
        
        return json.dumps({
            'status': 'success',
            'message': 'Feedback submitted successfully',
            'feedback_id': feedback_id,
            'feedback_details': feedback_data
        }, indent=2, default=str)
        
    except Exception as e:
        logger.error(f"Error in submit_product_feedback: {e}")
        return f"Error occurred while submitting feedback: {str(e)}"

@function_tool
async def get_product_recommendations(user_id: str, 
                                    category: Optional[str] = None,
                                    max_price: Optional[str] = None) -> str:
    """
    Get product recommendations for a user based on their wishlist and preferences.
    
    Args:
        user_id (str): Unique identifier for the user
        category (Optional[str]): Specific category to recommend from
        max_price (Optional[str]): Maximum price range for recommendations
        
    Returns:
        str: JSON string containing recommended products
        
    Example:
        recommendations = await get_product_recommendations("user001", "Spreads", 300)
    """
    try:
        if not user_id:
            return "Error: User ID is required"
        
        db = await get_database()
        max_price = float(max_price) if max_price else None
        
        # Get user's wishlist to understand preferences
        wishlist = await db.get_user_wishlist(user_id)
        
        # Build recommendation filter based on wishlist and parameters
        filter_dict = {'in_stock': True}  # Only recommend available products
        
        if category:
            filter_dict['category'] = category
        if max_price:
            filter_dict['price'] = {'$lte': max_price}
        
        # Get products matching criteria
        products = await db.get_products_by_filter(filter_dict)
        
        if products is None:
            return "Error: Unable to get product recommendations"
        
        if not products:
            return "No products found matching recommendation criteria"
        
        # Filter out products already in wishlist
        wishlist_product_ids = []
        if wishlist:
            wishlist_product_ids = [item.get('product_id') for item in wishlist]
        
        recommended_products = [
            product for product in products 
            if product.get('product_id') not in wishlist_product_ids
        ]
        
        # Sort by rating (highest first)
        recommended_products.sort(key=lambda x: x.get('rating', 0), reverse=True)
        
        # Limit to top 5 recommendations
        recommended_products = recommended_products[:5]
        
        # Convert ObjectId to string for JSON serialization
        for product in recommended_products:
            if '_id' in product:
                product['_id'] = str(product['_id'])
        
        return json.dumps({
            'user_id': user_id,
            'recommendation_criteria': filter_dict,
            'total_recommendations': len(recommended_products),
            'recommended_products': recommended_products
        }, indent=2, default=str)
        
    except Exception as e:
        logger.error(f"Error in get_product_recommendations: {e}")
        return f"Error occurred while getting recommendations: {str(e)}"

@function_tool
async def get_user_info(user_id: str) -> str:
    """
    Retrieve user profile information from the database.This is used for geting the user profile information like name, contact details, customer type, preferred language, location, and registration details.
    use this function for ordering the products and adding feedback and to get the user profile information in needed.
    
    Args:
        user_id (str): Unique identifier for the user (e.g., "new_user_001", "repeat_user_001")
        
    Returns:
        str: JSON string containing user profile information including name, contact details,
             customer type, preferred language, location, and registration details
             
    Example:
        user_info = await get_user_info("new_user_001")
    """
    try:
        if not user_id:
            return "Error: User ID is required"
        
        db = await get_database()
        
        # Now using async database operations
        user_profile = await db.get_user_profile(user_id)
        
        if user_profile is None:
            return f"Error: Unable to retrieve user profile for {user_id}"
        
        if not user_profile:
            return f"No user profile found for user ID: {user_id}"
        
        # Convert datetime objects to string for JSON serialization
        if 'registration_date' in user_profile:
            user_profile['registration_date'] = user_profile['registration_date'].isoformat()
        if 'created_at' in user_profile:
            user_profile['created_at'] = user_profile['created_at'].isoformat()
        if 'updated_at' in user_profile:
            user_profile['updated_at'] = user_profile['updated_at'].isoformat()
        
        return json.dumps({
            'status': 'success',
            'user_profile': user_profile
        }, indent=2, default=str)
        
    except Exception as e:
        logger.error(f"Error in get_user_info: {e}")
        return f"Error occurred while retrieving user info for {user_id}: {str(e)}"

# Cleanup function to close database connection
async def cleanup_database():
    """Close database connection when done."""
    global _db_instance
    if _db_instance is not None:
        await _db_instance.disconnect()
        _db_instance = None