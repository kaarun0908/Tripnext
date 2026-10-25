from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from urllib.parse import urlsplit
from app.auth import auth_bp
from app.extensions import db
from app.models import User
from app.forms import LoginForm, RegistrationForm

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    reg_form = RegistrationForm()
    if reg_form.validate_on_submit():
        user = User(
            full_name=reg_form.full_name.data.strip(),
            email=reg_form.email.data.strip().lower(),
            phone=reg_form.phone.data.strip() if reg_form.phone.data else None,
            role='customer'
        )
        user.set_password(reg_form.password.data)
        db.session.add(user)
        db.session.commit()

        flash('Registration successful! Please log in to explore destinations and manage bookings.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('login.html', form=form, reg_form=reg_form, active_tab='register')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('main.dashboard'))

    form = LoginForm()
    reg_form = RegistrationForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.strip().lower()).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            flash(f'Welcome back, {user.full_name}!', 'success')

            next_page = request.args.get('next')
            if not next_page or urlsplit(next_page).netloc != '':
                next_page = url_for('admin.dashboard') if user.is_admin else url_for('main.dashboard')
            return redirect(next_page)
        else:
            flash('Invalid email address or password. Please verify your credentials.', 'danger')

    return render_template('login.html', form=form, reg_form=reg_form, active_tab='login')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been securely logged out.', 'info')
    return redirect(url_for('main.index'))
