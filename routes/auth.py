"""
Authentication Blueprint
Handles user login, registration, password hashing, session management, and route protection.
"""

from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from database import db, User

auth_bp = Blueprint('auth', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if request.path.startswith('/api/'):
                return jsonify({"error": "Authentication required"}), 401
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('user_role') != 'Administrator':
            if request.path.startswith('/api/'):
                return jsonify({"error": "Administrator privileges required"}), 403
            flash("Access denied: Administrator privileges required.", "danger")
            return redirect(url_for('dashboard.view_dashboard'))
        return f(*args, **kwargs)
    return decorated_function

import re

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Accept JSON or Form submit
        if request.is_json:
            data = request.get_json()
            email = data.get('email', '').strip().lower()
            password = data.get('password', '')
        else:
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')

        # Validate Email format
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not email or not re.match(email_regex, email):
            err = "Please enter a valid email address."
            if request.is_json:
                return jsonify({"error": err}), 400
            flash(err, "danger")
            return render_template('login.html')

        if not password or len(password) < 4:
            err = "Password must be at least 4 characters long."
            if request.is_json:
                return jsonify({"error": err}), 400
            flash(err, "danger")
            return render_template('login.html')

        user = User.query.filter_by(email=email).first()

        if user:
            # Existing account verification
            if user.check_password(password):
                if not user.is_active:
                    if request.is_json:
                        return jsonify({"error": "Account is disabled. Contact system admin."}), 403
                    flash("Account is disabled. Contact system administrator.", "danger")
                    return render_template('login.html')

                session['user_id'] = user.id
                session['user_name'] = user.name
                session['user_email'] = user.email
                session['user_role'] = user.role

                if request.is_json:
                    return jsonify({
                        "message": "Login successful",
                        "user": user.to_dict(),
                        "redirect": url_for('dashboard.view_dashboard')
                    }), 200
                
                flash(f"Welcome back, {user.name}!", "success")
                next_page = request.args.get('next')
                return redirect(next_page or url_for('dashboard.view_dashboard'))
            else:
                if request.is_json:
                    return jsonify({"error": "Invalid password for existing account."}), 401
                flash("Invalid password for existing account.", "danger")
                return render_template('login.html')
        else:
            # Non-existent email: Automatically create normal Researcher user account
            username_part = email.split('@')[0].replace('.', ' ').replace('_', ' ').title()
            user_name = f"User ({username_part})" if username_part else "New Researcher"

            new_user = User(
                name=user_name,
                email=email,
                role='Researcher',  # Default role: Researcher
                is_active=True
            )
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()

            session['user_id'] = new_user.id
            session['user_name'] = new_user.name
            session['user_email'] = new_user.email
            session['user_role'] = new_user.role

            if request.is_json:
                return jsonify({
                    "message": "Account created automatically. Login successful!",
                    "user": new_user.to_dict(),
                    "redirect": url_for('dashboard.view_dashboard')
                }), 200

            flash(f"Welcome! Account created automatically for {email}.", "success")
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard.view_dashboard'))

    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            name = data.get('name', '').strip()
            email = data.get('email', '').strip().lower()
            password = data.get('password', '')
            confirm_password = data.get('confirm_password', '')
            role = data.get('role', 'Researcher')
        else:
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')
            confirm_password = request.form.get('confirm_password', '')
            role = request.form.get('role', 'Researcher')

        if not name or not email or not password:
            err = "All fields are required."
            if request.is_json:
                return jsonify({"error": err}), 400
            flash(err, "warning")
            return render_template('register.html')

        if password != confirm_password:
            err = "Passwords do not match."
            if request.is_json:
                return jsonify({"error": err}), 400
            flash(err, "warning")
            return render_template('register.html')

        if User.query.filter_by(email=email).first():
            err = "Email address is already registered."
            if request.is_json:
                return jsonify({"error": err}), 400
            flash(err, "warning")
            return render_template('register.html')

        # Limit role registration for non-admins
        valid_roles = ['Environmental Analyst', 'Researcher', 'Administrator']
        if role not in valid_roles:
            role = 'Researcher'

        new_user = User(name=name, email=email, role=role)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        if request.is_json:
            return jsonify({"message": "Registration successful! Please login."}), 201

        flash("Registration successful! You can now log in.", "success")
        return redirect(url_for('auth.login'))

    return render_template('register.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('auth.login'))
