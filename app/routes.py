import random

from app import app, db
from app.forms import RegistrationForm, WellbeingForm, LoginForm, ResourceForm
from app.models import WellbeingResponse, Notification, User, Resource
from flask import flash, url_for, redirect, render_template, request
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash
from flask_login import current_user, login_user, logout_user, login_required

@app.route("/home", methods=["GET", "POST"])
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
        flash(" Daily check-in not yet available. Please check back later! ", "success")
        return redirect(url_for("tracking"))

    existing = WellbeingResponse.query.filter_by(
        notification_id=notification.notification_id
    ).first()

    if existing:
        flash(" Check in already completed today. Here are your stats! ", "success")
        return redirect(url_for("tracking"))

    form = WellbeingForm()

    if form.validate_on_submit():

        stress = form.stress.data
        sleep = form.sleep.data
        social = form.social.data
        academic = form.academic.data
        activity = form.activity.data

        daily_entry = WellbeingResponse(
            notification_id=notification.notification_id,
            student_id=current_user.id,
            date=datetime.now(timezone.utc),
            stress=stress,
            sleep=sleep,
            social=social,
            academic=academic,
            activity=activity,
            notes=form.notes.data
        )

        db.session.add(daily_entry)
        db.session.commit()

        notification.read = True

        score = daily_entry.overall_rating()

        LOW_THRESHOLD = 3

        low_cats = []
        if stress < LOW_THRESHOLD:
            low_cats.append("stress")
        if sleep < LOW_THRESHOLD:
            low_cats.append("sleep")
        if social < LOW_THRESHOLD:
            low_cats.append("social")
        if academic < LOW_THRESHOLD:
            low_cats.append("academic")
        if activity < LOW_THRESHOLD:
            low_cats.append("activity")

        random_resources_lst = []
        for cat in low_cats:
            all_cat_resources = Resource.query.filter(Resource.category == cat).all()
            if all_cat_resources:
                random_resource = random.choice(all_cat_resources)
                random_resources_lst.append(random_resource)

        if len(random_resources_lst) == 0:
            random_resources_lst = None

        return render_template("score.html", score=score, resources = random_resources_lst, low_categories=low_cats)

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



@app.route("/", methods=["GET", "POST"])
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

        if not user or not check_password_hash(user.password_hash, password):
            flash("Invalid email or password.", "danger")
            return redirect(url_for("login", form=form))

        login_user(user)
        flash(f"Welcome back {user.username}!", "success")
        if user.is_admin:
            return redirect(url_for('add_resources'))
        else:
            return redirect(url_for('index'))

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
        return redirect(url_for('/admin/resources'))

    graph = request.args.get("graph_options", "stress")

    user_responses = current_user.responses

    data = []
    title = None

    for response in user_responses:
        date = response.date.strftime("%d-%m-%Y")

        if graph =="average":
            avg = round((response.sleep + response.sleep + response.academic + response.stress + response.social)/5, 2)
            data.append((date, avg))
            title = "Average Score Over Time"
        elif graph == "stress":
            data.append((date, response.stress))
            title = "Stress Score Over Time"
        elif graph == "sleep":
            data.append((date, response.sleep))
            title = "Sleep Score Over Time"
        elif graph == "social":
            data.append((date, response.social))
            title = "Social Score Over Time"
        elif graph == "academic":
            title = "Academic Score Over Time"
            data.append((date, response.academic))
        elif graph == "activity":
            title = "Activity Score Over Time"
            data.append((date, response.activity))

    labels = [row[0] for row in data]
    values = [row[1] for row in data]

    avg = round(sum(values) / len(values),2) if values else 0

    return render_template("tracking.html", labels=labels, values=values, title=title, avg=avg, graph_option=graph)

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