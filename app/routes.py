import os
from app import app, db
from app.forms import RegistrationForm, WellbeingForm, LoginForm
from app.models import Wellbeing, Notification, User
from flask import session, json, flash, url_for, redirect, render_template, current_app
from sqlalchemy import inspect
from sqlalchemy.exc import IntegrityError, OperationalError
from datetime import datetime, timezone

from werkzeug.security import generate_password_hash, check_password_hash

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
    form = RegistrationForm()
    if form.validate_on_submit(): #Check if the form is submitted and valid
        user = User(
        username = form.username.data,
        email = form.email.data,
        course = form.course.data,
        year_of_study = form.year_of_study.data,
        password = generate_password_hash(form.password.data)
        )
        try:
            db.session.add(user)
            db.session.commit()
            flash(f"Registration successfully")
            return redirect(url_for('index'))
        except IntegrityError:
            db.session.rollback()
            flash(f"User already exists")
            return redirect(url_for('complete'))
    return render_template("registration.html", form=form)

@app.route("/wellbeing", methods=['GET','POST'])
def complete():
    form = WellbeingForm()
    date = datetime.now(timezone.utc).date()
    if form.validate_on_submit():
        daily_entry = Wellbeing(
            stress = form.stress.data,
            sleep = form.sleep.data,
            social = form.social.data,
            academic = form.academic.data,
            activity = form.activity.data,
            notes = form.notes.data,
            date=date
        )
        db.session.add(daily_entry)
        db.session.commit()
        score = daily_entry.overall_rating()
        return render_template("score.html", score=score)

        flash(f"Form submitted, average score: {daily_entry.overall_rating()}")
        return redirect(url_for('index'))

    return render_template("wellbeing_form.html", form=form)

@app.before_request
def check_notifications():
    # Fix for if notification table doesn't exist
    try:
        inspector = inspect(db.engine)

        # If table doesn't exist, do nothing
        if "notification" not in inspector.get_table_names():
            return
        else:
            notification = Notification.query.filter_by(read=False).first()
            flash(notification.message, "info")
            notification.read = True
            db.session.commit()

    except OperationalError:
        return



@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        flash("You are already logged in", "success")
        return redirect(url_for("index"))

    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data.lower().strip()
        password = form.password.data

        user = User.query.filter_by(email=email).first()

        if not user:
            flash("Invalid email or password.", "danger")
            return render_template("login.html", form=form)

        if not check_password_hash(user.password, password):
            flash("Invalid email or password.", "danger")
            return render_template("login.html", form=form)

        # success
        session["user_id"] = user.user_id
        session["username"] = user.username

        flash(f"Welcome back, {user.username}!", "success")
        return redirect(url_for("complete"))

    return render_template("login.html", form=form)

#Logs users out of the session individually
@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))



