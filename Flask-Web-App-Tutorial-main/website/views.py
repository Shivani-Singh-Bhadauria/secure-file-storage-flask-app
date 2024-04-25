from flask import Blueprint, render_template, request, flash, jsonify, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from .forms import UploadForm 
from flask import redirect
from flask import url_for
from .models import Note, File
from . import db
from io import BytesIO
import json
import os

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST': 
        note = request.form.get('note')#Gets the note from the HTML 

        if len(note) < 1:
            flash('Note is too short!', category='error') 
        else:
            new_note = Note(data=note, user_id=current_user.id)  #providing the schema for the note 
            db.session.add(new_note) #adding the note to the database 
            db.session.commit()
            flash('Note Added!', category='success')

    return render_template("home.html", user=current_user)
    
@views.route('/add_file', methods=['GET', 'POST'])
def add_file():
    uploaded_files = None
    if request.method == 'POST': 
        if 'file' not in request.files:
            flash('No file part', category='error')
            return render_template("add_file.html", user=current_user)

        file = request.files['file']

        if file.filename == '':
            flash('No selected file', category='error')
            return render_template("add_file.html", user=current_user)

        if file: 
            new_file = File(name = file.filename, data=file.read(), user_id=current_user.id)  
            db.session.add(new_file)
            db.session.commit()
            flash('File uploaded successfully!', category='success')
            return render_template("add_file.html", user=current_user)
        uploaded_files = Note.query.filter_by(user_id=current_user.id).all()

    return render_template("add_file.html", user=current_user, files=uploaded_files)


@views.route('/delete-note', methods=['POST'])
def delete_note():  
    note = json.loads(request.data) # this function expects a JSON from the INDEX.js file 
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()
            flash('Note Deleted!', category='success')

    return jsonify({})
        


@views.route('/delete-file', methods=['POST'])
def delete_file():  
    file_data = json.loads(request.data) # this function expects a JSON from the INDEX.js file 
    fileId = file_data['fileId']
    file = File.query.get(fileId)
    if file:
        if file.user_id == current_user.id:
            db.session.delete(file)
            db.session.commit()
            flash('File Deleted!', category='success')

    return jsonify({})
