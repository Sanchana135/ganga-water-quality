"""
Dashboard UI Navigation Blueprint
Renders template pages and handles user navigation routes.
"""

from flask import Blueprint, render_template, session, redirect, url_for
from routes.auth import login_required, admin_required
from database import Station

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def landing():
    return render_template('index.html')

@dashboard_bp.route('/dashboard')
@login_required
def view_dashboard():
    stations = Station.query.order_by(Station.id).all()
    return render_template('dashboard.html', stations=stations)

@dashboard_bp.route('/monitoring')
@login_required
def view_monitoring():
    stations = Station.query.order_by(Station.id).all()
    return render_template('monitoring.html', stations=stations)

@dashboard_bp.route('/map')
@login_required
def view_map():
    stations = Station.query.order_by(Station.id).all()
    return render_template('map.html', stations=stations)

@dashboard_bp.route('/forecast')
@login_required
def view_forecast():
    stations = Station.query.order_by(Station.id).all()
    return render_template('forecast.html', stations=stations)

@dashboard_bp.route('/satellite')
@login_required
def view_satellite():
    stations = Station.query.order_by(Station.id).all()
    return render_template('satellite.html', stations=stations)

@dashboard_bp.route('/analytics')
@login_required
def view_analytics():
    stations = Station.query.order_by(Station.id).all()
    return render_template('analytics.html', stations=stations)

@dashboard_bp.route('/alerts')
@login_required
def view_alerts():
    stations = Station.query.order_by(Station.id).all()
    return render_template('alerts.html', stations=stations)

@dashboard_bp.route('/history')
@login_required
def view_history():
    stations = Station.query.order_by(Station.id).all()
    return render_template('history.html', stations=stations)

@dashboard_bp.route('/dss')
@login_required
def view_dss():
    stations = Station.query.order_by(Station.id).all()
    return render_template('dss.html', stations=stations)

@dashboard_bp.route('/reports')
@login_required
def view_reports():
    stations = Station.query.order_by(Station.id).all()
    return render_template('reports.html', stations=stations)

@dashboard_bp.route('/upload')
@login_required
def view_upload():
    return render_template('upload.html')

@dashboard_bp.route('/admin')
@login_required
@admin_required
def view_admin():
    stations = Station.query.order_by(Station.id).all()
    return render_template('admin.html', stations=stations)
