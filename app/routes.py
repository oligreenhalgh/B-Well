import os
from time import strftime
from unicodedata import category

from app import app, db
from app.forms import RegistrationForm, WellbeingForm, LoginForm, ResourceForm
from app.models import WellbeingResponse, Notification, User, Resource
from flask import session, json, flash, url_for, redirect, render_template, current_app, request
from sqlalchemy import inspect
from sqlalchemy.exc import IntegrityError, OperationalError
from datetime import datetime, timezone, date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import current_user, login_user, logout_user, login_required

@app.route("/", methods=["GET", "POST"])
def index():
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
        )
        user.set_password(form.password.data)

        if form.email.data[-11:] == "@bham.ac.uk":
            user.is_admin = True

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

@app.route("/wellbeing", methods=['GET', 'POST'])
@login_required
def complete():
    from datetime import datetime, timezone
    import sqlalchemy as sa

    today = datetime.now(timezone.utc).date()

    notification = Notification.query.filter(
        Notification.student_id == current_user.id,
        Notification.type == "daily",
        sa.func.date(Notification.created_at) == today
    ).first()

    if not notification:
        return redirect(url_for("index"))

    existing = WellbeingResponse.query.filter_by(
        notification_id=notification.notification_id
    ).first()

    if existing:
        flash("Check in already completed today. Here are your stats!")
        return redirect(url_for("tracking"))

    form = WellbeingForm()

    if form.validate_on_submit():
        daily_entry = WellbeingResponse(
            notification_id=notification.notification_id,
            student_id=current_user.id,
            date=datetime.now(timezone.utc),
            stress=form.stress.data,
            sleep=form.sleep.data,
            social=form.social.data,
            academic=form.academic.data,
            activity=form.activity.data,
            notes=form.notes.data
        )

        db.session.add(daily_entry)

        # Mark notification as read (optional but nice)
        notification.read = True

        db.session.commit()

        score = daily_entry.overall_rating()
        return render_template("score.html", score=score)

    return render_template("wellbeing_form.html", form=form)

@app.before_request
def check_notifications():

    if request.endpoint == "static":
        return

    if not current_user.is_authenticated:
        return

    notification = Notification.query.filter_by(
        student_id=current_user.id,
        read=False
    ).first()

    if notification:
        flash((notification.message, notification.link), "info")
        notification.read = True
        db.session.commit()



@app.route("/login", methods=["GET", "POST"])
def login():

    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('add_resources'))
        return redirect(url_for('index'))

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
        if user.is_admin:
            return redirect(url_for('add_resources'))
        else:
            return redirect(url_for('index'))

        flash(f"Welcome back, {user.username}!", "success")
        return redirect(url_for("complete"))

    return render_template("login.html", form=form)

#Logs users out of the session individually
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/tracking", methods=['GET','POST'])
@login_required
def tracking():

    if current_user.is_admin:
        return redirect(url_for('index'))

    graph = request.args.get("graph_options", "stress")

    user_responses = current_user.responses

    data = []
    title = None

    for response in user_responses:
        date = response.date.strftime("%d-%m-%Y")

        if graph =="average":
            avg = (response.sleep + response.sleep + response.academic + response.stress + response.social)/5
            data.append((date, avg))
            title = "Average Scores over Time"
        elif graph == "stress":
            data.append((date, response.stress))
            title = "Stress Score over Time"
        elif graph == "sleep":
            data.append((date, response.sleep))
            title = "Sleep Score over Time"
        elif graph == "social":
            data.append((date, response.social))
            title = "Social Score over Time"
        elif graph == "academic":
            title = "Academic Score over Time"
            data.append((date, response.academic))
        elif graph == "activity":
            title = "Activity Score over Time"
            data.append((date, response.activity))
        else:
            title = "Sleep Score over Time"
            data.append((date, response.sleep))

    labels = [row[0] for row in data]
    values = [row[1] for row in data]

    avg = sum(values) / len(values) if values else 0

    LOW_THRESHOLD = 2

    totals = {
        "stress": 0,
        "sleep": 0,
        "social": 0,
        "academic": 0,
        "activity": 0
              }

    count = len(user_responses)

    for r in user_responses:
        totals["stress"] += r.stress
        totals["sleep"] += r.sleep
        totals["social"] += r.social
        totals["academic"] += r.academic
        totals["activity"] += r.activity

    averages = {
        k: (totals[k] / count) if count > 0 else 0
        for k in totals
    }

    low_categories = [
        k for k, v in averages.items()
        if v <= LOW_THRESHOLD
    ]

    if low_categories:
        resources = Resource.query.filter(
            Resource.category.in_(low_categories)
        ).all()
    else:
        resources = []

    return render_template("tracking.html", labels=labels, values=values, title=title, avg=avg, graph_option=graph, resources = resources, low_categories=low_categories )

@app.route("/admin/resources", methods=['GET', 'POST'])
@login_required
def add_resources():
    if not current_user.is_admin:
        return redirect(url_for('index'))

    resources = Resource.query.order_by(Resource.title).all()

    form = ResourceForm()

    if form.validate_on_submit():
        resource = Resource(
            title = form.title.data,
            category = form.category.data,
            url = form.url.data
        )
        db.session.add(resource)
        db.session.commit()
        flash('You have added a resource')
        return redirect(url_for('add_resources'))
    return render_template('resources.html', form=form, resources=resources)


@app.route('/admin/resources/update/<int:resource_id>', methods=['GET', 'POST'])
@login_required
def update_resource(resource_id):
    if not current_user.is_admin:
        return redirect(url_for('index'))
    resource = Resource.query.get_or_404(resource_id)
    resources = Resource.query.order_by(Resource.title).all()
    form = ResourceForm(obj=resource)

    if form.validate_on_submit():
        resource.title = form.title.data
        resource.category = form.category.data
        resource.url = form.url.data
        db.session.commit()
        flash(f'You have successfully changed the resource')
        return redirect(url_for('add_resources'))

    return render_template('resources.html', form=form, resources=resources)

@app.route('/admin/resources/deleting/<int:resource_id>', methods=['GET', 'POST'])
@login_required
def delete_resource(resource_id):
    if not current_user.is_admin:
        return redirect(url_for('index'))

    resource = Resource.query.get_or_404(resource_id)
    db.session.delete(resource)
    db.session.commit()
    flash('You have successfully deleted the resource')
    return redirect(url_for('add_resources'))

from app.models import User


