import os
import base64

from flask import Flask, render_template, request, redirect, url_for, session

from model import Donation

app = Flask(__name__)


@app.route('/')
def home():
    return redirect(url_for('all'))


@app.route('/donations/')
def all():
    donations = Donation.select()
    return render_template('donations.jinja2', donations=donations)


@app.route('/create/', methods=['GET', 'POST'])
def create():
        # If the handler receives a POST request (a form submission),
        # then it should attempt to retrieve the name of the donor and
        # the amount of the donation from the form submission.
        # It should retrieve the donor from the database with the
        # indicated name, and create a new donation with the indicated
        # donor and donation amount. Then it should redirect
        # the visitor to the home page.
    if request.method == 'POST':
       # Donation.update(value=request.form['value'])\
       #         .where(Donation.donor == request.form['donor'])\
       #         .execute()
       donation = Donation(value=request.form['value'], donor=request.form['donor'])
       donation.save()
       return(redirect(url_for('all')))

    # If the handler receives a GET request, then it should render
    # the template for the donation creation page.
    return render_template('create.jinja2')


if __name__ == "__main__":

    port = int(os.environ.get("PORT", 6738))
    app.run(host='0.0.0.0', port=port)

