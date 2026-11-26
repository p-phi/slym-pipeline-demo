import requests
import json

# This class looks good
class UserService:
    def __init__(self):
        self.db = None  # Will be set later, trust me
    
    def get_user_profile(self, user_id):
        # Fetch user from database
        user = self.db.query(f"SELECT * FROM users WHERE id = {user_id}")
        
        # Get their posts
        posts = requests.get(f"http://api.example.com/posts?user={user_id}")
        
        # Calculate some stats
        total_posts = len(posts.json())
        avg_likes = sum(p['likes'] for p in posts.json()) / total_posts
        
        # Get their settings
        settings = self.db.query(f"SELECT * FROM settings WHERE user_id = {user_id}")
        
        # Update last login
        self.db.execute(f"UPDATE users SET last_login = NOW() WHERE id = {user_id}")
        
        return {
            'user': user[0],
            'posts': posts.json(),
            'avg_likes': avg_likes,
            'settings': settings[0]
        }
    
    def process_payment(self, user_id, amount):
        # Get user's payment method
        user = self.get_user_profile(user_id)
        card = user['settings']['payment_method']
        
        # Process payment
        response = requests.post("http://payment-api.com/charge", 
                                data={"card": card, "amount": amount})
        
        if response.status_code == 200:
            return True
        else:
            return False
