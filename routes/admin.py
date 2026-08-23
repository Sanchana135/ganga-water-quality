"""
Admin Management Blueprint
Provides endpoints for Administrator operations: user management, station maintenance, system activity log.
"""

from flask import Blueprint, jsonify, request, session
from database import db, User, Station, SensorReading, Alert
from routes.auth import login_required, admin_required

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

@admin_bp.route('/users', methods=['GET'])
@login_required
@admin_required
def list_users():
    users = User.query.order_by(User.id).all()
    return jsonify([u.to_dict() for u in users])

@admin_bp.route('/users/<int:user_id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_user_active(user_id):
    usr = User.query.get_or_404(user_id)
    if usr.id == session.get('user_id'):
        return jsonify({"error": "Cannot disable your own logged-in account"}), 400
    usr.is_active = not usr.is_active
    db.session.commit()
    return jsonify({"message": f"User status updated to {'Active' if usr.is_active else 'Disabled'}", "user": usr.to_dict()})

@admin_bp.route('/users/<int:user_id>/role', methods=['POST'])
@login_required
@admin_required
def update_user_role(user_id):
    data = request.get_json() or {}
    new_role = data.get('role')
    if new_role not in ['Administrator', 'Environmental Analyst', 'Researcher']:
        return jsonify({"error": "Invalid role specified"}), 400

    usr = User.query.get_or_404(user_id)
    usr.role = new_role
    db.session.commit()
    return jsonify({"message": f"User role updated to {new_role}", "user": usr.to_dict()})

@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_user(user_id):
    usr = User.query.get_or_404(user_id)
    if usr.id == session.get('user_id'):
        return jsonify({"error": "Cannot delete your own logged-in account"}), 400

    db.session.delete(usr)
    db.session.commit()
    return jsonify({"message": f"User #{user_id} deleted successfully"})

@admin_bp.route('/stations', methods=['POST'])
@login_required
@admin_required
def add_station():
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    lat = float(data.get('latitude', 0.0))
    lng = float(data.get('longitude', 0.0))
    loc = data.get('location', '').strip()

    if not name or not loc:
        return jsonify({"error": "Station name and location are required"}), 400

    st = Station(name=name, latitude=lat, longitude=lng, location=loc, status='ACTIVE')
    db.session.add(st)
    db.session.commit()
    return jsonify({"message": f"Monitoring station '{name}' added successfully", "station": st.to_dict()}), 201

@admin_bp.route('/stations/<int:station_id>', methods=['PUT'])
@login_required
@admin_required
def edit_station(station_id):
    st = Station.query.get_or_404(station_id)
    data = request.get_json() or {}

    if 'name' in data:
        st.name = data['name'].strip()
    if 'latitude' in data:
        st.latitude = float(data['latitude'])
    if 'longitude' in data:
        st.longitude = float(data['longitude'])
    if 'location' in data:
        st.location = data['location'].strip()
    if 'status' in data:
        st.status = data['status']

    db.session.commit()
    return jsonify({"message": f"Station #{station_id} updated successfully", "station": st.to_dict()})
