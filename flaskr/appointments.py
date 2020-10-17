from flask import (
    Blueprint,flash, Flask, g, redirect, render_template, request, url_for 
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('bookings', __name__)

@bp.route('/booking')
@login_required
def booking():
    if g.user['admin'] == 1:
        return redirect(url_for('bookings.admin'))
    
    db = get_db()
    bookings = db.execute(
        'SELECT p.id, datetime, booked, reason, patient_id'
        ' FROM bookings p'
        ' WHERE p.patient_id = ?',
        (g.user['id'],)
    ).fetchall()

    return render_template('bookings/booking.html', bookings=bookings)

def delete_outdated_bookingSlots():
    pass

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    db = get_db()

    AvailableBookings = db.execute(
        'SELECT id, datetime, booked'
        ' FROM bookings'
        ' WHERE booked = 0'
    ).fetchall()

    if request.method == 'POST':
        SlotId = request.form.get('dateTime')
        reason = request.form['reason']
        error = None

        if not SlotId:
            error = 'Booking slot is required.'
        elif not reason:
            error = 'Reason is required.'

        if error is not None:
            flash(error)
        else:            
            db.execute(
                'UPDATE bookings SET booked = ?, patient_id = ?, reason = ?'
                ' WHERE id = ?',
                (1, g.user['id'], reason, SlotId)
            )
            db.commit()
            return redirect(url_for('bookings.booking'))

    return render_template('bookings/create.html', AvailableBookings=AvailableBookings)

def get_booking(id, check_author=True):
    booking = get_db().execute(
        'SELECT p.id, dateTime, booked, patient_id, reason, username'
        ' FROM bookings p JOIN user u ON p.patient_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if booking is None:
        abort(404, "Appointment id {0} doesn't exist.")
    
    if check_author and booking['patient_id'] != g.user['id']:
        abort(403)
    
    return booking

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    booking = get_booking(id)

    if request.method == 'POST':
        reason = request.form['reason']
        error = None

        if not reason:
            error = 'Reason is required'
        
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE bookings SET reason = ?'
                ' WHERE id = ?',
                (reason, id)
            )
            db.commit()
            return redirect(url_for('bookings.booking'))

    return render_template('bookings/update.html', booking=booking)

@bp.route('/<int:id>/updateAdmin', methods=('GET', 'POST'))
@login_required
def updateAdmin(id):
    booking = get_booking(id, False)

    if request.method == 'POST':
        reason = request.form['reason']
        error = None

        if not reason:
            error = 'Reason is required'
        
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE bookings SET reason = ?'
                ' WHERE id = ?',
                (reason, id)
            )
            db.commit()
            return redirect(url_for('bookings.booking'))

    return render_template('bookings/update.html', booking=booking)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_booking(id, False)
    db = get_db()
    db.execute(
        'UPDATE bookings SET booked = ?, patient_id = ?, reason = ?'
        ' WHERE id = ?',
        (0, None, None, id)
    )
    db.commit()
    return redirect(url_for('bookings.booking'))

@bp.route('/admin')
@login_required
def admin():
    db = get_db()
    bookings = db.execute(
        'SELECT p.id, datetime, booked, patient_id, reason'
        ' FROM bookings p'
    ).fetchall()

    users = db.execute(
        'SELECT id, firstname, lastname'
        ' FROM user'
    ).fetchall()

    return render_template('bookings/admin.html', bookings=bookings, users=users)

@bp.route('/createSlot', methods=('GET', 'POST'))
@login_required
def createSlot():
    db = get_db()

    if request.method == 'POST':
        dateTime = request.form.get('dateTime')
        error = None

        if not dateTime:
            error = 'Date and Time is required'

        if error is not None:
            flash(error)
        else:
            dateTime = dateTime.replace('T', ' ')
            db.execute(
                'INSERT INTO bookings (datetime, booked)'
                ' VALUES (?, ?)',
                (dateTime, 0)
            )
            db.commit()
            return redirect(url_for('bookings.admin'))

    return render_template('bookings/createSlot.html')

def get_bookingSlot(id):
    booking = get_db().execute(
        'SELECT id'
        ' FROM bookings'
        ' WHERE id = ?',
        (id,)
    ).fetchone()

    if booking is None:
        abort(404, "Appointment id {0} doesn't exist.")
    
    return booking

@bp.route('/<int:id>/deleteSlot', methods=('POST',))
@login_required
def deleteSlot(id):
    get_bookingSlot(id)
    db = get_db()
    db.execute('DELETE FROM bookings WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('bookings.admin'))