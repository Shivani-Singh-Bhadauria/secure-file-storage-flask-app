from flask import Blueprint, render_template, request, flash, jsonify, make_response
from flask_login import login_required, current_user
from .models import Note, File, User
from . import db
import json
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Random import get_random_bytes
from Crypto.PublicKey import RSA

views = Blueprint('views', __name__)


# Encryption function using RSA
def encrypt_with_RSA(data, user_id):
    recipient = User.query.get(user_id)
    public_key = RSA.import_key(recipient.public_key)
    cipher_rsa = PKCS1_OAEP.new(public_key)
    encrypted_data = cipher_rsa.encrypt(data)
    return encrypted_data


# Decryption function using RSA
def decrypt_with_RSA(encrypted_data):
    user = User.query.get(current_user.id)
    private_key = RSA.import_key(user.private_key)
    cipher_rsa = PKCS1_OAEP.new(private_key)
    decrypted_data = cipher_rsa.decrypt(encrypted_data)
    return decrypted_data


# Generate a random encryption key for AES
def generate_aes_key():
    return get_random_bytes(16)  # 16 bytes for AES-128

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
            # Generate AES key
            aes_key = generate_aes_key()

            # Encrypt file data with AES
            cipher_aes = AES.new(aes_key, AES.MODE_EAX)
            ciphertext, tag = cipher_aes.encrypt_and_digest(file.read())
            nonce = cipher_aes.nonce

            # Encrypt AES key with RSA
            encrypted_aes_key = encrypt_with_RSA(aes_key, current_user.id)

            new_file = File(name=file.filename, data=ciphertext, tag=tag, nonce=nonce, encrypted_aes_key=encrypted_aes_key, user_id=current_user.id)
            db.session.add(new_file)
            db.session.commit()
            flash('File uploaded successfully!', category='success')

            return render_template("add_file.html", user=current_user)
        uploaded_files = Note.query.filter_by(user_id=current_user.id).all()

    return render_template("add_file.html", user=current_user, files=uploaded_files)

@views.route('/download_file/<int:file_id>', methods=['GET'])
def download_file(file_id):
    file = File.query.get_or_404(file_id)

    # Decrypt AES key with RSA
    aes_key = decrypt_with_RSA(file.encrypted_aes_key)

    # Decrypt file data with AES
    cipher_aes = AES.new(aes_key, AES.MODE_EAX, nonce=file.nonce)
    decrypted_data = cipher_aes.decrypt_and_verify(file.data, file.tag)

    response = make_response(decrypted_data)
    response.headers['Content-Disposition'] = f'attachment; filename="{file.name}"'
    return response


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

@views.route('/about')
def about():
    return render_template('about.html', user=current_user)


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