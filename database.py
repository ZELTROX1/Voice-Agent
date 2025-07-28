from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, DuplicateKeyError
import datetime
import logging
from bson import ObjectId
from typing import List, Dict, Any, Optional
import os
from dotenv import load_dotenv
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class TwiddlesDatabase:
    """
    Database class for managing Twiddles e-commerce data in MongoDB.
    
    Handles connections, CRUD operations for products, orders, feedback, and wishlists.
    """
    
    def __init__(self, database_name: str = 'Techladder'):
        """
        Initialize database connection.
        
        Args:
            database_name (str): Name of the MongoDB database
        """
        self.database_name = database_name
        self.client: Optional[AsyncIOMotorClient] = None
        self.db = None
        
        # Get credentials from environment
        self.username = os.getenv("MONGODB_USERNAME")
        self.password = os.getenv("MONGODB_PASSWORD")
        self.url = os.getenv("MONGODB_URL")
        
        if not all([self.username, self.password, self.url]):
            raise ValueError("Missing required MongoDB environment variables")
            
        self.uri = f"mongodb+srv://{self.username}:{self.password}@{self.url}/?retryWrites=true&w=majority"

    async def connect(self) -> bool:
        """
        Establish connection to MongoDB.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.client = AsyncIOMotorClient(self.uri)
            # Test connection
            await self.client.admin.command('ping')
            self.db = self.client[self.database_name]
            logger.info(f"Successfully connected to MongoDB database: {self.database_name}")
            return True
            
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during connection: {e}")
            return False

    async def disconnect(self) -> None:
        """Close the MongoDB connection."""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")

    async def insert_documents(self, collection_name: str, documents: List[Dict[str, Any]]) -> Optional[List[str]]:
        """
        Insert multiple documents into a collection.
        
        Args:
            collection_name (str): Name of the collection
            documents (List[Dict]): List of documents to insert
            
        Returns:
            Optional[List[str]]: List of inserted document IDs, None if error
        """
        if self.db is None:
            logger.error("Database not connected")
            return None
            
        collection = self.db[collection_name]
        
        try:
            result = await collection.insert_many(documents)
            inserted_ids = [str(id) for id in result.inserted_ids]
            logger.info(f"Successfully inserted {len(inserted_ids)} documents into '{collection_name}'")
            return inserted_ids
            
        except Exception as e:
            logger.error(f"Error inserting documents into '{collection_name}': {e}")
            return None

    async def get_all_products(self) -> Optional[List[Dict[str, Any]]]:
        """
        Retrieve all products from the products collection.
        
        Returns:
            Optional[List[Dict]]: List of all products, None if error
        """
        if self.db is None:
            logger.error("Database not connected")
            return None
            
        try:
            cursor = self.db['products'].find({})
            products = await cursor.to_list(length=None)
            logger.info(f"Retrieved {len(products)} products")
            return products
            
        except Exception as e:
            logger.error(f"Error retrieving products: {e}")
            return None

    async def get_products_by_filter(self, filter_dict: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
        """
        Retrieve products based on filter criteria.
        
        Args:
            filter_dict (Dict): MongoDB filter criteria
            
        Returns:
            Optional[List[Dict]]: Filtered products, None if error
        """
        if self.db is None:
            logger.error("Database not connected")
            return None
            
        try:
            cursor = self.db['products'].find(filter_dict)
            products = await cursor.to_list(length=None)
            logger.info(f"Retrieved {len(products)} products matching filter")
            return products
            
        except Exception as e:
            logger.error(f"Error retrieving filtered products: {e}")
            return None

    async def create_order(self, order_data: Dict[str, Any]) -> Optional[str]:
        """
        Create a new order.
        
        Args:
            order_data (Dict): Order information
            
        Returns:
            Optional[str]: Order ID if successful, None if error
        """
        if self.db is None:
            logger.error("Database not connected")
            return None
            
        # Add timestamp if not provided
        if 'created_at' not in order_data:
            order_data['created_at'] = datetime.datetime.utcnow()
            
        try:
            result = await self.db['orders'].insert_one(order_data)
            order_id = str(result.inserted_id)
            logger.info(f"Successfully created order with ID: {order_id}")
            return order_id
            
        except Exception as e:
            logger.error(f"Error creating order: {e}")
            return None

    async def add_feedback(self, feedback_data: Dict[str, Any]) -> Optional[str]:
        """
        Add user feedback.
        
        Args:
            feedback_data (Dict): Feedback information
            
        Returns:
            Optional[str]: Feedback ID if successful, None if error
        """
        if self.db is None:
            logger.error("Database not connected")
            return None
            
        # Add timestamp if not provided
        if 'created_at' not in feedback_data:
            feedback_data['created_at'] = datetime.datetime.utcnow()
            
        try:
            result = await self.db['feedback'].insert_one(feedback_data)
            feedback_id = str(result.inserted_id)
            logger.info(f"Successfully added feedback with ID: {feedback_id}")
            return feedback_id
            
        except Exception as e:
            logger.error(f"Error adding feedback: {e}")
            return None

    async def get_user_wishlist(self, user_id: str) -> Optional[List[Dict[str, Any]]]:
        """
        Retrieve user's wishlist.
        
        Args:
            user_id (str): User identifier
            
        Returns:
            Optional[List[Dict]]: User's wishlist items, None if error
        """
        if self.db is None:
            logger.error("Database not connected")
            return None
            
        collection_name = f"{user_id}_wishlist"
        
        try:
            cursor = self.db[collection_name].find({})
            wishlist = await cursor.to_list(length=None)
            logger.info(f"Retrieved {len(wishlist)} wishlist items for user {user_id}")
            return wishlist
            
        except Exception as e:
            logger.error(f"Error retrieving wishlist for user {user_id}: {e}")
            return None

    async def add_to_wishlist(self, user_id: str, wishlist_items: List[Dict[str, Any]]) -> Optional[List[str]]:
        """
        Add items to user's wishlist.
        
        Args:
            user_id (str): User identifier
            wishlist_items (List[Dict]): Items to add to wishlist
            
        Returns:
            Optional[List[str]]: List of inserted item IDs, None if error
        """
        collection_name = f"{user_id}_wishlist"
        return await self.insert_documents(collection_name, wishlist_items)

    async def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve user profile information.
        
        Args:
            user_id (str): User identifier
            
        Returns:
            Optional[Dict]: User profile data, None if error or not found
        """
        if self.db is None:
            logger.error("Database not connected")
            return None
            
        try:
            user = await self.db['users'].find_one({"user_id": user_id})
            if user and '_id' in user:
                user['_id'] = str(user['_id'])
            logger.info(f"Retrieved user profile for {user_id}")
            return user
            
        except Exception as e:
            logger.error(f"Error retrieving user profile for {user_id}: {e}")
            return None

    async def create_user_profile(self, user_data: Dict[str, Any]) -> Optional[str]:
        """
        Create a new user profile.
        
        Args:
            user_data (Dict): User profile information
            
        Returns:
            Optional[str]: User ID if successful, None if error
        """
        if self.db is None:
            logger.error("Database not connected")
            return None
            
        # Add timestamp if not provided
        if 'created_at' not in user_data:
            user_data['created_at'] = datetime.datetime.utcnow()
            
        try:
            result = await self.db['users'].insert_one(user_data)
            user_id = str(result.inserted_id)
            logger.info(f"Successfully created user profile with ID: {user_id}")
            return user_id
            
        except Exception as e:
            logger.error(f"Error creating user profile: {e}")
            return None

    async def update_user_profile(self, user_id: str, update_data: Dict[str, Any]) -> bool:
        """
        Update user profile information.
        
        Args:
            user_id (str): User identifier
            update_data (Dict): Data to update
            
        Returns:
            bool: True if successful, False if error
        """
        if self.db is None:
            logger.error("Database not connected")
            return False
            
        update_data['updated_at'] = datetime.datetime.utcnow()
            
        try:
            result = await self.db['users'].update_one(
                {"user_id": user_id},
                {"$set": update_data}
            )
            success = result.modified_count > 0
            if success:
                logger.info(f"Successfully updated user profile for {user_id}")
            else:
                logger.warning(f"No user found with ID {user_id} to update")
            return success
            
        except Exception as e:
            logger.error(f"Error updating user profile for {user_id}: {e}")
            return False

    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - cleanup connection."""
        await self.disconnect()


def create_sample_data():
    """Create sample data for testing."""
    # Sample user profiles
    sample_users = [
        {
            "user_id": "new_user_001",
            "name": "Priya Sharma",
            "phone": "+91-9876543210",
            "email": "priya.sharma@gmail.com",
            "registration_date": datetime.datetime.now() - datetime.timedelta(days=2),
            "customer_type": "new",
            "preferred_language": "hindi",
            "location": "Delhi",
            "created_at": datetime.datetime.utcnow()
        },
        {
            "user_id": "new_user_002", 
            "name": "Rahul Gupta",
            "phone": "+91-8765432109",
            "email": "rahul.gupta@yahoo.com",
            "registration_date": datetime.datetime.now() - datetime.timedelta(days=1),
            "customer_type": "new",
            "preferred_language": "english",
            "location": "Mumbai",
            "created_at": datetime.datetime.utcnow()
        },
        {
            "user_id": "new_user_003",
            "name": "Anjali Singh",
            "phone": "+91-7654321098",
            "email": "anjali.singh@outlook.com",
            "registration_date": datetime.datetime.now() - datetime.timedelta(days=3),
            "customer_type": "new",
            "preferred_language": "hinglish",
            "location": "Bangalore",
            "created_at": datetime.datetime.utcnow()
        },
        {
            "user_id": "repeat_user_001",
            "name": "Meera Joshi",
            "phone": "+91-9123456789",
            "email": "meera.joshi@gmail.com",
            "registration_date": datetime.datetime.now() - datetime.timedelta(days=120),
            "customer_type": "repeat",
            "preferred_language": "hinglish",
            "location": "Pune",
            "total_orders": 4,
            "created_at": datetime.datetime.utcnow()
        }
    ]
    
    sample_wishlist = [
        {
            "product_id": "TW-BT-001",
            "added_date": datetime.datetime(2024, 7, 20, 10, 30, 0),
            "priority": "high",
            "notes": "Love the orange flavor! Perfect for my morning snack",
            "quantity_desired": 2,
            "notification_on_stock": True,
            "notification_on_price_drop": True
        },
        {
            "product_id": "TW-SP-001", 
            "added_date": datetime.datetime(2024, 7, 18, 14, 45, 0),
            "priority": "medium",
            "notes": "Want to try this as a healthier spread option",
            "quantity_desired": 1,
            "notification_on_stock": True,
            "notification_on_price_drop": False
        },
        {
            "product_id": "TW-CM-001",
            "added_date": datetime.datetime(2024, 7, 15, 9, 20, 0), 
            "priority": "low",
            "notes": "Great value combo pack for gifting",
            "quantity_desired": 1,
            "notification_on_stock": False,
            "notification_on_price_drop": True
        },
        {
            "product_id": "TW-BT-003",
            "added_date": datetime.datetime(2024, 7, 22, 16, 15, 0),
            "priority": "high",
            "notes": "Currently out of stock - want to buy when available",
            "quantity_desired": 3,
            "notification_on_stock": True,
            "notification_on_price_drop": False
        }
    ]
    
    sample_products = [
        {
        "product_id": "TW-SP-001",
        "name": "Walnut Brownie Chocolate Spread",
        "category": "Spreads",
        "brand": "Twiddles",
        "price": 299,
        "mrp": 399,
        "size": "100g",
        "description": "Made with 50% California Walnuts + Almonds & Seeds. Rich in Omega-3 and protein.",
        "ingredients": ["California Walnuts", "Almonds", "Seeds", "Dark Chocolate", "Jaggery"],
        "dietary_info": ["No Refined Sugar", "High Protein", "Omega-3 Rich"],
        "image_url": "walnut_brownie_spread.jpg",
        "in_stock": True,
        "rating": 4.8,
        "reviews_count": 245
    },
    {
        "product_id": "TW-SP-002", 
        "name": "Almond Silk Chocolate Spread",
        "category": "Spreads",
        "brand": "Twiddles",
        "price": 279,
        "mrp": 369,
        "size": "100g",
        "description": "Smooth and creamy almond-based chocolate spread with natural sweeteners.",
        "ingredients": ["Almonds", "Dark Chocolate", "Coconut Oil", "Jaggery", "Vanilla"],
        "dietary_info": ["No Refined Sugar", "Gluten Free", "High Protein"],
        "image_url": "almond_silk_spread.jpg",
        "in_stock": True,
        "rating": 4.7,
        "reviews_count": 189
    },
    {
        "product_id": "TW-BT-001",
        "name": "Orange Noir Bites",
        "category": "Bites",
        "brand": "Twiddles",
        "price": 199,
        "mrp": 249,
        "size": "80g",
        "description": "Premium dark chocolate bites infused with natural orange essence and nuts.",
        "ingredients": ["Dark Chocolate", "Orange Zest", "Almonds", "Cashews", "Dates"],
        "dietary_info": ["No Refined Sugar", "Natural Flavors", "Antioxidant Rich"],
        "image_url": "orange_noir_bites.jpg",
        "in_stock": True,
        "rating": 4.9,
        "reviews_count": 312
    },
    {
        "product_id": "TW-BT-002",
        "name": "Chocolate Almond Crunch Bites",
        "category": "Bites", 
        "brand": "Twiddles",
        "price": 229,
        "mrp": 289,
        "size": "90g",
        "description": "Crunchy almond pieces coated in rich dark chocolate. Perfect guilt-free snacking.",
        "ingredients": ["Roasted Almonds", "Dark Chocolate", "Jaggery", "Sea Salt"],
        "dietary_info": ["No Refined Sugar", "High Protein", "Keto Friendly"],
        "image_url": "chocolate_almond_bites.jpg",
        "in_stock": True,
        "rating": 4.6,
        "reviews_count": 156
    },
    {
        "product_id": "TW-BT-003",
        "name": "Mixed Nut Energy Bites",
        "category": "Bites",
        "brand": "Twiddles", 
        "price": 249,
        "mrp": 319,
        "size": "100g",
        "description": "Power-packed energy bites with mixed nuts, seeds and natural sweeteners.",
        "ingredients": ["Almonds", "Walnuts", "Cashews", "Pumpkin Seeds", "Dates", "Coconut"],
        "dietary_info": ["No Refined Sugar", "High Energy", "Protein Rich"],
        "image_url": "mixed_nut_bites.jpg",
        "in_stock": False,
        "rating": 4.5,
        "reviews_count": 98
    },
    {
        "product_id": "TW-SP-003",
        "name": "Hazelnut Crunch Spread",
        "category": "Spreads",
        "brand": "Twiddles",
        "price": 319,
        "mrp": 399,
        "size": "120g",
        "description": "Luxurious hazelnut spread with crunchy pieces and premium chocolate.",
        "ingredients": ["Hazelnuts", "Dark Chocolate", "Coconut Sugar", "Vanilla"],
        "dietary_info": ["No Refined Sugar", "Gluten Free", "Premium Quality"],
        "image_url": "hazelnut_crunch_spread.jpg",
        "in_stock": True,
        "rating": 4.8,
        "reviews_count": 201
    },
    {
        "product_id": "TW-CM-001",
        "name": "Twiddles Combo Pack - Spreads Trio",
        "category": "Combo",
        "brand": "Twiddles",
        "price": 799,
        "mrp": 1167,
        "size": "3x100g",
        "description": "Get all three signature spreads in one combo pack at special price.",
        "ingredients": ["Walnut Brownie", "Almond Silk", "Hazelnut Crunch"],
        "dietary_info": ["No Refined Sugar", "Variety Pack", "Best Value"],
        "image_url": "spreads_combo.jpg",
        "in_stock": True,
        "rating": 4.9,
        "reviews_count": 87
    },
    {
        "product_id": "TW-BT-004",
        "name": "Dark Chocolate Walnut Bites",
        "category": "Bites",
        "brand": "Twiddles",
        "price": 269,
        "mrp": 329,
        "size": "85g",
        "description": "Premium California walnuts covered in 70% dark chocolate.",
        "ingredients": ["California Walnuts", "70% Dark Chocolate", "Coconut Sugar"],
        "dietary_info": ["No Refined Sugar", "Omega-3 Rich", "Antioxidants"],
        "image_url": "dark_chocolate_walnut_bites.jpg",
        "in_stock": True,
        "rating": 4.7,
        "reviews_count": 134
    }
    ]
    return sample_users, sample_wishlist, sample_products


async def main():
    """Main function demonstrating usage."""
    try:
        # Using async context manager for automatic cleanup
        async with TwiddlesDatabase() as db:
            # Create sample data
            sample_users, sample_wishlist, sample_products = create_sample_data()
            
            # Insert sample users
            user_ids = await db.insert_documents("users", sample_users)
            if user_ids:
                print(f"Inserted users with IDs: {user_ids}")
            
            # # Insert sample products
            # product_ids = await db.insert_documents("products", sample_products)
            # if product_ids:
            #     print(f"Inserted products with IDs: {product_ids}")
            
            # # Add items to user wishlist
            # wishlist_ids = await db.add_to_wishlist("user001", sample_wishlist)
            # if wishlist_ids:
            #     print(f"Added wishlist items with IDs: {wishlist_ids}")
            
            # # Retrieve all products
            # products = await db.get_all_products()
            # if products:
            #     print(f"Found {len(products)} products in database")
                
            # # Get user wishlist
            # wishlist = await db.get_user_wishlist("user001")
            # if wishlist:
            #     print(f"User001 has {len(wishlist)} items in wishlist")
                
            # Test user profile retrieval
            user_profile = await db.get_user_profile("new_user_001")
            if user_profile:
                print(f"Retrieved user profile: {user_profile['name']} from {user_profile['location']}")
                
    except Exception as e:
        logger.error(f"Error in main execution: {e}")


if __name__ == "__main__":
    asyncio.run(main())