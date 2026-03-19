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
    for i in current_user.responses:
        if str(i.date.strftime("%Y-%m-%d")) == str(date.today()):
            flash("Check in form can only be completed once daily, but here are your past stats!")
            return redirect(url_for("tracking"))
    form = WellbeingForm()
    if form.validate_on_submit():
        daily_entry = WellbeingResponse(
            notification_id = 1,
            student_id = current_user.id,
            date = datetime.now(timezone.utc),
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
    print(graph)
    user = current_user.responses
    data = []
    title = None
    for response in user:
        date = response.date.strftime("%d-%m-%Y")
        if graph == "stress":
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
    avg = 0
    for val in values:
        avg += val
    avg = avg/len(values)


    return render_template("tracking.html", labels=labels, values=values, title=title, avg=avg, graph_option=graph )

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





