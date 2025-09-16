import os
import logging
import click
import tempfile
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, current_app, send_file, jsonify, session
import subprocess
from datetime import datetime, timedelta
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
from flask_migrate import Migrate
from config import Config 
from models import db, User, Plan, File, Folder, Subscription, Payment, Notification, UserFileShare, UserFolderShare
from database import create_database
from PIL import Image
import av
import cv2
from flask_mail import Mail, Message
import razorpay
from cryptography.fernet import Fernet
from cryptography.fernet import Fernet, InvalidToken, MultiFernet
from sqlalchemy import or_
from itsdangerous import URLSafeTimedSerializer
from functools import wraps
from io import BytesIO
import zipfile
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.config.from_object(Config)

s = URLSafeTimedSerializer(app.config['SECRET_KEY'])

mail = Mail(app)

# Initialize Razorpay client
razorpay_client = razorpay.Client(
    auth=(app.config.get('RAZORPAY_KEY_ID'), app.config.get('RAZORPAY_KEY_SECRET'))
)

db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

CHUNK_FOLDER = os.path.join(UPLOAD_FOLDER, 'chunks')
if not os.path.exists(CHUNK_FOLDER):
    os.makedirs(CHUNK_FOLDER)

THUMBNAIL_FOLDER = os.path.join(UPLOAD_FOLDER, 'thumbnails')
if not os.path.exists(THUMBNAIL_FOLDER):
    os.makedirs(THUMBNAIL_FOLDER)

VIDEO_CACHE_FOLDER = os.path.join(UPLOAD_FOLDER, 'video_cache')
if not os.path.exists(VIDEO_CACHE_FOLDER):
    os.makedirs(VIDEO_CACHE_FOLDER)

# Initialize a thread pool for background tasks like video conversion.
executor = ThreadPoolExecutor(max_workers=2)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@app.cli.command("init-db")
def init_db_command():
    """(DESTRUCTIVE) Drops all tables, creates the database, and initializes the default plan."""
    if not click.confirm('This will delete all existing data. Are you sure you want to continue?'):
        print("Operation cancelled.")
        return

    create_database(app)
    if not Plan.query.filter_by(name='Free').first():
        free_plan = Plan(name='Free', size_limit=20 * 1024 * 1024 * 1024) # 20GB in bytes
        db.session.add(free_plan)
        db.session.commit()
        print("Initialized the database and created the Free plan.")
    else:
        print("Database already initialized.")

@app.cli.command("create-admin")
@click.argument("name")
@click.argument("email")
@click.argument("password")
def create_admin_command(name, email, password):
    """Creates a new admin user."""
    if User.query.filter_by(email=email).first():
        print("User with this email already exists.")
        return

    new_user = User(name=name, email=email, role='admin')
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    print(f"Admin user {email} created successfully.")

@app.cli.command("backfill-subscriptions")
def backfill_subscriptions_command():
    """Creates free subscriptions for users who have a plan but no subscription."""
    users_without_subscription = User.query.filter(
        User.plan_id.isnot(None),
        ~User.subscriptions.any()
    ).all()

    if not users_without_subscription:
        print("All users with plans already have subscriptions.")
        return

    free_plan = Plan.query.filter_by(name='Free').first()
    if not free_plan:
        print("Error: 'Free' plan not found. Cannot backfill subscriptions.")
        return

    count = 0
    for user in users_without_subscription:
        if user.plan_id == free_plan.id:
            start_date = datetime.utcnow()
            end_date = start_date + timedelta(days=365 * 100)
            new_subscription = Subscription(user_id=user.id, plan_id=free_plan.id, start_date=start_date, end_date=end_date, active=True)
            db.session.add(new_subscription)
            count += 1
            print(f"Created free subscription for user {user.email}")

    if count > 0:
        db.session.commit()
        print(f"Successfully created {count} new subscriptions.")
    else:
        print("No users found needing a free plan subscription backfill.")

@app.cli.command("secure-all-thumbnails")
def secure_all_thumbnails_command():
    """
    Ensures all files are encrypted and all thumbnails are generated and encrypted.
    This command replaces `backfill-thumbnails` and `encrypt-existing-thumbnails`.
    """
    files_to_process = File.query.filter(
        (File.mime_type.like('image/%') | File.mime_type.like('video/%'))
    ).all()

    if not files_to_process:
        print("No image or video files found in the database.")
        return

    print(f"Found {len(files_to_process)} media files to check. Starting security audit...")
    updated_files = 0
    updated_thumbnails = 0
    
    master_fernet = Fernet(current_app.config['MASTER_ENCRYPTION_KEY'])

    with tempfile.TemporaryDirectory() as temp_dir:
        for file in files_to_process:
            try:
                # --- Step 1: Ensure the main file is encrypted ---
                if not file.encrypted_key:
                    print(f"File {file.filename} (ID: {file.id}) is not encrypted. Encrypting now...")
                    # Generate a new key for this file
                    new_file_key = Fernet.generate_key()
                    fernet = Fernet(new_file_key)
                    
                    # Read the unencrypted content
                    with open(file.path, 'rb') as f_read:
                        unencrypted_content = f_read.read()
                    
                    # Encrypt and overwrite the file
                    encrypted_content = fernet.encrypt(unencrypted_content)
                    with open(file.path, 'wb') as f_write:
                        f_write.write(encrypted_content)
                    
                    # Update the database record with the new key
                    file.encrypted_key = master_fernet.encrypt(new_file_key).decode('utf-8')
                    file.size = len(encrypted_content) # Update size to reflect encrypted size
                    updated_files += 1
                
                # --- Step 2: Get the Fernet instance for this file ---
                file_key = master_fernet.decrypt(file.encrypted_key.encode('utf-8'))
                fernet = Fernet(file_key)

                # --- Step 3: Check and secure the thumbnail ---
                thumb_name = f"thumb_{os.path.splitext(os.path.basename(file.path))[0]}.jpg"
                thumbnail_full_path = os.path.join(THUMBNAIL_FOLDER, thumb_name)

                # Force regeneration for .mov files, otherwise only create if it doesn't exist.
                if os.path.exists(thumbnail_full_path) and not file.filename.lower().endswith('.mov'):
                    # Thumbnail exists, check if it's encrypted
                    with open(thumbnail_full_path, 'rb') as f_thumb:
                        thumb_content = f_thumb.read()
                    try:
                        fernet.decrypt(thumb_content) # If this works, it's already encrypted correctly
                    except InvalidToken:
                        # It's not encrypted, so encrypt it.
                        print(f"Encrypting existing thumbnail for {file.filename}...")
                        encrypted_thumb_data = fernet.encrypt(thumb_content)
                        with open(thumbnail_full_path, 'wb') as f_write_thumb:
                            f_write_thumb.write(encrypted_thumb_data)
                        updated_thumbnails += 1
                    file.thumbnail_path = thumb_name # Ensure path is set even if only encrypting
                else:
                    # Thumbnail does not exist, so create it
                    action = "Regenerating" if os.path.exists(thumbnail_full_path) else "Generating"
                    print(f"{action} new thumbnail for {file.filename}...")
                    temp_file_path = None
                    try:
                        # Use a temporary file that we can control the lifetime of
                        temp_f = tempfile.NamedTemporaryFile(delete=False, dir=temp_dir, suffix=os.path.splitext(file.filename)[1])
                        with open(file.path, 'rb') as f_enc:
                            decrypted_content = fernet.decrypt(f_enc.read())
                        temp_f.write(decrypted_content)
                        temp_file_path = temp_f.name
                        temp_f.close() # Close the handle so ffmpeg can access it on Windows
                        
                        thumbnail_data = None
                        if file.mime_type.startswith('image/'):
                            thumbnail_data = create_image_thumbnail(temp_file_path)
                        elif file.mime_type.startswith('video/'):
                            thumbnail_data = create_video_thumbnail(temp_file_path)
                        
                        if thumbnail_data:
                            encrypted_thumbnail_data = fernet.encrypt(thumbnail_data)
                            with open(thumbnail_full_path, 'wb') as thumb_f:
                                thumb_f.write(encrypted_thumbnail_data)
                            file.thumbnail_path = thumb_name # Set path after successful creation
                            updated_thumbnails += 1
                    finally:
                        # Ensure the temporary file is cleaned up if it was created
                        if temp_file_path and os.path.exists(temp_file_path):
                            os.remove(temp_file_path)

            except Exception as e:
                print(f"An error occurred while processing file {file.filename} (ID: {file.id}): {e}. Skipping.")
                db.session.rollback()
                continue

    db.session.commit()
    print(f"\nSecurity audit complete. Updated {updated_files} main files and {updated_thumbnails} thumbnails.")

@app.cli.command("check-ffmpeg")
def check_ffmpeg_command():
    """Checks if ffmpeg is installed and accessible in the system's PATH."""
    try:
        # We run 'ffmpeg -h' because it's a lightweight command that will succeed if ffmpeg is found,
        # and we capture the output to prevent it from flooding the console.
        result = subprocess.run(['ffmpeg', '-h'], capture_output=True, text=True, check=True)
        print("\n✅ Success: ffmpeg is installed and accessible to the application.")
        # Optionally print the first few lines of the help output to confirm.
        print("--- ffmpeg help output (first 5 lines) ---")
        print('\n'.join(result.stdout.splitlines()[:5]))
        print("-----------------------------------------\n")
    except FileNotFoundError:
        print("\n❌ Error: The 'ffmpeg' command was not found.")
        print("Please ensure that FFmpeg is installed on your server and that the directory containing 'ffmpeg.exe' (e.g., C:\\ffmpeg\\bin) is included in your system's PATH environment variable.")
        print("After updating the PATH, you may need to restart your terminal or computer for the changes to take effect.\n")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error: ffmpeg was found, but it returned an error: {e.stderr}\n")


@app.cli.command("clean-video-cache")
@click.option('--days', default=7, help='Delete cached files older than this many days.')
def clean_video_cache_command(days):
    """Deletes old files from the video cache directory."""
    if not os.path.exists(VIDEO_CACHE_FOLDER):
        print("Video cache directory does not exist. Nothing to do.")
        return

    cutoff = datetime.utcnow() - timedelta(days=days)
    deleted_count = 0
    for filename in os.listdir(VIDEO_CACHE_FOLDER):
        filepath = os.path.join(VIDEO_CACHE_FOLDER, filename)
        if os.path.isfile(filepath):
            try:
                file_mod_time = datetime.utcfromtimestamp(os.path.getmtime(filepath))
                if file_mod_time < cutoff:
                    os.remove(filepath)
                    deleted_count += 1
            except Exception as e:
                print(f"Error deleting cached file {filename}: {e}")
    print(f"Video cache cleanup complete. Deleted {deleted_count} files older than {days} days.")

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def get_share_permissions(item, user):
    """
    Returns the share object for a given item and user, which contains permissions.
    Returns None if no direct share exists.
    """
    if isinstance(item, File):
        return UserFileShare.query.filter_by(file_id=item.id, user_id=user.id).first()
    elif isinstance(item, Folder):
        return UserFolderShare.query.filter_by(folder_id=item.id, user_id=user.id).first()
    return None

def get_effective_permissions(item, user, visited_users=None):
    """
    Recursively finds the effective share permissions for a user on an item.
    It traverses up the folder hierarchy and through re-share chains.
    Returns a tuple: (has_access, can_download, can_copy, can_reshare)
    """
    if visited_users is None:
        visited_users = set()

    if user in visited_users:
        return False, False, False, False
    visited_users.add(user)

    if item.user_id == user.id:
        return True, True, True, True # Owner has all permissions

    share_model = UserFileShare if isinstance(item, File) else UserFolderShare
    share = get_share_permissions(item, user)

    if share:
        if share.reshared_by_id:
            resharer = User.query.get(share.reshared_by_id)
            # A user has access via a reshare only if the person who reshared it to them still has reshare permission.
            has_access_from_resharer, _, _, can_reshare_from_resharer = get_effective_permissions(item, resharer, visited_users)
            if has_access_from_resharer and can_reshare_from_resharer:
                return True, share.can_download, share.can_copy, share.can_reshare
        else: # Direct share from owner
            return True, share.can_download, share.can_copy, share.can_reshare

    if isinstance(item, File) and item.folder:
        return get_effective_permissions(item.folder, user, visited_users)
    
    if isinstance(item, Folder) and item.parent:
        return get_effective_permissions(item.parent, user, visited_users)

    return False, False, False, False

def has_access(item, user):
    return get_effective_permissions(item, user)[0]

def can_download_item(item, user):
    return get_effective_permissions(item, user)[1]

def can_copy_item(item, user):
    return get_effective_permissions(item, user)[2]

def can_reshare_item(item, user):
    return get_effective_permissions(item, user)[3]

def get_total_shares(item):
    all_shares = set()
    
    # Start with direct shares from the owner
    direct_shares = item.user_shares
    
    shares_to_process = list(direct_shares)
    processed_shares = set(shares_to_process)

    while shares_to_process:
        share = shares_to_process.pop(0)
        all_shares.add(share)

        if share.can_reshare:
            share_model = UserFileShare if isinstance(item, File) else UserFolderShare
            
            reshared_by_this_user = share_model.query.filter_by(
                reshared_by_id=share.user_id,
                **{'file_id' if isinstance(item, File) else 'folder_id': item.id}
            ).all()
            
            for reshare in reshared_by_this_user:
                if reshare not in processed_shares:
                    shares_to_process.append(reshare)
                    processed_shares.add(reshare)

    return len(all_shares)

@app.context_processor
def inject_permission_helpers():
    return dict(
        can_download_item=can_download_item,
        can_copy_item=can_copy_item,
        get_total_shares=get_total_shares,
        can_reshare_item=can_reshare_item
    )

def get_unique_filename(path):
    """
    Checks if a file exists at the given path and returns a unique path if it does.
    e.g., if 'uploads/image.jpg' exists, it will try 'uploads/image_1.jpg', etc.
    """
    if not os.path.exists(path):
        return path
    
    directory, filename = os.path.split(path)
    name, ext = os.path.splitext(filename)
    
    counter = 1
    while True:
        new_name = f"{name}_{counter}{ext}"
        new_path = os.path.join(directory, new_name)
        if not os.path.exists(new_path):
            return new_path
        counter += 1

def create_image_thumbnail(file_path):
    """Creates an image thumbnail and returns it as bytes."""
    try:
        with Image.open(file_path) as img:
            img.thumbnail((256, 256))
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            
            thumb_io = BytesIO()
            img.save(thumb_io, "JPEG", quality=85)
            thumb_io.seek(0)
            return thumb_io.read()
    except Exception as e:
        app.logger.error(f"Could not create image thumbnail for {file_path}: {e}")
        return None

def create_video_thumbnail(file_path):
    """Creates a video thumbnail and returns it as bytes."""
    try:
        with av.open(file_path) as container:
            # Find the first video stream
            stream = container.streams.video[0]
            # Seek to a position that is 15% into the video to find a good frame
            seek_time = stream.duration * 0.15
            container.seek(int(seek_time))

            # Decode frames until we get one
            frame = next(container.decode(stream))
            
            # Convert the frame to a Pillow Image
            img = frame.to_image()

            # Resize it using a high-quality downsampling filter (LANCZOS)
            # while maintaining aspect ratio.
            target_width = 320 # A slightly larger thumbnail for better quality
            width, height = img.size
            target_height = int(target_width * height / width)
            img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)

            # Save the thumbnail to an in-memory buffer with higher quality
            thumb_io = BytesIO()
            img.save(thumb_io, "JPEG", quality=92)
            thumb_io.seek(0)
            return thumb_io.read()
    except Exception as e:
        app.logger.error(f"Could not create video thumbnail for {file_path} using PyAV: {e}")
    return None

def convert_video_to_mp4(input_path, output_path):
    """Converts a video file to a web-friendly MP4 (H.264/AAC) using ffmpeg."""
    try:
        # Using subprocess to call ffmpeg directly is often the most reliable way.
        # -i: input file
        # -vcodec libx264: video codec H.264
        # -acodec aac: audio codec AAC
        # -pix_fmt yuv420p: pixel format for compatibility
        # -movflags +faststart: allows the video to start playing before it's fully downloaded
        # -y: overwrite output file if it exists
        command = [
            'ffmpeg',
            '-i', input_path,
            '-vcodec', 'libx264',
            '-acodec', 'aac',
            '-pix_fmt', 'yuv420p',
            '-movflags', '+faststart',
            '-y',
            output_path
        ]
        # We don't want ffmpeg's output flooding the console unless there's an error.
        subprocess.run(command, check=True, capture_output=True, text=True)
        app.logger.info(f"Successfully converted {os.path.basename(input_path)} to {os.path.basename(output_path)}")
        return True
    except subprocess.CalledProcessError as e:
        app.logger.error(f"ffmpeg conversion failed for {os.path.basename(input_path)}. Stderr: {e.stderr}")
        return False
    except FileNotFoundError:
        app.logger.error("ffmpeg command not found. Make sure ffmpeg is installed and in your system's PATH.")
        return False

@app.route('/')
@app.route('/folder/<int:folder_id>')
@login_required
def index(folder_id=None):
    if current_user.role == 'admin':
        return redirect(url_for('admin_dashboard'))

    # If a user has not selected a plan yet, guide them to the pricing page.
    if not current_user.plan_id:
        flash('Welcome! Please select a plan to get started.', 'info')
        return redirect(url_for('pricing'))

    # Get search and sort parameters from the request
    search_term = request.args.get('search', '')
    sort_by = request.args.get('sort', 'date_desc')
    sharer_id = request.args.get('sharer_id', type=int)

    # Check if the request is an AJAX call for a partial update
    is_partial_request = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    # Base queries
    # For modals, we need all folders the user can move items TO. That's their own folders.
    base_folders_query = Folder.query.filter_by(user_id=current_user.id)
    breadcrumbs = []
    
    if folder_id:
        folder = db.get_or_404(Folder, folder_id)
        # Access check: user must own the folder or it (or a parent) must be shared with them.
        if not has_access(folder, current_user):
            flash('You do not have permission to access this folder.', 'danger')
            return redirect(url_for('index'))
        # If inside an accessible folder, show its direct contents.
        folders_query = Folder.query.filter_by(parent_id=folder_id)
        files_query = File.query.filter_by(folder_id=folder_id)
        
        # Build breadcrumb path
        if sharer_id:
            # If we are in a shared context, build a virtual breadcrumb path
            sharer = db.get_or_404(User, sharer_id)
            breadcrumbs.append({'name': 'Home', 'url': url_for('index')})
            breadcrumbs.append({'name': 'Shared', 'url': url_for('shared_items')})
            breadcrumbs.append({'name': f"{sharer.name} ({sharer.id})", 'url': url_for('shared_items', sharer_id=sharer.id)})
            
            # This approach is clean and avoids showing the owner's private path.
            # We can build a partial path from the shared item downwards if needed,
            # but for now, just showing the current folder is clear and secure.
            if folder.user_id == sharer_id: # Make sure we are in the sharer's folder
                 breadcrumbs.append({'name': folder.name, 'url': url_for('index', folder_id=folder.id, sharer_id=sharer_id)})

        else:
            # Original breadcrumb logic for user's own files
            temp_folder = folder
            while temp_folder:
                breadcrumbs.append({'name': temp_folder.name, 'url': url_for('index', folder_id=temp_folder.id, sharer_id=sharer_id)})
                temp_folder = temp_folder.parent
            breadcrumbs.append({'name': 'Home', 'url': url_for('index')})
            breadcrumbs.reverse()

    else:
        folder = None
        # In root, show user's own root folders + root folders shared with them
        # We fetch all root items and then filter by access.
        folders_query = Folder.query.filter(Folder.parent_id.is_(None))
        files_query = File.query.filter(File.folder_id.is_(None))

    if folder_id:
        # If we are inside a folder we already have access to, list all its contents directly.
        # The access checks will happen when the user tries to enter a sub-folder or download a file.
        folders = folders_query.all()
        files = files_query.all()
    else:
        # For the root view, we must check each item individually to see if it's owned or shared.
        all_folders_in_view = folders_query.all()
        all_files_in_view = files_query.all()
        folders = [f for f in all_folders_in_view if has_access(f, current_user)]
        files = [f for f in all_files_in_view if has_access(f, current_user)]


    # Apply search filter
    if search_term:
        folders = [f for f in folders if search_term.lower() in f.name.lower()]
        files = [f for f in files if search_term.lower() in f.filename.lower()]

    # Apply sorting
    if sort_by == 'name_desc':
        folders.sort(key=lambda f: f.name, reverse=True)
        files.sort(key=lambda f: f.filename, reverse=True)
    elif sort_by == 'date_desc':
        folders.sort(key=lambda f: f.name) # Folders don't have a date, sort by name
        files.sort(key=lambda f: f.created_at, reverse=True)
    elif sort_by == 'date_asc':
        folders.sort(key=lambda f: f.name) # Folders don't have a date, sort by name
        files.sort(key=lambda f: f.created_at)
    elif sort_by == 'type_asc':
        folders.sort(key=lambda f: f.name) # Folders are one type, sort by name
        files.sort(key=lambda f: f.mime_type)
    elif sort_by == 'type_desc':
        folders.sort(key=lambda f: f.name) # Folders are one type, sort by name
        files.sort(key=lambda f: f.mime_type, reverse=True)
    else: # Default sort is name_asc
        folders.sort(key=lambda f: f.name)
        files.sort(key=lambda f: f.filename)

    # For partial requests, only render the file list
    if is_partial_request:
        all_folders = base_folders_query.order_by(Folder.name.asc()).all() # Modals need all folders
        return render_template('_file_list.html', files=files, folders=folders, all_folders=all_folders, current_folder=folder, breadcrumbs=breadcrumbs, sharer_id=sharer_id)

    # For full page loads, render the entire index
    all_folders = base_folders_query.all()
    return render_template('index.html', files=files, folders=folders, current_folder=folder, all_folders=all_folders, search=search_term, sort=sort_by, is_partial=is_partial_request, breadcrumbs=breadcrumbs, sharer_id=sharer_id)

class VirtualFolder:
    """A class to represent a non-database folder, like 'Shared' or a user folder."""
    def __init__(self, id, name, parent=None):
        self.id = id
        self.name = name
        self.parent = parent
        self.children = []
        self.files = []

@app.context_processor
def inject_notifications():
    if current_user.is_authenticated:
        unread_notifications = Notification.query.filter_by(user_id=current_user.id, is_read=False).order_by(Notification.created_at.desc()).all()
        return dict(unread_notifications=unread_notifications)
    return dict(unread_notifications=[])

@app.route('/shared')
@app.route('/shared/<int:sharer_id>')
@login_required
def shared_items(sharer_id=None):
    """
    Handles the virtual 'Shared' folder view.
    - If no sharer_id, it lists users who have shared items.
    - If sharer_id is provided, it lists items from that specific user.
    """
    if current_user.role == 'admin':
        return redirect(url_for('admin_dashboard'))

    search_term = request.args.get('search', '')
    sort_by = request.args.get('sort', 'date_desc')
    breadcrumbs = []

    # For modals, we always need the user's own folders for moving items.
    all_folders = Folder.query.filter_by(user_id=current_user.id).all()

    if sharer_id is None:
        # --- Top-level "Shared" view: List users as folders ---
        breadcrumbs.append({'name': 'Home', 'url': url_for('index')})
        breadcrumbs.append({'name': 'Shared', 'url': url_for('shared_items')})
        
        # 1. Get all files and folders shared with the current user.
        files_shared_with_me = File.query.join(UserFileShare).filter(UserFileShare.user_id == current_user.id).all()
        folders_shared_with_me = Folder.query.join(UserFolderShare).filter(UserFolderShare.user_id == current_user.id).all()
        # 2. Create a set of the owners (sharers) of those items.
        sharers = {file.user for file in files_shared_with_me}
        sharers.update({folder.user for folder in folders_shared_with_me})

        # Create virtual folders for each sharer
        virtual_user_folders = [VirtualFolder(id=sharer.id, name=f"{sharer.name} ({sharer.id})") for sharer in sharers]

        # Sort the virtual folders by name
        virtual_user_folders.sort(key=lambda f: f.name)

        # This is the virtual "Shared" folder acting as the current folder
        current_virtual_folder = VirtualFolder(id=0, name="Shared")

        return render_template('index.html', 
                               folders=virtual_user_folders, 
                               files=[], 
                               current_folder=current_virtual_folder, 
                               all_folders=all_folders, 
                               search=search_term, 
                               sort=sort_by,
                               is_shared_view=True,
                               breadcrumbs=breadcrumbs)
    else:
        # --- User-specific shared view: List items from one sharer ---
        sharer = db.get_or_404(User, sharer_id)

        # Get all folders shared by this user with the current user.
        folders_query = Folder.query.join(UserFolderShare).filter(UserFolderShare.user_id == current_user.id, Folder.user_id == sharer_id)
        
        # Get all files shared by this user, excluding those inside an already-shared folder.
        shared_folder_ids = [f.id for f in folders_query.all()]
        files_query = File.query.join(UserFileShare).filter(UserFileShare.user_id == current_user.id, File.user_id == sharer_id, File.folder_id.notin_(shared_folder_ids))

        # Apply search filter
        if search_term:
            files_query = files_query.filter(File.filename.ilike(f'%{search_term}%'))
            folders_query = folders_query.filter(Folder.name.ilike(f'%{search_term}%'))

        # Apply sorting
        folders_query = folders_query.order_by(Folder.name.asc())
        files_query = files_query.order_by(File.filename.asc())

        files = files_query.all()
        folders = folders_query.all()

        breadcrumbs.append({'name': 'Home', 'url': url_for('index')})
        breadcrumbs.append({'name': 'Shared', 'url': url_for('shared_items')})
        breadcrumbs.append({'name': f"{sharer.name} ({sharer.id})", 'url': url_for('shared_items', sharer_id=sharer.id)})

        return render_template('index.html', 
                               files=files, 
                               folders=folders,
                               all_folders=all_folders, 
                               search=search_term, 
                               sort=sort_by,
                               is_shared_view=True,
                               breadcrumbs=breadcrumbs,
                               sharer_id=sharer_id)

def _delete_folder_recursive(folder):
    """Helper function to recursively delete folders and calculate total size."""
    total_size_deleted = 0
    # Create copies of the collections to avoid issues with changing them during iteration
    subfolders_to_delete = list(folder.children)
    files_to_delete = list(folder.files)

    for subfolder in subfolders_to_delete:
        total_size_deleted += _delete_folder_recursive(subfolder)

    for file in files_to_delete:
        try:
            os.remove(file.path)
        except FileNotFoundError:
            # If file is already gone from disk, log it but still remove from DB.
            app.logger.warning(f"File not found on disk during recursive delete, but proceeding to delete database record: {file.path}")
        except OSError as e:
            # For other errors (e.g., permissions), log and skip this file.
            app.logger.error(f'Error deleting file {file.path} from disk during recursive delete: {e}')
            continue

        # Also delete the cached video preview if it exists
        if file.mime_type == 'video/quicktime':
            cached_filename = f"cache_{file.id}_{int(file.created_at.timestamp())}.mp4"
            cached_filepath = os.path.join(VIDEO_CACHE_FOLDER, cached_filename)
            if os.path.exists(cached_filepath):
                os.remove(cached_filepath)

        total_size_deleted += file.size
        db.session.delete(file)

    db.session.delete(folder)
    return total_size_deleted

@app.route('/delete-folder/<int:folder_id>', methods=['POST'])
@login_required
def delete_folder(folder_id):
    folder = db.get_or_404(Folder, folder_id)
    if folder.user_id != current_user.id and current_user.role != 'admin':
        flash('You do not have permission to delete this folder.', 'danger')
        return redirect(url_for('index'))

    parent_id = folder.parent_id # Store parent_id before deletion
    size_to_free = _delete_folder_recursive(folder)
    
    if size_to_free > 0:
        current_user.used_storage -= size_to_free

    db.session.commit()
    flash('Folder and its contents deleted successfully!', 'success')

    if parent_id:
        return redirect(url_for('index', folder_id=parent_id))
    return redirect(url_for('index'))

@app.route('/favicon.ico')
def favicon():
    # Return a 204 No Content response to prevent 404 errors in the console.
    return '', 204

@app.route('/create-folder', methods=['POST'])
@login_required
def create_folder():
    if not current_user.plan_id:
        flash('You must select a plan to perform this action.', 'danger')
        return redirect(url_for('pricing'))
    folder_name = request.form['folder_name']
    parent_id = request.form.get('parent_id')
    if parent_id == 'None':
        parent_id = None
    
    if not folder_name:
        flash('Folder name cannot be empty.', 'warning')
    else:
        new_folder = Folder(name=folder_name, user_id=current_user.id, parent_id=parent_id)
        db.session.add(new_folder)
        db.session.commit()
        flash('Folder created successfully!', 'success')

    if parent_id:
        return redirect(url_for('index', folder_id=parent_id))
    return redirect(url_for('index'))

@app.route('/rename-folder/<int:folder_id>', methods=['POST'])
@login_required
def rename_folder(folder_id):
    folder = db.get_or_404(Folder, folder_id)
    if folder.user_id != current_user.id:
        flash('You do not have permission to rename this folder.', 'danger')
        return redirect(url_for('index'))
    new_name = request.form['new_name']
    folder.name = new_name
    db.session.commit()
    flash('Folder renamed successfully!', 'success')
    return redirect(request.referrer or url_for('index'))

@app.route('/rename-file/<int:file_id>', methods=['POST'])
@login_required
def rename_file(file_id):
    if not current_user.plan_id:
        flash('You must select a plan to perform this action.', 'danger')
        return redirect(url_for('pricing'))
    file = db.get_or_404(File, file_id)
    if file.user_id != current_user.id and current_user.role != 'admin':
        flash('You do not have permission to rename this file.', 'danger')
        return redirect(url_for('index'))

    new_name = request.form['new_name']
    if not new_name:
        flash('File name cannot be empty.', 'warning')
    else:
        file.filename = new_name
        db.session.commit()
        flash('File renamed successfully!', 'success')

    if file.folder_id:
        return redirect(url_for('index', folder_id=file.folder_id))
    return redirect(url_for('index'))

@app.route('/move-file/<int:file_id>', methods=['POST'])
@login_required
def move_file(file_id):
    file = db.get_or_404(File, file_id)
    if not has_access(file, current_user) and current_user.role != 'admin':
        flash('You do not have permission to move this file.', 'danger')
        return redirect(url_for('index'))

    new_folder_id = request.form.get('new_folder_id')
    if new_folder_id == 'None':
        new_folder_id = None
    
    file.folder_id = new_folder_id
    db.session.commit()
    flash('File moved successfully!', 'success')

    if file.folder_id:
        return redirect(url_for('index', folder_id=file.folder_id))
    return redirect(url_for('index'))

@app.route('/move-folder/<int:folder_id>', methods=['POST'])
@login_required
def move_folder(folder_id):
    folder = db.get_or_404(Folder, folder_id)
    if folder.user_id != current_user.id and current_user.role != 'admin':
        flash('You do not have permission to move this folder.', 'danger')
        return redirect(url_for('index'))

    new_parent_id = request.form.get('new_parent_id')
    if new_parent_id == 'None':
        new_parent_id = None
    
    folder.parent_id = new_parent_id
    db.session.commit()
    flash('Folder moved successfully!', 'success')

    if folder.parent_id:
        return redirect(url_for('index', folder_id=folder.parent_id))
    return redirect(url_for('index'))

@app.route('/preview/<int:file_id>')
@login_required
def preview_file(file_id):
    origin_url = request.args.get('origin')
    sharer_id = request.args.get('sharer_id', type=int)

    file = db.get_or_404(File, file_id)

    # --- Video Conversion Status Check ---
    is_video_processing = False
    cached_video_path = None
    
    # To ensure consistent permissions, check access on the container folder if it exists.
    # This mirrors the logic in the main index view.
    access_granted = False
    if file.folder:
        if has_access(file.folder, current_user):
            access_granted = True
    else: # For root files, check access on the file itself
        if has_access(file, current_user):
            access_granted = True

    if not access_granted:
        flash('You do not have permission to preview this file.', 'danger')
        return redirect(url_for('index'))

    # If it's a .mov file, check its conversion status before rendering
    if file.mime_type == 'video/quicktime':
        cached_filename = f"cache_{file.id}_{int(file.created_at.timestamp())}.mp4"
        cached_filepath = os.path.join(VIDEO_CACHE_FOLDER, cached_filename)
        if os.path.exists(cached_filepath):
            cached_video_path = url_for('download_file', file_id=file.id, inline=True, sharer_id=sharer_id)
        else:
            # If not cached, check if a conversion job is already running
            if not is_conversion_running(file.id):
                # Start conversion in the background
                executor.submit(convert_and_cache_video, file.id)
            is_video_processing = True

    # --- Logic for Next/Previous navigation ---
    previous_file_id = None
    next_file_id = None

    # Only provide next/prev for media files the user has access to
    if file.mime_type.startswith('image/') or file.mime_type.startswith('video/'):
        # Get all media files in the same folder, then filter by access.
        media_files_query = File.query.filter(
            File.folder_id == file.folder_id,
            (File.mime_type.like('image/%') | File.mime_type.like('video/%'))
        ).order_by(File.created_at.desc())
        accessible_media_files = [f for f in media_files_query.all() if has_access(f, current_user)]

        try:
            current_index = accessible_media_files.index(file)
            if current_index > 0:
                previous_file_id = url_for('preview_file', file_id=accessible_media_files[current_index - 1].id, origin=origin_url, sharer_id=sharer_id)
            if current_index < len(accessible_media_files) - 1:
                next_file_id = url_for('preview_file', file_id=accessible_media_files[current_index + 1].id, origin=origin_url, sharer_id=sharer_id)
        except ValueError:
            # This can happen if the file is shared but the query is wrong.
            pass

    file_content = None
    try:
        # Decrypt the file key using the master key
        master_fernet = Fernet(current_app.config['MASTER_ENCRYPTION_KEY']) # This key is already bytes
        file_key = master_fernet.decrypt(file.encrypted_key.encode('utf-8'))
        fernet = Fernet(file_key)

        # Read encrypted content from disk
        with open(file.path, 'rb') as f:
            encrypted_content = f.read()

        # Decrypt the file content
        decrypted_content = fernet.decrypt(encrypted_content)

        if file.mime_type.startswith('text'):
            file_content = decrypted_content.decode('utf-8')
        elif file.mime_type.startswith('image') or file.mime_type.startswith('video') or file.mime_type.startswith('audio') or file.mime_type == 'application/pdf':
            # For media and PDF, we need to serve the decrypted content as a blob or data URL
            # For simplicity in preview, we'll use download_file route which already handles decryption and streaming
            # In a real app, you might create a temporary URL or data URI for direct embedding
            pass # The template will call download_file for these types

    except Exception as e:
        flash(f'Could not preview file: {e}', 'danger')
        return redirect(url_for('index'))
    
    # Query for all folders owned by the user to populate modals (like the 'Copy' modal)
    all_folders = Folder.query.filter_by(user_id=current_user.id).order_by(Folder.name).all()

    return render_template('preview.html', 
                           file=file, 
                           file_content=file_content,
                           previous_file_id=previous_file_id,
                           next_file_id=next_file_id, 
                           all_folders=all_folders,
                           origin_url=origin_url,
                           sharer_id=sharer_id,
                           is_video_processing=is_video_processing,
                           cached_video_path=cached_video_path)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        app.logger.info(f"Attempting to log in user with email: {email}")
        user = User.query.filter_by(email=email).first()
        app.logger.info(f"User found in database: {user}")
        if user:
            app.logger.info(f"Password check result: {user.check_password(password)}")
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password.', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        app.logger.info(f"Registering user with email: {email}")
        if User.query.filter_by(email=email).first():
            flash('Email address already exists.', 'warning')
            return redirect(url_for('register'))
        
        # Create user without a default plan
        new_user = User(name=name, email=email)
        new_user.set_password(password)
        app.logger.info(f"Generated password hash for {email}: {new_user.password_hash}")
        db.session.add(new_user)
        db.session.commit()

        # Log the user in and redirect them to choose a plan
        login_user(new_user)
        flash('Congratulations, you are now registered! Please select a plan to get started.', 'success')
        return redirect(url_for('pricing'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    # This check is a safeguard, but the /index route should redirect first.
    is_ajax = 'application/json' in request.headers.get('Accept', '')

    # For AJAX, we can't rely on flashed messages, so we'll return JSON.
    if is_ajax and not current_user.plan_id:
        return jsonify({'success': False, 'error': 'You must select a plan before you can upload files.'}), 400

    if not current_user.plan_id:
        flash('You must select a plan before you can upload files.', 'danger')
        return redirect(url_for('pricing'))
    
    # --- Chunked Upload Logic ---
    file = request.files.get('file')
    if not file:
        flash('No file part in the request.', 'warning')
        if is_ajax:
            return jsonify({'success': False, 'error': 'No file part in the request.'}), 400
        return redirect(url_for('index'))

    # These parameters are sent by the client-side JS for each chunk
    upload_uuid = request.form.get('dzuuid')
    chunk_index = int(request.form.get('dzchunkindex'))
    total_chunks = int(request.form.get('dztotalchunkcount'))

    # Sanitize the UUID to prevent directory traversal
    safe_uuid = secure_filename(upload_uuid)
    chunk_path = os.path.join(CHUNK_FOLDER, f"{safe_uuid}_{chunk_index}")
    
    # Save the chunk
    with open(chunk_path, 'wb') as f:
        f.write(file.read())

    # If it's not the last chunk, just return success for this chunk
    if chunk_index < total_chunks - 1:
        return jsonify({'success': True, 'message': 'Chunk uploaded successfully'})

    # --- This is the LAST chunk, so reassemble and process the file ---
    original_filename = file.filename # The original filename is sent with each chunk
    
    # Generate a unique path to prevent overwriting existing files
    base_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(original_filename))
    final_path = get_unique_filename(base_path)
    unique_filename = os.path.basename(final_path)

    try:
        with open(final_path, 'wb') as final_file:
            for i in range(total_chunks):
                part_path = os.path.join(CHUNK_FOLDER, f"{safe_uuid}_{i}")
                with open(part_path, 'rb') as part_file:
                    final_file.write(part_file.read())
                os.remove(part_path) # Clean up the chunk
    except Exception as e:
        app.logger.error(f"Could not reassemble file {original_filename}: {e}")
        return jsonify({'success': False, 'error': 'File reassembly failed.'}), 500

    mime_type = request.form.get('mime_type', 'application/octet-stream')

    # --- Generate thumbnail before encryption ---
    thumbnail_filename = None
    thumbnail_data = None
    if mime_type.startswith('image/'):
        thumbnail_data = create_image_thumbnail(final_path)
    elif mime_type.startswith('video/'):
        thumbnail_data = create_video_thumbnail(final_path)

    # --- File is now reassembled, proceed with encryption and saving ---
    folder_id = request.form.get('folder_id')
    if folder_id == 'None':
        folder_id = None

    user_plan = db.session.get(Plan, current_user.plan_id)
    uploaded_count = 0
    failed_uploads = []
    total_size_added = 0

    filename = unique_filename # Use the unique filename for the database record

    # Generate a new Fernet key for this file
    file_key = Fernet.generate_key()
    fernet = Fernet(file_key)

    # Read reassembled file content, encrypt it, and then write it back.
    # This is memory-intensive but guarantees correct encryption with Fernet.
    with open(final_path, 'rb') as f:
        file_content = f.read()
    
    encrypted_content = fernet.encrypt(file_content)
    file_size = len(encrypted_content)

    # Check storage space
    if current_user.used_storage + file_size > user_plan.size_limit:
        os.remove(final_path) # Clean up the reassembled file
        return jsonify({'success': False, 'error': f'Could not upload {filename} due to insufficient storage.'}), 413

    # Overwrite the reassembled file with the encrypted content
    with open(final_path, 'wb') as f:
        f.write(encrypted_content)

    # --- Encrypt and save thumbnail if it was created ---
    if thumbnail_data:
        encrypted_thumbnail_data = fernet.encrypt(thumbnail_data)
        thumb_name = f"thumb_{os.path.splitext(unique_filename)[0]}.jpg"
        thumb_path = os.path.join(THUMBNAIL_FOLDER, thumb_name)
        with open(thumb_path, 'wb') as thumb_f:
            thumb_f.write(encrypted_thumbnail_data)
        thumbnail_filename = os.path.basename(thumb_path)

    # Encrypt the file_key with the master encryption key
    master_fernet = Fernet(current_app.config['MASTER_ENCRYPTION_KEY'])
    encrypted_file_key = master_fernet.encrypt(file_key)

    new_file = File(user_id=current_user.id, folder_id=folder_id, filename=original_filename, path=final_path, size=file_size, mime_type=mime_type, encrypted_key=encrypted_file_key.decode('utf-8'), thumbnail_path=thumbnail_filename)
    db.session.add(new_file)
    db.session.flush() # Flush to get the new file's ID

    file_data = {
        'id': new_file.id,
        'filename': new_file.filename,
        'size': new_file.size,
        'mime_type': new_file.mime_type,
        'created_at': new_file.created_at.strftime('%Y-%m-%d')
    }
    total_size_added = file_size
    uploaded_count = 1

    if total_size_added > 0:
        current_user.used_storage += total_size_added
        db.session.commit()

    # Handle response type
    if is_ajax:
        return jsonify({'success': True, 'file': file_data})
    # Fallback for non-ajax, though our new flow is all ajax
    return redirect(url_for('index', folder_id=folder_id))

@app.route('/thumbnails/<path:filename>')
@login_required
def serve_thumbnail(filename):
    """
    Serves a decrypted thumbnail image.
    The sharer_id is passed as a query parameter to handle permissions for shared items.
    """
    sharer_id = request.args.get('sharer_id', type=int)

    # Find the file record directly using the thumbnail_path
    file_record = File.query.filter_by(thumbnail_path=filename).first()

    if not file_record:
        return "Thumbnail not found or permission denied", 404

    # To ensure consistent permissions, check access on the container folder if it exists.
    access_granted = False
    if file_record.folder:
        if has_access(file_record.folder, current_user):
            access_granted = True
    else: # For root files, check access on the file itself
        if has_access(file_record, current_user):
            access_granted = True
    if not access_granted:
        return "Thumbnail not found or permission denied", 404

    if not file_record.encrypted_key:
        # This is a fallback for legacy, unencrypted files. Serve directly.
        # This should not be hit after running `secure-all-thumbnails`.
        app.logger.warning(f"Serving unencrypted thumbnail for legacy file: {file_record.filename}")
        return send_from_directory(THUMBNAIL_FOLDER, filename)

    try:
        # Decrypt the file key
        master_fernet = Fernet(current_app.config['MASTER_ENCRYPTION_KEY'])
        file_key = master_fernet.decrypt(file_record.encrypted_key.encode('utf-8'))
        # Use MultiFernet to handle key rotation in the future if needed, and for robustness.
        f = MultiFernet([Fernet(file_key)])

        # Read and decrypt the thumbnail
        with open(os.path.join(THUMBNAIL_FOLDER, filename), 'rb') as thumb_file:
            decrypted_content = f.decrypt(thumb_file.read())
        return send_file(BytesIO(decrypted_content), mimetype='image/jpeg')
    except Exception as e:
        app.logger.error(f"Error serving thumbnail {filename}: {e}")
        return "Error processing thumbnail", 500

def is_conversion_running(file_id):
    """Check if a conversion lock file exists for a given file_id."""
    lock_file = os.path.join(VIDEO_CACHE_FOLDER, f"convert_{file_id}.lock")
    return os.path.exists(lock_file)

def convert_and_cache_video(file_id):
    """
    A background task to convert a .mov file to .mp4.
    This function is designed to be run in a separate thread.
    """
    with app.app_context():
        file = db.session.get(File, file_id)
        if not file or file.mime_type != 'video/quicktime':
            app.logger.error(f"Conversion task started for invalid file ID {file_id}.")
            return

        cached_filename = f"cache_{file.id}_{int(file.created_at.timestamp())}.mp4"
        cached_filepath = os.path.join(VIDEO_CACHE_FOLDER, cached_filename)
        lock_file = os.path.join(VIDEO_CACHE_FOLDER, f"convert_{file_id}.lock")

        # Create a lock file to indicate conversion is in progress
        with open(lock_file, 'w') as f:
            f.write('running')

        temp_mov_path = None
        try:
            app.logger.info(f"Starting background conversion for file ID {file.id}.")
            master_fernet = Fernet(current_app.config['MASTER_ENCRYPTION_KEY'])
            file_key = master_fernet.decrypt(file.encrypted_key.encode('utf-8'))
            fernet = Fernet(file_key)
            with open(file.path, 'rb') as f_enc:
                decrypted_content = fernet.decrypt(f_enc.read())
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mov') as temp_mov:
                temp_mov.write(decrypted_content)
                temp_mov_path = temp_mov.name

            convert_video_to_mp4(temp_mov_path, cached_filepath)
            app.logger.info(f"Background conversion successful for file ID {file.id}.")
        except Exception as e:
            app.logger.error(f"Background conversion failed for file ID {file.id}: {e}")
        finally:
            # Clean up temporary files
            if temp_mov_path and os.path.exists(temp_mov_path):
                os.remove(temp_mov_path)
            if os.path.exists(lock_file):
                os.remove(lock_file)

@app.route('/download/<int:file_id>')
@login_required
def download_file(file_id):
    sharer_id = request.args.get('sharer_id', type=int)
    file = db.get_or_404(File, file_id)
    is_ajax = 'application/json' in request.headers.get('Accept', '')

    # Check access on the container folder first for consistency with the preview page.
    access_granted = False
    if file.folder:
        if has_access(file.folder, current_user):
            access_granted = True
    else: # For root files, check access on the file itself
        if has_access(file, current_user):
            access_granted = True
    if not access_granted:
        if is_ajax: return jsonify({'error': 'Permission denied.'}), 403
        else:
            flash('You do not have permission to access this file.', 'danger')
            return redirect(url_for('index'))

    # Determine if this is a download request or an inline preview request
    as_attachment = request.args.get('inline', 'false').lower() != 'true'

    # --- Serve cached .mov previews ---
    if not as_attachment and file.mime_type == 'video/quicktime':
        cached_filename = f"cache_{file.id}_{int(file.created_at.timestamp())}.mp4"
        cached_filepath = os.path.join(VIDEO_CACHE_FOLDER, cached_filename)
        if os.path.exists(cached_filepath):
            return send_file(cached_filepath, mimetype='video/mp4')
        else:
            # This should not be hit if the preview page logic is correct
            return "Video is still processing.", 404

    # Enforce specific download permission ONLY for actual downloads, not previews
    if as_attachment and not can_download_item(file, current_user):
        message = 'You do not have permission to download this file.'
        if is_ajax: return jsonify({'error': message}), 403
        flash(message, 'danger')
        return redirect(request.referrer or url_for('index'))

    try:
        # Decrypt the file key using the master key
        master_fernet = Fernet(current_app.config['MASTER_ENCRYPTION_KEY']) # This key is already bytes
        file_key = master_fernet.decrypt(file.encrypted_key.encode('utf-8'))
        fernet = Fernet(file_key)

        # Read encrypted content from disk
        with open(file.path, 'rb') as f:
            encrypted_content = f.read()

        # Decrypt the file content
        decrypted_content = fernet.decrypt(encrypted_content)

        # Create a BytesIO object to serve the decrypted content
        from io import BytesIO
        
        if as_attachment:
            return send_file(
                BytesIO(decrypted_content), 
                mimetype=file.mime_type, 
                as_attachment=True, 
                download_name=file.filename
            )
        else: # For inline display (previews, sharing), don't set download_name
            return send_file(BytesIO(decrypted_content), mimetype=file.mime_type)
    except Exception as e:
        if is_ajax: return jsonify({'error': f'Error downloading file: {e}'}), 500
        else:
            flash(f'Error downloading file: {e}', 'danger')
            return redirect(url_for('index'))

@app.route('/video-status/<int:file_id>')
@login_required
def video_status(file_id):
    """Checks the conversion status of a video file."""
    file = db.get_or_404(File, file_id)
    if not has_access(file, current_user):
        return jsonify({'status': 'error', 'message': 'Permission denied'}), 403

    cached_filename = f"cache_{file.id}_{int(file.created_at.timestamp())}.mp4"
    cached_filepath = os.path.join(VIDEO_CACHE_FOLDER, cached_filename)

    if os.path.exists(cached_filepath):
        return jsonify({'status': 'complete', 'url': url_for('download_file', file_id=file.id, inline=True)})
    else:
        return jsonify({'status': 'processing'})

@app.route('/share-with-user', methods=['POST'])
@login_required
def share_with_user():
    file_ids_str = request.form.get('file_ids', '')
    folder_ids_str = request.form.get('folder_ids', '')
    recipient_email = request.form.get('recipient_email')
    # Get permissions from the form
    can_download = 'can_download' in request.form
    can_copy = 'can_copy' in request.form
    can_reshare = 'can_reshare' in request.form

    if not (file_ids_str or folder_ids_str) or not recipient_email:
        return jsonify({'success': False, 'error': 'At least one item and a recipient email are required.'}), 400

    file_ids = [int(id) for id in file_ids_str.split(',') if id.isdigit()]
    folder_ids = [int(id) for id in folder_ids_str.split(',') if id.isdigit()]

    # --- Permission Inheritance Logic ---
    # If a folder is being shared, we don't need to create separate share records
    # for files or subfolders that are inside it. The permissions will be inherited.
    # We create a set of all folder IDs being shared for efficient lookup.
    shared_folder_id_set = set(folder_ids)
    final_file_ids_to_share = []
    for file_id in file_ids:
        file = db.session.get(File, file_id)
        # Only add the file to the share list if its parent folder is NOT also being shared.
        if file and file.folder_id not in shared_folder_id_set:
            final_file_ids_to_share.append(file_id)
    file_ids = final_file_ids_to_share # Use the filtered list

    recipient = User.query.filter_by(email=recipient_email).first()
    if not recipient:
        return jsonify({'success': False, 'error': f'User with email {recipient_email} not found.'}), 404

    if recipient.id == current_user.id:
        return jsonify({'success': False, 'error': 'You cannot share items with yourself.'}), 400

    shared_count = 0
    for file_id in file_ids:
        file = db.session.get(File, file_id)
        if file:
            if not can_reshare_item(file, current_user):
                continue

            # Check if a share already exists
            existing_share = UserFileShare.query.filter_by(user_id=recipient.id, file_id=file.id).first()
            if existing_share:
                continue # Skip if already shared

            reshared_by_id = None
            if file.user_id != current_user.id:
                reshared_by_id = current_user.id

            new_share = UserFileShare(user_id=recipient.id, file_id=file.id, can_download=can_download, can_copy=can_copy, can_reshare=can_reshare, reshared_by_id=reshared_by_id)
            db.session.add(new_share)
            sharer_message = f"You shared '{file.filename}' with {recipient.name}."
            recipient_message = f"'{current_user.name}' shared a file with you: '{file.filename}'"
            db.session.add(Notification(user_id=current_user.id, message=sharer_message))
            db.session.add(Notification(user_id=recipient.id, message=recipient_message, link=url_for('index'))) # Simplified link
            shared_count += 1

    for folder_id in folder_ids:
        folder = db.session.get(Folder, folder_id)
        if folder:
            if not can_reshare_item(folder, current_user):
                continue

            existing_share = UserFolderShare.query.filter_by(user_id=recipient.id, folder_id=folder.id).first()
            if existing_share:
                continue

            reshared_by_id = None
            if folder.user_id != current_user.id:
                reshared_by_id = current_user.id

            new_share = UserFolderShare(user_id=recipient.id, folder_id=folder.id, can_download=can_download, can_copy=can_copy, can_reshare=can_reshare, reshared_by_id=reshared_by_id)
            db.session.add(new_share)
            sharer_message = f"You shared the folder '{folder.name}' with {recipient.name}."
            recipient_message = f"'{current_user.name}' shared a folder with you: '{folder.name}'"
            db.session.add(Notification(user_id=current_user.id, message=sharer_message))
            db.session.add(Notification(user_id=recipient.id, message=recipient_message, link=url_for('index'))) # Simplified link
            shared_count += 1

    db.session.commit()

    if shared_count > 0:
        return jsonify({'success': True, 'message': f'Successfully shared {shared_count} item(s) with {recipient.name}.'})
    else:
        return jsonify({'success': False, 'error': 'No new items were shared. They may already be shared with this user.'}), 409

@app.route('/item/<item_type>/<int:item_id>/shares', methods=['GET'])
@login_required
def get_item_shares(item_type, item_id):
    if item_type == 'file':
        item = db.get_or_404(File, item_id)
        share_model = UserFileShare
    elif item_type == 'folder':
        item = db.get_or_404(Folder, item_id)
        share_model = UserFolderShare
    else:
        return jsonify({'success': False, 'error': 'Invalid item type.'}), 400

    if item.user_id != current_user.id:
        return jsonify({'success': False, 'error': 'Permission denied.'}), 403

    shares = share_model.query.filter(
        share_model.file_id == item.id if item_type == 'file' else share_model.folder_id == item.id
    ).all()
    
    shared_users = [{
        'id': share.user.id, 
        'name': share.user.name, 
        'email': share.user.email,
        'can_download': share.can_download,
        'can_copy': share.can_copy,
        'can_reshare': share.can_reshare
    } for share in shares]
    return jsonify({'success': True, 'shares': shared_users})

@app.route('/update-share-permissions', methods=['POST'])
@login_required
def update_share_permissions():
    item_id = request.form.get('item_id')
    item_type = request.form.get('item_type')
    user_id = request.form.get('user_id')
    
    if item_type == 'file':
        item = db.session.get(File, item_id)
        share_model = UserFileShare
    elif item_type == 'folder':
        item = db.session.get(Folder, item_id)
        share_model = UserFolderShare
    else:
        return jsonify({'success': False, 'error': 'Invalid item type.'}), 400

    if not item or item.user_id != current_user.id:
        return jsonify({'success': False, 'error': 'Permission denied.'}), 403

    share = share_model.query.filter_by(
        user_id=user_id,
        **{'file_id' if item_type == 'file' else 'folder_id': item.id}
    ).first()

    if not share:
        return jsonify({'success': False, 'error': 'Share not found.'}), 404

    can_download = request.form.get('can_download')
    if can_download is not None:
        share.can_download = can_download.lower() == 'true'

    can_copy = request.form.get('can_copy')
    if can_copy is not None:
        share.can_copy = can_copy.lower() == 'true'

    can_reshare = request.form.get('can_reshare')
    if can_reshare is not None:
        can_reshare_bool = can_reshare.lower() == 'true'
        if not can_reshare_bool and share.can_reshare:
            # Revoke reshares if can_reshare is being turned off
            revoke_reshare_for_user(item, share.user)
        share.can_reshare = can_reshare_bool

    db.session.commit()
    return jsonify({'success': True, 'message': 'Permissions updated.'})

@app.route('/api/notifications/unread', methods=['GET'])
@login_required
def get_unread_notifications():
    """Fetches unread notifications for the current user for real-time updates."""
    unread_notifications = Notification.query.filter_by(user_id=current_user.id, is_read=False).order_by(Notification.created_at.desc()).all()
    notifications_data = [
        {
            'id': n.id,
            'message': n.message,
            'link': n.link,
            'created_at': n.created_at.isoformat()
        } for n in unread_notifications
    ]
    return jsonify(notifications_data)

@app.route('/notifications/mark-as-read', methods=['POST'])
@login_required
def mark_notifications_as_read():
    """Marks all of the user's notifications as read."""
    try:
        # Update all unread notifications for the current user to be read
        Notification.query.filter_by(user_id=current_user.id, is_read=False).update({'is_read': True})
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Could not mark notifications as read for user {current_user.id}: {e}")
        return jsonify({'success': False, 'error': 'An internal error occurred.'}), 500

@app.route('/generate-public-selection-link')
@login_required
def generate_public_selection_link():
    file_ids_str = request.args.get('file_ids', '')
    folder_ids_str = request.args.get('folder_ids', '')

    if not file_ids_str and not folder_ids_str:
        return jsonify({'error': 'No items selected'}), 400

    # Basic check to ensure user owns all items they are trying to share
    file_ids = [int(id) for id in file_ids_str.split(',') if id.isdigit()]
    folder_ids = [int(id) for id in folder_ids_str.split(',') if id.isdigit()]

    for fid in file_ids:
        if not db.session.get(File, fid) or db.session.get(File, fid).user_id != current_user.id:
            return jsonify({'error': 'Permission denied for one or more files.'}), 403
    for fid in folder_ids:
        if not db.session.get(Folder, fid) or db.session.get(Folder, fid).user_id != current_user.id:
            return jsonify({'error': 'Permission denied for one or more folders.'}), 403

    # Token contains the selection and expires in 24 hours (86400 seconds)
    selection_data = {'file_ids': file_ids, 'folder_ids': folder_ids}
    token = s.dumps(selection_data, salt='selection-download')
    
    # The link points to a new public download endpoint
    link = url_for('public_download_selection', token=token, _external=True)
    return jsonify({'link': link})



def revoke_reshare_for_user(item, user):
    share_model = UserFileShare if isinstance(item, File) else UserFolderShare
    
    # Find users this user has shared the item with
    reshared_to_shares = share_model.query.filter_by(
        reshared_by_id=user.id,
        **{'file_id' if isinstance(item, File) else 'folder_id': item.id}
    ).all()

    for share in reshared_to_shares:
        # Recursively call to delete the chain
        revoke_reshare_for_user(item, share.user)
        db.session.delete(share)

@app.route('/unshare-item', methods=['POST'])
@login_required
def unshare_item():
    item_id = request.form.get('item_id')
    item_type = request.form.get('item_type')
    user_id_to_unshare = request.form.get('user_id')

    if not item_id or not item_type or not user_id_to_unshare:
        return jsonify({'success': False, 'error': 'Item ID, Item Type and User ID are required.'}), 400

    if item_type == 'file':
        item = db.session.get(File, item_id)
        share_model = UserFileShare
    elif item_type == 'folder':
        item = db.session.get(Folder, item_id)
        share_model = UserFolderShare
    else:
        return jsonify({'success': False, 'error': 'Invalid item type.'}), 400

    if not item:
        return jsonify({'success': False, 'error': 'Item not found.'}), 404

    if item.user_id != current_user.id:
        return jsonify({'success': False, 'error': 'You can only manage shares for your own items.'}), 403

    user_to_unshare = db.get_or_404(User, user_id_to_unshare)

    share_to_delete = share_model.query.filter_by(
        user_id=user_id_to_unshare,
        **{'file_id' if item_type == 'file' else 'folder_id': item.id}
    ).first()

    if not share_to_delete:
        return jsonify({'success': False, 'error': 'Share record not found.'}), 404

    # Revoke reshares
    revoke_reshare_for_user(item, user_to_unshare)
    
    db.session.delete(share_to_delete)
    db.session.commit()

    return jsonify({'success': True, 'message': f'Successfully unshared {item_type} from {user_to_unshare.name}.'})


@app.route('/generate-share-link/<int:file_id>')
@login_required
def generate_share_link(file_id):
    file = db.get_or_404(File, file_id)
    if file.user_id != current_user.id:
        return jsonify({'error': 'Permission denied'}), 403
    
    # Token expires in 24 hours (86400 seconds)
    token = s.dumps(file.id, salt='file-download')
    link = url_for('public_download', token=token, _external=True)
    return jsonify({'link': link})

@app.route('/public/download/<token>')
def public_download(token):
    try:
        # Max age of token is 24 hours
        file_id = s.loads(token, salt='file-download', max_age=86400)
    except Exception:
        flash('The download link is invalid or has expired.', 'danger')
        return redirect(url_for('login'))

    file = db.get_or_404(File, file_id)

    try:
        # Decrypt the file key using the master key
        master_fernet = Fernet(current_app.config['MASTER_ENCRYPTION_KEY'])
        file_key = master_fernet.decrypt(file.encrypted_key.encode('utf-8'))
        fernet = Fernet(file_key)

        # Read encrypted content from disk
        with open(file.path, 'rb') as f:
            encrypted_content = f.read()

        # Decrypt the file content
        decrypted_content = fernet.decrypt(encrypted_content)

        return send_file(
            BytesIO(decrypted_content), 
            mimetype=file.mime_type, 
            as_attachment=True, # Always download for public links
            download_name=file.filename
        )
    except Exception as e:
        app.logger.error(f"Error serving public file {file_id}: {e}")
        flash('Could not download the file due to an internal error.', 'danger')
        return redirect(url_for('login'))

@app.route('/public/download-selection/<token>')
def public_download_selection(token):
    try:
        # Max age of token is 24 hours
        selection_data = s.loads(token, salt='selection-download', max_age=86400)
        file_ids = selection_data.get('file_ids', [])
        folder_ids = selection_data.get('folder_ids', [])
    except Exception:
        flash('The download link is invalid or has expired.', 'danger')
        return redirect(url_for('login'))

    memory_file = BytesIO()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        # Add standalone files
        files = File.query.filter(File.id.in_(file_ids)).all()
        for file in files:
            try:
                master_fernet = Fernet(current_app.config['MASTER_ENCRYPTION_KEY'])
                file_key = master_fernet.decrypt(file.encrypted_key.encode('utf-8'))
                fernet = Fernet(file_key)
                with open(file.path, 'rb') as f:
                    decrypted_content = fernet.decrypt(f.read())
                zf.writestr(file.filename, decrypted_content)
            except Exception as e:
                app.logger.error(f"Failed to add file {file.filename} to public zip: {e}")

        # Add folders
        folders = Folder.query.filter(Folder.id.in_(folder_ids)).all()
        for folder in folders:
            add_folder_to_zip(folder, zf, folder.name)

    memory_file.seek(0)
    zip_filename = f"DriveMate_Shared_Archive_{datetime.utcnow().strftime('%Y-%m-%d')}.zip"
    return send_file(memory_file, mimetype='application/zip', as_attachment=True, download_name=zip_filename)


@app.route('/share-page')
def share_page():
    file_ids_str = request.args.get('files', '')
    if not file_ids_str:
        flash('No files specified for sharing.', 'warning')
        return redirect(url_for('index'))

    file_ids = [int(id) for id in file_ids_str.split(',') if id.isdigit()]
    
    # We don't check for ownership here, as the links themselves are secure.
    # This page is public.
    files = File.query.filter(File.id.in_(file_ids)).all()

    links = []
    for file in files:
        # Generate a secure, timed token for each file
        token = s.dumps(file.id, salt='file-download')
        link = url_for('public_download', token=token, _external=True)
        links.append({'filename': file.filename, 'url': link})

    return render_template('share_page.html', links=links)

@app.route('/delete-multiple', methods=['POST'])
@login_required
def delete_multiple():
    file_ids_str = request.form.get('file_ids', '')
    folder_ids_str = request.form.get('folder_ids', '')

    file_ids = [int(id) for id in file_ids_str.split(',') if id.isdigit()]
    folder_ids = [int(id) for id in folder_ids_str.split(',') if id.isdigit()]

    total_size_freed = 0
    deleted_items_count = 0

    # Delete folders first
    if folder_ids:
        folders = Folder.query.filter(Folder.id.in_(folder_ids), Folder.user_id == current_user.id).all()
        for folder in folders:
            total_size_freed += _delete_folder_recursive(folder)
            deleted_items_count += 1

    # Delete standalone files that are not part of an already-deleted folder
    if file_ids:
        files = File.query.filter(File.id.in_(file_ids), File.user_id == current_user.id).all()
        for file in files:
            # Check if the file object is still present in the session before processing
            if file in db.session:
                try:
                    os.remove(file.path)
                except FileNotFoundError:
                    app.logger.warning(f"File not found on disk during multi-delete, but proceeding to delete database record: {file.path}")
                except OSError as e:
                    app.logger.error(f'Error during multi-delete of file {file.path} from disk: {e}')
                    continue # Skip this file and move to the next one

                # This code will run if os.remove succeeded or if it was a FileNotFoundError
                total_size_freed += file.size
                db.session.delete(file)
                deleted_items_count += 1

    if total_size_freed > 0:
        current_user.used_storage -= total_size_freed
    
    if deleted_items_count > 0:
        db.session.commit()
        flash(f'{deleted_items_count} item(s) deleted successfully.', 'success')
    else:
        flash('No items were selected or you do not have permission to delete them.', 'warning')

    return redirect(request.referrer or url_for('index'))

@app.route('/delete/<int:file_id>', methods=['POST'])
@login_required
def delete_file(file_id):
    file = db.get_or_404(File, file_id) # Only the owner can delete
    if file.user_id != current_user.id:
        flash('You do not have permission to delete this file.', 'danger')
        return redirect(url_for('index'))

    try:
        os.remove(file.path)
    except FileNotFoundError:
        # If file is not found, we can still proceed to delete the DB record.
        app.logger.warning(f"File not found on disk during deletion, but proceeding to delete database record: {file.path}")
    except OSError as e:
        # For other OS errors (like permission errors), we should stop.
        flash(f'Error deleting file from disk: {e}', 'danger')
        return redirect(url_for('index'))

    # Also delete the cached video preview if it exists
    if file.mime_type == 'video/quicktime':
        cached_filename = f"cache_{file.id}_{int(file.created_at.timestamp())}.mp4"
        cached_filepath = os.path.join(VIDEO_CACHE_FOLDER, cached_filename)
        if os.path.exists(cached_filepath):
            os.remove(cached_filepath)

    current_user.used_storage -= file.size
    db.session.delete(file)
    db.session.commit()

    flash('File deleted successfully.', 'success')
    if file.folder_id:
        return redirect(url_for('index', folder_id=file.folder_id))
    return redirect(url_for('index'))
@app.route('/download-selection')
@login_required
def download_selection():
    file_ids_str = request.args.get('file_ids', '')
    folder_ids_str = request.args.get('folder_ids', '')

    if not file_ids_str and not folder_ids_str:
        flash('No items selected for download.', 'warning')
        return redirect(request.referrer or url_for('index'))

    file_ids = [int(id) for id in file_ids_str.split(',') if id.isdigit()]
    folder_ids = [int(id) for id in folder_ids_str.split(',') if id.isdigit()]

    memory_file = BytesIO()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        # Add standalone files
        files_to_zip = []
        for file_id in file_ids:
            file = db.get_or_404(File, file_id)
            if has_access(file, current_user):
                try:
                    master_fernet = Fernet(current_app.config['MASTER_ENCRYPTION_KEY'])
                    file_key = master_fernet.decrypt(file.encrypted_key.encode('utf-8'))
                    fernet = Fernet(file_key)
                    with open(file.path, 'rb') as f:
                        decrypted_content = fernet.decrypt(f.read())
                    zf.writestr(file.filename, decrypted_content)
                except Exception as e:
                    app.logger.error(f"Failed to add file {file.filename} to zip: {e}")
            else:
                app.logger.warning(f"User {current_user.id} tried to download file {file.id} without permission.")

        # Add folders
        for folder_id in folder_ids:
            folder = db.get_or_404(Folder, folder_id)
            if has_access(folder, current_user):
                add_folder_to_zip(folder, zf, folder.name)
            else:
                app.logger.warning(f"User {current_user.id} tried to download folder {folder.id} without permission.")

    memory_file.seek(0)
    zip_filename = f"DriveMate_Selection_{datetime.utcnow().strftime('%Y-%m-%d')}.zip"

    return send_file(
        memory_file,
        mimetype='application/zip',
        as_attachment=True,
        download_name=zip_filename
    )


@app.route('/api/create-zip')
@login_required
def api_create_zip():
    file_ids_str = request.args.get('file_ids', '')
    folder_ids_str = request.args.get('folder_ids', '')

    if not file_ids_str and not folder_ids_str:
        return jsonify({'error': 'No items selected'}), 400

    file_ids = [int(id) for id in file_ids_str.split(',') if id.isdigit()]
    folder_ids = [int(id) for id in folder_ids_str.split(',') if id.isdigit()]
    
    memory_file = BytesIO()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        # Add standalone files
        files = File.query.filter(File.id.in_(file_ids)).all()
        for file in files:
            if has_access(file, current_user):
                try:
                    master_fernet = Fernet(current_app.config['MASTER_ENCRYPTION_KEY'])
                    file_key = master_fernet.decrypt(file.encrypted_key.encode('utf-8'))
                    fernet = Fernet(file_key)
                    with open(file.path, 'rb') as f:
                        decrypted_content = fernet.decrypt(f.read())
                    zf.writestr(file.filename, decrypted_content)
                except Exception as e:
                    app.logger.error(f"Failed to add file {file.filename} to zip: {e}")

        # Add folders
        folders = Folder.query.filter(Folder.id.in_(folder_ids)).all()
        for folder in folders:
            if has_access(folder, current_user):
                add_folder_to_zip(folder, zf, folder.name)

        memory_file.seek(0)
    return send_file(memory_file, mimetype='application/zip')

def add_folder_to_zip(folder, zf, current_path=""):
    """Helper function to recursively add files from a folder to a zip file."""
    # Add files in the current folder
    for file in folder.files:
        try:
            # Decrypt file
            master_fernet = Fernet(current_app.config['MASTER_ENCRYPTION_KEY'])
            file_key = master_fernet.decrypt(file.encrypted_key.encode('utf-8'))
            fernet = Fernet(file_key)
            with open(file.path, 'rb') as f:
                encrypted_content = f.read()
            decrypted_content = fernet.decrypt(encrypted_content)
            
            # Add to zip with relative path
            zip_path = os.path.join(current_path, file.filename)
            zf.writestr(zip_path, decrypted_content)
        except Exception as e:
            app.logger.error(f"Failed to add file {file.filename} to zip: {e}")
            zf.writestr(os.path.join(current_path, f"ERROR_READING_{file.filename}.txt"), f"Could not include {file.filename} due to an error.".encode('utf-8'))

    # Recurse into subfolders
    for subfolder in folder.children:
        add_folder_to_zip(subfolder, zf, os.path.join(current_path, subfolder.name))

@app.route('/download-folder/<int:folder_id>')
@login_required
def download_folder(folder_id):
    folder = db.get_or_404(Folder, folder_id)
    if not has_access(folder, current_user):
        flash('You do not have permission to download this folder.', 'danger')
        return redirect(url_for('index'))

    memory_file = BytesIO()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        add_folder_to_zip(folder, zf, folder.name)

    memory_file.seek(0)
    zip_filename = f"{secure_filename(folder.name)}.zip"

    return send_file(
        memory_file,
        mimetype='application/zip',
        as_attachment=True,
        download_name=zip_filename
    )

def _copy_file_instance(source_file, dest_folder_id, user):
    """
    Helper to copy a single file instance. Returns the size of the copied file or None on failure.
    """
    try:
        # Decrypt original file
        master_fernet = Fernet(current_app.config['MASTER_ENCRYPTION_KEY'])
        source_file_key = master_fernet.decrypt(source_file.encrypted_key.encode('utf-8'))
        source_fernet = Fernet(source_file_key)
        with open(source_file.path, 'rb') as f:
            decrypted_content = source_fernet.decrypt(f.read())

        # Prepare new file path
        new_base_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(source_file.filename))
        new_final_path = get_unique_filename(new_base_path)
        new_unique_filename = os.path.basename(new_final_path)

        # Re-encrypt with new key
        new_file_key = Fernet.generate_key()
        new_fernet = Fernet(new_file_key)
        new_encrypted_content = new_fernet.encrypt(decrypted_content)
        new_file_size = len(new_encrypted_content)

        # Write new encrypted file
        with open(new_final_path, 'wb') as f:
            f.write(new_encrypted_content)

        # Copy thumbnail
        new_thumbnail_filename = None
        if source_file.thumbnail_path:
            try:
                with open(os.path.join(THUMBNAIL_FOLDER, source_file.thumbnail_path), 'rb') as f:
                    encrypted_thumb = f.read()
                decrypted_thumb = source_fernet.decrypt(encrypted_thumb)
                new_encrypted_thumb = new_fernet.encrypt(decrypted_thumb)
                thumb_name = f"thumb_{os.path.splitext(new_unique_filename)[0]}.jpg"
                thumb_path = os.path.join(THUMBNAIL_FOLDER, thumb_name)
                with open(thumb_path, 'wb') as thumb_f:
                    thumb_f.write(new_encrypted_thumb)
                new_thumbnail_filename = os.path.basename(thumb_path)
            except Exception:
                pass # Fail silently on thumbnail copy

        # Create new DB record
        new_encrypted_file_key = master_fernet.encrypt(new_file_key)
        new_file = File(
            user_id=user.id,
            folder_id=dest_folder_id,
            filename=source_file.filename,
            path=new_final_path,
            size=new_file_size,
            mime_type=source_file.mime_type,
            encrypted_key=new_encrypted_file_key.decode('utf-8'),
            thumbnail_path=new_thumbnail_filename
        )
        db.session.add(new_file)
        return new_file_size
    except Exception as e:
        app.logger.error(f"Error copying file instance for {source_file.filename}: {e}")
        return None

def _copy_folder_recursive(source_folder, dest_parent_id, user):
    """
    Recursively copies a folder and its contents for a new user.
    Returns the total size of all copied files.
    """
    new_folder = Folder(
        name=source_folder.name,
        user_id=user.id,
        parent_id=dest_parent_id
    )
    db.session.add(new_folder)
    db.session.flush()

    total_size_copied = 0
    for source_file in source_folder.files:
        copied_size = _copy_file_instance(source_file, new_folder.id, user)
        if copied_size is not None:
            total_size_copied += copied_size
        else:
            app.logger.error(f"Failed to copy file {source_file.filename} while copying folder {source_folder.name}")

    for source_subfolder in source_folder.children:
        total_size_copied += _copy_folder_recursive(source_subfolder, new_folder.id, user)
    
    return total_size_copied

@app.route('/copy-item', methods=['POST'])
@login_required
def copy_item():
    file_id = request.form.get('file_id', type=int)
    folder_id = request.form.get('folder_id', type=int)
    destination_folder_id = request.form.get('destination_folder_id')
    if destination_folder_id == 'None':
        destination_folder_id = None

    if destination_folder_id:
        dest_folder = db.get_or_404(Folder, destination_folder_id)
        if dest_folder.user_id != current_user.id:
            flash('Invalid destination folder.', 'danger')
            return redirect(request.referrer or url_for('index'))

    if file_id:
        source_file = db.get_or_404(File, file_id)
        if not can_copy_item(source_file, current_user):
            flash('You do not have permission to copy this file.', 'danger')
            return redirect(request.referrer)
        
        copied_size = _copy_file_instance(source_file, destination_folder_id, current_user)
        if copied_size is not None:
            current_user.used_storage += copied_size
            db.session.commit()
            flash(f"Successfully copied '{source_file.filename}' to your files.", 'success')
        else:
            db.session.rollback()
            flash(f"Failed to copy '{source_file.filename}'.", 'danger')

    elif folder_id:
        source_folder = db.get_or_404(Folder, folder_id)
        if not can_copy_item(source_folder, current_user):
            flash('You do not have permission to copy this folder.', 'danger')
            return redirect(request.referrer)

        try:
            copied_size = _copy_folder_recursive(source_folder, destination_folder_id, current_user)
            current_user.used_storage += copied_size
            db.session.commit()
            flash(f"Successfully copied folder '{source_folder.name}'.", 'success')
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error during recursive copy of folder {folder_id}: {e}")
            flash(f"Failed to copy folder '{source_folder.name}'. An error occurred.", 'danger')

    return redirect(request.referrer or url_for('index'))

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender=current_app.config['MAIL_DEFAULT_SENDER'],
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)

@app.route("/forgot-password", methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            send_reset_email(user)
            flash('An email has been sent with instructions to reset your password.', 'info')
            return redirect(url_for('login'))
        else:
            flash('Email address not found.', 'warning')
    return render_template('forgot_password.html')

@app.route("/reset-password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('forgot_password'))
    if request.method == 'POST':
        password = request.form.get('password')
        user.set_password(password)
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_password.html')

@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    total_users = User.query.count()
    total_storage_used = db.session.query(db.func.sum(User.used_storage)).scalar() or 0
    total_active_subscriptions = Subscription.query.filter_by(active=True).count()
    # Placeholder for total earnings
    total_earnings = 0 
    return render_template('admin.html', 
                           total_users=total_users, 
                           total_storage_used=total_storage_used, 
                           total_active_subscriptions=total_active_subscriptions, 
                           total_earnings=total_earnings)

@app.route('/admin/plans')
@login_required
@admin_required
def admin_plans():
    plans = Plan.query.all()
    return render_template('admin_plans.html', plans=plans)

@app.route('/admin/create-plan', methods=['POST'])
@login_required
@admin_required
def create_plan():
    name = request.form['name']
    size_limit = int(request.form['size_limit']) * 1024 * 1024 * 1024 # Convert GB to bytes
    price = float(request.form['price'])
    duration = int(request.form['duration'])

    if not name or not size_limit or not price or not duration:
        flash('All fields are required.', 'warning')
    else:
        new_plan = Plan(name=name, size_limit=size_limit, price=price, duration=duration)
        db.session.add(new_plan)
        db.session.commit()
        flash('Plan created successfully!', 'success')

    return redirect(url_for('admin_plans'))

@app.route('/admin/delete-plan/<int:plan_id>', methods=['POST'])
@login_required
@admin_required
def delete_plan(plan_id):
    plan = db.get_or_404(Plan, plan_id)
    db.session.delete(plan)
    db.session.commit()
    flash('Plan deleted successfully!', 'success')
    return redirect(url_for('admin_plans'))

@app.route('/admin/storage_summary')
@login_required
@admin_required
def admin_storage_summary():
    users = User.query.all()
    total_storage_used = db.session.query(db.func.sum(User.used_storage)).scalar() or 0
    return render_template('admin_storage_summary.html', users=users, total_storage_used=total_storage_used)

@app.route('/admin/subscriptions_summary')
@login_required
@admin_required
def admin_subscriptions_summary():
    # Get all subscriptions for the detailed list view, ordered by most recent
    subscriptions = Subscription.query.order_by(Subscription.start_date.desc()).all()

    # Calculate active subscriber counts for each plan for the summary view
    plans = Plan.query.all()
    plans_with_counts = []
    for plan in plans:
        # Count active subscriptions by filtering the plan's subscription relationship.
        active_count = sum(1 for sub in plan.subscriptions if sub.active)
        plans_with_counts.append({'name': plan.name, 'count': active_count})

    return render_template('admin_subscriptions_summary.html', subscriptions=subscriptions, plans_with_counts=plans_with_counts)

@app.route('/admin/earnings_summary')
@login_required
@admin_required
def admin_earnings_summary():
    payments = Payment.query.all()
    total_earnings = db.session.query(db.func.sum(Payment.amount)).scalar() or 0
    return render_template('admin_earnings_summary.html', payments=payments, total_earnings=total_earnings)

@app.route('/pricing')
@login_required
def pricing():
    plans = Plan.query.all()
    return render_template('pricing.html', plans=plans)

@app.route('/subscribe/<int:plan_id>')
@login_required
def subscribe(plan_id):
    new_plan = db.get_or_404(Plan, plan_id)

    # --- Logic for a new user subscribing for the first time ---
    if not current_user.plan_id:
        if new_plan.price is None or new_plan.price == 0:
            current_user.plan_id = new_plan.id
            start_date = datetime.utcnow()
            end_date = start_date + timedelta(days=365 * 100)
            new_subscription = Subscription(user_id=current_user.id, plan_id=new_plan.id, start_date=start_date, end_date=end_date, active=True)
            db.session.add(new_subscription)
            db.session.commit()
            flash(f'You have successfully subscribed to the {new_plan.name} plan!', 'success')
            return redirect(url_for('index'))
        else:
            # New paid subscription - create Razorpay order
            amount_in_paise = int(new_plan.price * 100)
            order_data = {
                'amount': amount_in_paise,
                'currency': 'INR',
                'receipt': f'receipt_{current_user.id}_{datetime.utcnow().timestamp()}'
            }
            try:
                order = razorpay_client.order.create(data=order_data)
            except Exception as e:
                flash(f'Error contacting payment gateway: {e}', 'danger')
                return redirect(url_for('pricing'))

            session['payment_info'] = {
                'plan_id': new_plan.id,
                'amount': new_plan.price,
                'type': 'new_subscription',
                'razorpay_order_id': order['id']
            }
            return redirect(url_for('payment_page'))

    # --- Logic for user with an existing plan (UPGRADE) ---
    else:
        current_subscription = Subscription.query.filter_by(user_id=current_user.id, active=True).first()

        if not current_subscription:
            current_user.plan_id = None
            db.session.commit()
            return subscribe(plan_id)

        current_plan = current_subscription.plan

        if current_plan.id == new_plan.id:
            flash('You are already subscribed to this plan.', 'info')
            return redirect(url_for('subscription'))

        current_price = current_plan.price or 0.0
        new_price = new_plan.price or 0.0

        if new_price <= current_price:
            flash('Downgrading plans is not yet supported. Please contact support for assistance.', 'info')
            return redirect(url_for('pricing'))

        # --- UPGRADE LOGIC ---
        remaining_days = (current_subscription.end_date - datetime.utcnow()).days
        if remaining_days < 0:
            remaining_days = 0
        
        credit = current_price * (remaining_days / 30.0)
        final_price = new_price - credit
        if final_price < 0:
            final_price = 0

        # If prorated amount is zero or less, upgrade directly without payment
        if final_price <= 0:
            current_subscription.active = False
            start_date = datetime.utcnow()
            end_date = start_date + timedelta(days=new_plan.duration * 30)
            new_subscription = Subscription(user_id=current_user.id, plan_id=new_plan.id, start_date=start_date, end_date=end_date, active=True)
            db.session.add(new_subscription)
            current_user.plan_id = new_plan.id
            db.session.commit()
            flash(f'Successfully upgraded to the {new_plan.name} plan!', 'success')
            return redirect(url_for('subscription'))

        # Create Razorpay order for upgrade
        amount_in_paise = int(final_price * 100)
        order_data = {
            'amount': amount_in_paise,
            'currency': 'INR',
            'receipt': f'receipt_upgrade_{current_user.id}_{datetime.utcnow().timestamp()}'
        }
        try:
            order = razorpay_client.order.create(data=order_data)
        except Exception as e:
            flash(f'Error contacting payment gateway: {e}', 'danger')
            return redirect(url_for('pricing'))

        session['payment_info'] = {
            'plan_id': new_plan.id,
            'amount': final_price,
            'type': 'upgrade',
            'razorpay_order_id': order['id']
        }
        return redirect(url_for('payment_page'))

@app.route('/payment', methods=['GET'])
@login_required
def payment_page():
    payment_info = session.get('payment_info')
    if not payment_info or 'razorpay_order_id' not in payment_info:
        flash('No payment to process or session expired.', 'warning')
        return redirect(url_for('pricing'))
    
    plan = db.get_or_404(Plan, payment_info['plan_id'])
    amount = payment_info['amount']
    
    return render_template('payment.html', 
                           plan=plan, 
                           amount=amount, 
                           razorpay_key_id=app.config['RAZORPAY_KEY_ID'],
                           razorpay_order_id=payment_info['razorpay_order_id'],
                           user_name=current_user.name,
                           user_email=current_user.email)

@app.route('/payment-verification', methods=['POST'])
@login_required
def payment_verification():
    payment_info = session.get('payment_info')
    if not payment_info:
        flash('Payment session expired or invalid. Please try again.', 'danger')
        return redirect(url_for('pricing'))

    # Get payment details from the form submitted by Razorpay checkout
    razorpay_payment_id = request.form.get('razorpay_payment_id')
    razorpay_order_id = request.form.get('razorpay_order_id')
    razorpay_signature = request.form.get('razorpay_signature')

    # Verify the signature
    params_dict = {
        'razorpay_order_id': razorpay_order_id,
        'razorpay_payment_id': razorpay_payment_id,
        'razorpay_signature': razorpay_signature
    }
    try:
        razorpay_client.utility.verify_payment_signature(params_dict)
    except razorpay.errors.SignatureVerificationError as e:
        app.logger.error(f"Razorpay signature verification failed: {e}")
        flash('Payment verification failed. Please contact support if the amount was debited.', 'danger')
        return redirect(url_for('pricing'))

    # Signature is verified, now process the subscription
    plan_id = payment_info['plan_id']
    amount = payment_info['amount']
    payment_type = payment_info['type']
    new_plan = db.get_or_404(Plan, plan_id)

    if payment_type == 'upgrade':
        current_subscription = Subscription.query.filter_by(user_id=current_user.id, active=True).first()
        if current_subscription:
            current_subscription.active = False
        flash_message = f'Successfully upgraded to the {new_plan.name} plan!'
    elif payment_type == 'new_subscription':
        flash_message = f'You have successfully subscribed to the {new_plan.name} plan!'

    # Create new subscription
    start_date = datetime.utcnow()
    end_date = start_date + timedelta(days=new_plan.duration * 30)
    new_subscription = Subscription(user_id=current_user.id, plan_id=new_plan.id, start_date=start_date, end_date=end_date, active=True)
    db.session.add(new_subscription)

    # Create payment record
    payment = Payment(user_id=current_user.id, plan_id=new_plan.id, amount=amount, status='success', txn_id=razorpay_payment_id)
    db.session.add(payment)

    # Update user's plan
    current_user.plan_id = new_plan.id

    # Clean up session and commit
    session.pop('payment_info', None)
    db.session.commit()
    
    flash(flash_message, 'success')
    return redirect(url_for('subscription'))

@app.route('/storage')
@login_required
def storage():
    user_files = File.query.filter_by(user_id=current_user.id).all()
    total_files = len(user_files)
    total_size = sum(file.size for file in user_files)
    return render_template('storage.html', total_files=total_files, total_size=total_size)

@app.route('/subscription')
@login_required
def subscription():
    current_subscription = Subscription.query.filter_by(user_id=current_user.id, active=True).first()
    return render_template('subscription.html', current_subscription=current_subscription)

if __name__ == '__main__':
    app.run(ssl_context=('localhost+1.pem', 'localhost+1-key.pem'), host='0.0.0.0', port=8080)
