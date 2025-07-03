import logging
import hashlib
import time
from datetime import datetime, timedelta
from pymongo import MongoClient
from flask import session
import os
from config import Config

class UserService:
    def __init__(self):
        self.client = None
        self.db = None
        self.users_collection = None
        self.points_collection = None
        self.achievements_collection = None
        self._init_database()
    
    def _init_database(self):
        """Initialize database connection for user service"""
        try:
            # Use a simple local database for user data
            self.client = MongoClient('mongodb://localhost:27017/')
            self.db = self.client['search_engine_users']
            self.users_collection = self.db['users']
            self.points_collection = self.db['user_points']
            self.achievements_collection = self.db['achievements']
            
            # Create indexes
            self.users_collection.create_index('user_id', unique=True)
            self.points_collection.create_index('user_id')
            self.achievements_collection.create_index('user_id')
            
            logging.info("User service database initialized successfully")
        except Exception as e:
            logging.error(f"Error initializing user service database: {e}")
            # Fallback to session-based storage
            self.client = None
            self.db = None
    
    def get_or_create_user(self, user_identifier=None):
        """Get or create a user based on session or identifier"""
        if user_identifier is None:
            # Generate user ID from session
            user_identifier = session.get('user_id')
            if not user_identifier:
                # Create new user ID
                user_identifier = hashlib.md5(f"{time.time()}_{session.get('_id', 'anonymous')}".encode()).hexdigest()
                session['user_id'] = user_identifier
        
        if self.db is None:
            # Use session-based storage
            if 'user_profile' not in session:
                session['user_profile'] = {
                    'user_id': user_identifier,
                    'created_at': datetime.now().isoformat(),
                    'total_points': 0,
                    'level': 1,
                    'searches_count': 0,
                    'ai_queries_count': 0,
                    'achievements': []
                }
            return session['user_profile']
        
        # Database storage
        user = self.users_collection.find_one({'user_id': user_identifier})
        if not user:
            user = {
                'user_id': user_identifier,
                'created_at': datetime.now(),
                'total_points': 0,
                'level': 1,
                'searches_count': 0,
                'ai_queries_count': 0,
                'achievements': []
            }
            self.users_collection.insert_one(user)
        
        return user
    
    def add_points(self, user_id, points, activity_type, description=""):
        """Add points to user and check for achievements"""
        if self.db is None:
            # Session-based storage
            if 'user_profile' not in session:
                self.get_or_create_user(user_id)
            
            session['user_profile']['total_points'] += points
            session['user_profile']['level'] = self._calculate_level(session['user_profile']['total_points'])
            
            # Track activity
            if activity_type == 'search':
                session['user_profile']['searches_count'] += 1
            elif activity_type == 'ai_query':
                session['user_profile']['ai_queries_count'] += 1
            
            # Check achievements
            self._check_achievements(session['user_profile'])
            session.modified = True
            return session['user_profile']['total_points']
        
        # Database storage
        user = self.get_or_create_user(user_id)
        new_total = user['total_points'] + points
        new_level = self._calculate_level(new_total)
        
        # Update user stats
        update_data = {
            'total_points': new_total,
            'level': new_level,
            'last_activity': datetime.now()
        }
        
        if activity_type == 'search':
            update_data['searches_count'] = user.get('searches_count', 0) + 1
        elif activity_type == 'ai_query':
            update_data['ai_queries_count'] = user.get('ai_queries_count', 0) + 1
        
        self.users_collection.update_one(
            {'user_id': user_id},
            {'$set': update_data}
        )
        
        # Record point transaction
        self.points_collection.insert_one({
            'user_id': user_id,
            'points': points,
            'activity_type': activity_type,
            'description': description,
            'timestamp': datetime.now()
        })
        
        # Check achievements
        updated_user = self.users_collection.find_one({'user_id': user_id})
        self._check_achievements(updated_user)
        
        return new_total
    
    def _calculate_level(self, points):
        """Calculate user level based on points"""
        if points < 100:
            return 1
        elif points < 500:
            return 2
        elif points < 1000:
            return 3
        elif points < 2500:
            return 4
        elif points < 5000:
            return 5
        else:
            return 6 + (points - 5000) // 2500
    
    def _check_achievements(self, user):
        """Check and award achievements"""
        achievements = [
            {'id': 'first_search', 'name': 'First Search', 'description': 'Performed your first search', 'condition': lambda u: u.get('searches_count', 0) >= 1},
            {'id': 'search_explorer', 'name': 'Search Explorer', 'description': 'Performed 10 searches', 'condition': lambda u: u.get('searches_count', 0) >= 10},
            {'id': 'search_master', 'name': 'Search Master', 'description': 'Performed 50 searches', 'condition': lambda u: u.get('searches_count', 0) >= 50},
            {'id': 'ai_curious', 'name': 'AI Curious', 'description': 'Asked your first AI question', 'condition': lambda u: u.get('ai_queries_count', 0) >= 1},
            {'id': 'ai_enthusiast', 'name': 'AI Enthusiast', 'description': 'Asked 20 AI questions', 'condition': lambda u: u.get('ai_queries_count', 0) >= 20},
            {'id': 'point_collector', 'name': 'Point Collector', 'description': 'Earned 100 points', 'condition': lambda u: u.get('total_points', 0) >= 100},
            {'id': 'level_up', 'name': 'Level Up', 'description': 'Reached level 3', 'condition': lambda u: u.get('level', 1) >= 3},
        ]
        
        current_achievements = user.get('achievements', [])
        new_achievements = []
        
        for achievement in achievements:
            if achievement['id'] not in current_achievements and achievement['condition'](user):
                new_achievements.append(achievement['id'])
                current_achievements.append(achievement['id'])
        
        if new_achievements:
            if self.db is None:
                session['user_profile']['achievements'] = current_achievements
                session.modified = True
            else:
                self.users_collection.update_one(
                    {'user_id': user['user_id']},
                    {'$set': {'achievements': current_achievements}}
                )
        
        return new_achievements
    
    def get_user_stats(self, user_id):
        """Get user statistics"""
        user = self.get_or_create_user(user_id)
        
        return {
            'total_points': user.get('total_points', 0),
            'level': user.get('level', 1),
            'searches_count': user.get('searches_count', 0),
            'ai_queries_count': user.get('ai_queries_count', 0),
            'achievements': user.get('achievements', []),
            'next_level_points': self._get_next_level_points(user.get('total_points', 0))
        }
    
    def _get_next_level_points(self, current_points):
        """Calculate points needed for next level"""
        current_level = self._calculate_level(current_points)
        level_thresholds = [0, 100, 500, 1000, 2500, 5000]
        
        if current_level <= len(level_thresholds):
            return level_thresholds[current_level] if current_level < len(level_thresholds) else 5000 + (current_level - 5) * 2500
        else:
            return 5000 + (current_level - 4) * 2500
    
    def get_leaderboard(self, limit=10):
        """Get leaderboard of top users"""
        if self.db is None:
            # Cannot provide leaderboard without database
            return []
        
        return list(self.users_collection.find(
            {},
            {'user_id': 1, 'total_points': 1, 'level': 1}
        ).sort('total_points', -1).limit(limit))

# Point values for different activities
POINT_VALUES = {
    'search': 5,
    'ai_query': 10,
    'website_chat': 8,
    'daily_login': 2,
    'feature_discovery': 15
}

# Create global instance
user_service = UserService()