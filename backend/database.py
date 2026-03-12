import os
from pymongo import MongoClient
from datetime import datetime, timedelta
import gridfs
import hashlib
import io
import uuid
from typing import Dict, Any

# MongoDB connection
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/fracture_detection')
client = MongoClient(MONGO_URI)
db = client.fracture_detection

# Fallback in-memory store for development when MongoDB is unavailable
_use_memory_store = False
_mem_users: Dict[str, Dict[str, Any]] = {}
_mem_reports: Dict[str, Dict[str, Any]] = {}
_mem_images: Dict[str, bytes] = {}

def _enable_memory_store_due_to_error(e: Exception):
    global _use_memory_store
    # Switch to memory store on first DB error
    _use_memory_store = True

# Collections
users_collection = db.users
reports_collection = db.reports
images_collection = db.images

# GridFS for storing images
fs = gridfs.GridFS(db)

def hash_password(password):
    """Hash a password for storing."""
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(name, email, password, phone="", age=""):
    """Register a new user in MongoDB."""
    if _use_memory_store:
        if email in _mem_users:
            return False, "User already exists"
        hashed_password = hash_password(password)
        user_data = {
            'name': name,
            'email': email,
            'password': hashed_password,
            'phone': phone,
            'age': age,
            'created_at': datetime.now()
        }
        _mem_users[email] = user_data
        return True, "User registered successfully"
    try:
        if users_collection.find_one({"email": email}):
            return False, "User already exists"
        hashed_password = hash_password(password)
        user_data = {
            'name': name,
            'email': email,
            'password': hashed_password,
            'phone': phone,
            'age': age,
            'created_at': datetime.now()
        }
        users_collection.insert_one(user_data)
        return True, "User registered successfully"
    except Exception as e:
        _enable_memory_store_due_to_error(e)
        return register_user(name, email, password, phone, age)

def authenticate_user(email, password):
    """Authenticate a user from MongoDB."""
    if _use_memory_store:
        user = _mem_users.get(email)
        if not user:
            return False, "User not found"
        hashed_password = hash_password(password)
        if user['password'] != hashed_password:
            return False, "Invalid password"
        return True, "Authentication successful"
    try:
        user = users_collection.find_one({"email": email})
        if not user:
            return False, "User not found"
        hashed_password = hash_password(password)
        if user['password'] != hashed_password:
            return False, "Invalid password"
        return True, "Authentication successful"
    except Exception as e:
        _enable_memory_store_due_to_error(e)
        return authenticate_user(email, password)

def get_user_details(email):
    """Get user details from MongoDB (excluding password)."""
    if _use_memory_store:
        user = _mem_users.get(email)
        if not user:
            return None
        sanitized = dict(user)
        sanitized.pop('password', None)
        sanitized['_id'] = f"mem_{hashlib.md5(email.encode()).hexdigest()}"
        return sanitized
    try:
        user = users_collection.find_one({"email": email})
        if not user:
            return None
        user.pop('password', None)
        user['_id'] = str(user['_id'])
        return user
    except Exception as e:
        _enable_memory_store_due_to_error(e)
        return get_user_details(email)

def save_report(user_email, report_data, image_data=None):
    """Save a report to MongoDB."""
    if _use_memory_store:
        report_id = str(uuid.uuid4())
        doc = {
            '_id': report_id,
            'user_email': user_email,
            'report_data': report_data,
            'created_at': datetime.now()
        }
        if image_data:
            image_id = str(uuid.uuid4())
            _mem_images[image_id] = image_data
            doc['image_id'] = image_id
        _mem_reports[report_id] = doc
        return report_id
    try:
        report_doc = {
            'user_email': user_email,
            'report_data': report_data,
            'created_at': datetime.now()
        }
        if image_data:
            image_id = fs.put(image_data, filename=f"{user_email}_{datetime.now().isoformat()}.jpg")
            report_doc['image_id'] = image_id
        result = reports_collection.insert_one(report_doc)
        return str(result.inserted_id)
    except Exception as e:
        _enable_memory_store_due_to_error(e)
        return save_report(user_email, report_data, image_data)

def get_user_reports(user_email):
    """Get all reports for a user."""
    if _use_memory_store:
        reports = [r for r in _mem_reports.values() if r['user_email'] == user_email]
        reports.sort(key=lambda r: r['created_at'], reverse=True)
        return reports
    try:
        reports = reports_collection.find({"user_email": user_email}).sort("created_at", -1)
        report_list = []
        for report in reports:
            report['_id'] = str(report['_id'])
            if 'image_id' in report:
                report['image_id'] = str(report['image_id'])
            report_list.append(report)
        return report_list
    except Exception as e:
        _enable_memory_store_due_to_error(e)
        return get_user_reports(user_email)

def get_report_by_id(report_id):
    """Get a specific report by ID."""
    if _use_memory_store:
        return _mem_reports.get(report_id)
    from bson import ObjectId
    try:
        report = reports_collection.find_one({"_id": ObjectId(report_id)})
        if report:
            report['_id'] = str(report['_id'])
            if 'image_id' in report:
                report['image_id'] = str(report['image_id'])
        return report
    except Exception as e:
        _enable_memory_store_due_to_error(e)
        return get_report_by_id(report_id)

def get_image_by_id(image_id):
    """Get an image by ID from GridFS."""
    if _use_memory_store:
        data = _mem_images.get(image_id)
        if data is None:
            return None
        return io.BytesIO(data)
    from bson import ObjectId
    try:
        return fs.get(ObjectId(image_id))
    except Exception as e:
        _enable_memory_store_due_to_error(e)
        return get_image_by_id(image_id)


def get_analytics_summary(days: int = 30):
        """Compute high-level analytics over recent reports.

        Returns a dict with:
            - total_scans
            - scans_per_day: list of {date, count}
            - fracture_rate
            - average_confidence
            - body_region_distribution: list of {region, count}
        """
        now = datetime.now()
        since = now - timedelta(days=days)

        # Collect reports from either memory store or MongoDB
        if _use_memory_store:
            reports = [r for r in _mem_reports.values() if r.get('created_at') and r['created_at'] >= since]
        else:
            try:
                cursor = reports_collection.find({"created_at": {"$gte": since}})
                reports = list(cursor)
            except Exception as e:
                _enable_memory_store_due_to_error(e)
                reports = [r for r in _mem_reports.values() if r.get('created_at') and r['created_at'] >= since]

        total = len(reports)
        if total == 0:
            return {
                'total_scans': 0,
                'scans_per_day': [],
                'fracture_rate': 0.0,
                'average_confidence': 0.0,
                'body_region_distribution': [],
                'window_days': days,
            }

        scans_per_day = {}
        fracture_count = 0
        confidence_sum = 0.0
        confidence_count = 0
        region_counts = {}

        for r in reports:
            created_at = r.get('created_at', now)
            if isinstance(created_at, datetime):
                day_key = created_at.strftime('%Y-%m-%d')
            else:
                # Fallback if stored as string
                day_key = str(created_at)[:10]
            scans_per_day[day_key] = scans_per_day.get(day_key, 0) + 1

            data = r.get('report_data', {}) or {}
            if data.get('fracture_detected'):
                fracture_count += 1

            conf = data.get('confidence')
            try:
                if conf is not None:
                    confidence_sum += float(conf)
                    confidence_count += 1
            except Exception:
                pass

            region = data.get('body_region') or 'Unknown'
            region_counts[region] = region_counts.get(region, 0) + 1

        scans_per_day_list = [
            {'date': d, 'count': scans_per_day[d]}
            for d in sorted(scans_per_day.keys())
        ]

        fracture_rate = fracture_count / total if total else 0.0
        avg_conf = (confidence_sum / confidence_count) if confidence_count else 0.0

        body_region_distribution = [
            {'region': k, 'count': v}
            for k, v in sorted(region_counts.items(), key=lambda kv: kv[1], reverse=True)
        ]

        return {
            'total_scans': total,
            'scans_per_day': scans_per_day_list,
            'fracture_rate': fracture_rate,
            'average_confidence': avg_conf,
            'body_region_distribution': body_region_distribution,
            'window_days': days,
        }