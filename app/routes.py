import os
from app import app, db
from app.forms import RegistrationForm, WellbeingForm, LoginForm
from app.models import WellbeingResponse, Notification, User
from flask import session, json, flash, url_for, redirect, render_template, current_app, request
from sqlalchemy import inspect
from sqlalchemy.exc import IntegrityError, OperationalError
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import current_user, login_user, logout_user, login_required

@app.route("/", methods=["GET", "POST"])
def index():
    '''
    user_id = session.get("user_id")
    daily_averages = {}
    if user_id:
        entries = Wellbeing.query.filter_by(user_id=user_id).all()
        daily_totals = {}
        daily_counts = {}

        for entry in entries:
            date = entry.submitted_on
            row_avg = (entry.stress + entry.sleep + entry.social + entry.academic + entry.activity) / 5

            daily_totals[date] = daily_totals.get(date, 0) + row_avg
            daily_counts[date] = daily_counts.get(date, 0) + 1

        for date in daily_totals:
            daily_averages[date] = round(daily_totals[date] / daily_counts[date], 2)

    return render_template("index.html", daily_scores=daily_averages)
    '''

    return render_template("index.html")

@app.route("/registration", methods=["GET", "POST"])
def registration():

    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = RegistrationForm()
    if form.validate_on_submit(): #Check if the form is submitted and valid
        user = User(
            username=form.username.data,
            email=form.email.data,
            course=form.course.data,
            year_of_study=form.year_of_study.data
        )
        user.set_password(form.password.data)

        try:
            db.session.add(user)
            db.session.commit()
            flash(f"Registration successful")
            return redirect(url_for('login'))
        except IntegrityError:
            db.session.rollback()
            flash(f"User(name) already exists")
            return redirect(url_for('registration'))
    return render_template("registration.html", form=form)

@app.route("/wellbeing", methods=['GET','POST'])
@login_required
def complete():
    form = WellbeingForm()
    if form.validate_on_submit():
        daily_entry = WellbeingResponse(
            date = datetime.now(timezone.utc),
            student_id = current_user.id,
            stress = form.stress.data,
            sleep = form.sleep.data,
            social = form.social.data,
            academic = form.academic.data,
            activity = form.activity.data,
            notes = form.notes.data
        )
        db.session.add(daily_entry)
        db.session.commit()
        score = daily_entry.overall_rating()
        return render_template("score.html", score=score)

    return render_template("wellbeing_form.html", form=form)

@app.before_request
def check_notifications():

    # Ignore static file requests
    if request.endpoint == "static":
        return

    notification = Notification.query.filter_by(read=False).first()

    if notification:
        flash((notification.message, notification.link), "info")
        notification.read = True
        db.session.commit()



@app.route("/login", methods=["GET", "POST"])
def login():

    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data.lower().strip()
        password = form.password.data

        user = User.query.filter_by(email=email).first()

        if not user:
            flash("Invalid email or password.", "danger")
            return render_template("login.html", form=form)

        if not check_password_hash(user.password_hash, password):
            flash("Invalid email or password.", "danger")
            return render_template("login.html", form=form)

        # success
        login_user(user)

        flash(f"Welcome back, {user.username}!", "success")
        return redirect(url_for("complete"))

    return render_template("login.html", form=form)

#Logs users out of the session individually
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))



