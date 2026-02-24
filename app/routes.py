import os
from app import app, db
from app.forms import RegistrationForm, WellbeingForm
from app.models import Wellbeing
from flask import session, json, flash, url_for, redirect, render_template, current_app

@app.route("/", methods=["GET", "POST"]) #Route for page with registration and log in links
def index():
    return render_template("index.html")

@app.route("/registration", methods=["GET", "POST"])
def registration():
    form = RegistrationForm()
    if form.validate_on_submit(): #Check if the form is submitted and valid
        #TO-DO: Store user data in database (use security measures for password)
        flash(f"Registration successful")
        return redirect(url_for("index")) #TO-DO: Change this to redirect to home page once created
    return render_template("registration.html", form=form)

@app.route("/wellbeing", methods=['GET','POST'])
def complete():
    form = WellbeingForm()
    if form.validate_on_submit():
        daily_entry = Wellbeing(
            stress = form.stress.data,
            sleep = form.sleep.data,
            social = form.social.data,
            academic = form.academic.data,
            activity = form.activity.data,
            notes = form.notes.data
        )

        db.session.add(daily_entry)
        db.session.commit()

        flash(f"Form submitted")
        return redirect(url_for('complete'))

    return render_template("wellbeing_form.html", form=form)
