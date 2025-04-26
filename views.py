import os 

from werkzeug.utils import secure_filename
from flask import current_app as app
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, Event, Registration
from forms import RegisterForm, LoginForm, EventForm
from werkzeug.security import generate_password_hash, check_password_hash

views = Blueprint('views', __name__)

@views.route('/')
def home():
    events = Event.query.order_by(Event.date.asc()).all()
    return render_template('home.html', events=events)

@views.route('/register', methods=['GET', 'POST'])
def register_user():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        new_user = User(email=form.email.data, name=form.name.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Bruker opprettet! Logg inn nå.')
        return redirect(url_for('views.login'))
    return render_template('register.html', form=form)

@views.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('views.home'))
        flash('Feil e-post eller passord.')
    return render_template('login.html', form=form)

@views.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('views.home'))

@views.route('/create_event', methods=['GET', 'POST'])
@login_required
def create_event():
    form = EventForm()
    if form.validate_on_submit():
        filename = None
        if form.image.data and allowed_file(form.image.data.filename):
            filename = secure_filename(form.image.data.filename)
            upload_path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], filename)
            form.image.data.save(upload_path)

        new_event = Event(
            name=form.name.data,
            description=form.description.data,
            date=form.date.data,
            location=form.location.data,
            image=filename,  # lagre bildefilnavn
            user_id=current_user.id
        )
        db.session.add(new_event)
        db.session.commit()
        flash('Arrangement opprettet!')
        return redirect(url_for('views.my_events'))

    return render_template('create_event.html', form=form)

@views.route('/my-events')
@login_required
def my_events():
    events = Event.query.filter_by(user_id=current_user.id).all()
    return render_template('my_events.html', events=events)

@views.route('/event/<int:event_id>', methods=['GET', 'POST'])
def event_detail(event_id):
    event = Event.query.get_or_404(event_id)
    is_registered = False
    if current_user.is_authenticated:
        is_registered = Registration.query.filter_by(user_id=current_user.id, event_id=event_id).first() is not None
    return render_template('event_detail.html', event=event, is_registered=is_registered)

@views.route('/register/<int:event_id>', methods=['POST'])
@login_required
def register_event(event_id):
    event = Event.query.get_or_404(event_id)
    if Registration.query.filter_by(user_id=current_user.id, event_id=event_id).first() is None:
        registration = Registration(user_id=current_user.id, event_id=event_id)
        db.session.add(registration)
        db.session.commit()
        flash('Du er nå påmeldt!')
    return redirect(url_for('views.event_detail', event_id=event_id))

@views.route('/unregister/<int:event_id>', methods=['POST'])
@login_required
def unregister(event_id):
    registration = Registration.query.filter_by(user_id=current_user.id, event_id=event_id).first()
    if registration:
        db.session.delete(registration)
        db.session.commit()
        flash('Du er nå avmeldt.')
    return redirect(url_for('views.event_detail', event_id=event_id))

@views.route('/edit-event/<int:event_id>', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)
    if event.user_id != current_user.id:
        flash('Du har ikke lov til å redigere dette arrangementet.')
        return redirect(url_for('views.home'))

    form = EventForm(obj=event)
    if form.validate_on_submit():
        event.name = form.name.data
        event.description = form.description.data
        event.date = form.date.data
        event.location = form.location.data
        db.session.commit()
        flash('Arrangementet ble oppdatert!')
        return redirect(url_for('views.my_events'))

    return render_template('edit_event.html', form=form, event=event)

@views.route('/delete-event/<int:event_id>', methods=['POST'])
@login_required
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    if event.user_id != current_user.id:
        flash('Du har ikke lov til å slette dette arrangementet.')
        return redirect(url_for('views.home'))

    # Først slette påmeldinger
    Registration.query.filter_by(event_id=event.id).delete()
    db.session.delete(event)
    db.session.commit()
    flash('Arrangementet ble slettet.')
    return redirect(url_for('views.my_events'))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}