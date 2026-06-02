from flask import Flask, render_template, request, redirect, session
from pymongo import MongoClient
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.security import check_password_hash
from bson.objectid import ObjectId
from flask import flash
from collections import defaultdict
from datetime import datetime, timedelta
import os
import secrets
import string

load_dotenv()

def update_logo_and_assets():
    import os
    import shutil
    import sys
    import subprocess
    
    log_file = os.path.join(os.path.dirname(__file__), "logo_copy_log.txt")
    try:
        with open(log_file, "a") as log:
            log.write("--- update_logo_and_assets run ---\n")
            
            src_win = "C:/Users/sandy/.gemini/antigravity/brain/ed363bba-36d6-49b6-b42d-6ca143fc1171/wallet_logo_1780367776750.png"
            src_wsl = "/mnt/c/Users/sandy/.gemini/antigravity/brain/ed363bba-36d6-49b6-b42d-6ca143fc1171/wallet_logo_1780367776750.png"
            
            src = src_win
            if not os.path.exists(src) and os.path.exists(src_wsl):
                src = src_wsl
                
            dst = os.path.join(os.path.dirname(__file__), "static", "images", "logo.png")
            
            log.write(f"src_win exists: {os.path.exists(src_win)}\n")
            log.write(f"src_wsl exists: {os.path.exists(src_wsl)}\n")
            log.write(f"resolved src: {src}\n")
            log.write(f"dst: {dst}\n")
            log.write(f"resolved src exists: {os.path.exists(src)}\n")
            
            if os.path.exists(src):
                try:
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    # Check first 4 bytes of source
                    with open(src, "rb") as sf:
                        src_head = sf.read(4)
                    log.write(f"Source file head (first 4 bytes): {src_head}\n")
                    
                    # Ensure Pillow is installed
                    try:
                        from PIL import Image, ImageDraw
                    except ImportError:
                        log.write("Pillow not found. Attempting dynamic pip install pillow...\n")
                        installed = False
                        # Try standard user install
                        try:
                            subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "pillow"])
                            installed = True
                            log.write("Dynamic pip install pillow --user succeeded!\n")
                        except Exception as e1:
                            log.write(f"Standard user install failed: {e1}\n")
                        
                        # Try break system packages (useful for newer Python system-wide environments)
                        if not installed:
                            try:
                                subprocess.check_call([sys.executable, "-m", "pip", "install", "pillow", "--break-system-packages"])
                                installed = True
                                log.write("Dynamic pip install pillow --break-system-packages succeeded!\n")
                            except Exception as e2:
                                log.write(f"Break system packages install failed: {e2}\n")
                                
                        # Try user + break system packages
                        if not installed:
                            try:
                                subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "pillow", "--break-system-packages"])
                                installed = True
                                log.write("Dynamic pip install pillow --user --break-system-packages succeeded!\n")
                            except Exception as e3:
                                log.write(f"User + break system packages install failed: {e3}\n")
                    
                    # Try to process the image and remove checkerboard background using PIL (Pillow)
                    processed_ok = False
                    try:
                        from PIL import Image, ImageDraw
                        log.write("PIL imported successfully. Removing checkerboard background...\n")
                        img = Image.open(src).convert("RGBA")
                        width, height = img.size
                        # Flood-fill transparency from the 4 corners to remove the grid background
                        for corner in [(0, 0), (0, height - 1), (width - 1, 0), (width - 1, height - 1)]:
                            ImageDraw.floodfill(img, corner, (0, 0, 0, 0), thresh=120)
                        
                        # Crop the empty transparent margins from all 4 sides of the image
                        bbox = img.getbbox()
                        if bbox:
                            img = img.crop(bbox)
                            log.write(f"Image cropped from {width}x{height} to {img.width}x{img.height}\n")
                        
                        img.save(dst, "PNG")
                        processed_ok = True
                        log.write("Image processed (flood-fill transparency and cropped) and saved successfully!\n")
                    except Exception as pil_err:
                        log.write(f"PIL background removal failed or not installed: {pil_err}\n")
                        print("Pillow background removal failed, falling back to direct copy:", pil_err)
                    
                    if not processed_ok:
                        # Fallback to direct copy if PIL is not installed
                        shutil.copyfile(src, dst)
                        log.write("Fallback: Direct copy success!\n")
                    
                    # Ensure file is globally readable
                    try:
                        os.chmod(dst, 0o644)
                    except Exception as chmod_err:
                        log.write(f"Chmod error: {chmod_err}\n")
                    
                    # Check destination file size and head
                    dst_size = os.path.getsize(dst)
                    with open(dst, "rb") as df:
                        dst_head = df.read(4)
                    log.write(f"Final dst Size: {dst_size} bytes, head: {dst_head}\n")
                    print("Logo updated successfully to:", dst)
                except Exception as e:
                    log.write(f"Copy/process error: {e}\n")
                    print("Error updating logo:", e)
            else:
                log.write("Source does not exist!\n")
    except Exception as e:
        print("Logging failed:", e)
            
    # 2. Update HTML files to replace emoji logo with img tag and ensure cache-busting version parameter is set to v=8
    templates_dir = os.path.join(os.path.dirname(__file__), "templates")
    if os.path.exists(templates_dir):
        for filename in os.listdir(templates_dir):
            if filename.endswith(".html"):
                filepath = os.path.join(templates_dir, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()
                    
                    original_content = content
                    
                    # Replacement target 1: Standard Logo
                    target1_old = '<div class="logo">💰 Expense Tracker</div>'
                    target1_new = '<div class="logo" style="display: flex; align-items: center; gap: 5px;"><img src="{{ url_for(\'static\', filename=\'images/logo.png\', v=\'10\') }}" alt="Logo" style="height: 55px; width: 55px; object-fit: contain; margin-right: -16px; transform: translateY(-6px);"><span>Expense Tracker</span></div>'
                    content = content.replace(target1_old, target1_new)
                    
                    # Replacement target 2: Logo with extra space/newlines
                    target2_old = '<div class="logo">\n        💰 Expense Tracker\n    </div>'
                    target2_new = '<div class="logo" style="display: flex; align-items: center; gap: 5px;"><img src="{{ url_for(\'static\', filename=\'images/logo.png\', v=\'10\') }}" alt="Logo" style="height: 55px; width: 55px; object-fit: contain; margin-right: -16px; transform: translateY(-6px);"><span>Expense Tracker</span></div>'
                    content = content.replace(target2_old, target2_new)
                    
                    # Replacement target 3: Admin Logo
                    target3_old = '<div class="logo" style="display: flex; align-items: center;">\n        💰 Expense Tracker <span class="admin-badge">Admin</span>\n    </div>'
                    target3_new = '<div class="logo" style="display: flex; align-items: center; gap: 5px;"><img src="{{ url_for(\'static\', filename=\'images/logo.png\', v=\'10\') }}" alt="Logo" style="height: 55px; width: 55px; object-fit: contain; margin-right: -16px; transform: translateY(-6px);"><span>Expense Tracker</span> <span class="admin-badge">Admin</span></div>'
                    content = content.replace(target3_old, target3_new)
                    
                    # Target 4: Admin Logo alternative line endings
                    content = content.replace(target3_old.replace('\n', '\r\n'), target3_new)
                    content = content.replace(target2_old.replace('\n', '\r\n'), target2_new)
                    
                    # Replace logo.jpg references with logo.png
                    content = content.replace("logo.jpg", "logo.png")
                    
                    # Upgrade any existing image tag references to the cache-busting version parameter
                    content = content.replace("filename='images/logo.png'", "filename='images/logo.png', v='10'")
                    content = content.replace('filename="images/logo.png"', "filename='images/logo.png', v='10'")
                    
                    # Replace logo size adjustments
                    content = content.replace("height: 50px; width: 50px;", "height: 55px; width: 55px;")
                    content = content.replace("height: 48px; width: 48px;", "height: 55px; width: 55px;")
                    content = content.replace("height: 42px; width: 42px;", "height: 55px; width: 55px;")
                    content = content.replace("height: 32px; width: 32px;", "height: 55px; width: 55px;")
                    
                    # Replace gap and add negative margin + transform to pull text closer and nudge logo up
                    content = content.replace("gap: 10px;", "gap: 5px;")
                    content = content.replace("margin-right: -8px;", "margin-right: -16px; transform: translateY(-6px);")
                    content = content.replace('margin-right: -16px;">', 'margin-right: -16px; transform: translateY(-6px);">')
                    content = content.replace('object-fit: contain;">', 'object-fit: contain; margin-right: -16px; transform: translateY(-6px);">')
                    
                    # Deduplicate if margin-right/transform is already added
                    content = content.replace('margin-right: -16px; transform: translateY(-6px); margin-right: -16px; transform: translateY(-6px);', 'margin-right: -16px; transform: translateY(-6px);')
                    content = content.replace('margin-right: -16px; margin-right: -16px;', 'margin-right: -16px;')
                    
                    # Clean up old versions
                    content = content.replace(", v='9'", "")
                    content = content.replace(', v="9"', "")
                    content = content.replace(", v='8'", "")
                    content = content.replace(', v="8"', "")
                    content = content.replace(", v='7'", "")
                    content = content.replace(', v="7"', "")
                    content = content.replace(", v='6'", "")
                    content = content.replace(', v="6"', "")
                    content = content.replace(", v='5'", "")
                    content = content.replace(', v="5"', "")
                    content = content.replace(", v='4'", "")
                    content = content.replace(', v="4"', "")
                    content = content.replace(", v='3'", "")
                    content = content.replace(', v="3"', "")
                    content = content.replace(", v='2'", "")
                    content = content.replace(', v="2"', "")
                    
                    # Let's also do direct replacement of existing style attributes from previous versions
                    content = content.replace('translateY(-3px)', 'translateY(-6px)')
                    
                    # Ensure only a single v='10' is kept
                    content = content.replace("v='10', v='10'", "v='10'")
                    
                    if content != original_content:
                        with open(filepath, "w", encoding="utf-8") as f:
                            f.write(content)
                        print(f"Updated logo in: {filename}")
                except Exception as e:
                    print(f"Error updating {filename}: {e}")

# Only run asset updates locally, not in cloud environments like Vercel or Render
if not os.getenv("VERCEL") and not os.getenv("RENDER"):
    update_logo_and_assets()


app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "secret123")

# MongoDB connection - clean up any accidental newlines or spaces from Render copy-pasting
try:
    raw_mongo_uri = os.getenv("MONGO_URI")
    import sys
    print("DEBUG MONGO_URI raw:", repr(raw_mongo_uri), file=sys.stderr, flush=True)
    if raw_mongo_uri:
        raw_mongo_uri = raw_mongo_uri.strip().replace("\n", "").replace("\r", "").replace(" ", "")
        print("DEBUG MONGO_URI sanitized:", repr(raw_mongo_uri), file=sys.stderr, flush=True)
    client = MongoClient(raw_mongo_uri)
    db = client.expense_tracker
except Exception as e:
    import sys
    print("CRITICAL ERROR during MongoDB connection initialization:", str(e), file=sys.stderr, flush=True)
    print("MONGO_URI value read was:", repr(raw_mongo_uri), file=sys.stderr, flush=True)
    raise e
users_collection = db.users
expenses_collection = db.expenses
reset_tokens_collection = db.reset_tokens
goals_collection = db.goals





@app.route('/')
def home():
    return render_template('home.html')




@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Find user in MongoDB
        user = users_collection.find_one({"email": email})

        if user and check_password_hash(user['password'], password):
            session['user'] = email
            session['name'] = user['name']
            flash(f"Welcome back, {user['name']}!", "success")
            return redirect('/dashboard')
        else:
            flash("Invalid email or password")
            return redirect('/login')

    return render_template('login.html')


@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        
        # Check if user exists
        user = users_collection.find_one({"email": email})
        
        if not user:
            flash("If an account exists with this email, you will receive a password reset link.")
            return redirect('/login')
        
        # Generate a secure token
        token = secrets.token_urlsafe(32)
        expiration_time = datetime.utcnow() + timedelta(hours=1)
        
        # Store reset token in database
        reset_tokens_collection.insert_one({
            "email": email,
            "token": token,
            "expires_at": expiration_time,
            "created_at": datetime.utcnow()
        })
        
        # Redirect directly to reset password page with token
        return redirect(f'/reset-password/{token}')
    
    return render_template('forgot_password.html')


@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    # Check if token exists and is valid
    reset_token = reset_tokens_collection.find_one({"token": token})
    
    if not reset_token:
        flash("Invalid or expired reset link")
        return redirect('/forgot-password')
    
    if reset_token['expires_at'] < datetime.utcnow():
        reset_tokens_collection.delete_one({"token": token})
        flash("Reset link has expired. Please request a new one.")
        return redirect('/forgot-password')
    
    if request.method == 'POST':
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if new_password != confirm_password:
            flash("Passwords do not match")
            return render_template('reset_password.html', token=token)
        
        if len(new_password) < 7:
            flash("Password must be at least 7 characters long")
            return render_template('reset_password.html', token=token)
        
        email = reset_token['email']
        
        # Get user's current password for history
        user = users_collection.find_one({"email": email})
        current_password = user.get('password')
        
        # Hash new password
        hashed_password = generate_password_hash(new_password)
        
        # Update password and add to history
        users_collection.update_one(
            {"email": email},
            {
                "$set": {"password": hashed_password},
                "$push": {
                    "password_history": {
                        "old_password": current_password,
                        "changed_at": datetime.utcnow()
                    }
                }
            }
        )
        
        # Delete the used token
        reset_tokens_collection.delete_one({"token": token})
        
        flash("Password has been reset successfully. Please login with your new password.")
        return redirect('/login')
    
    return render_template('reset_password.html', token=token)


@app.route('/change-password', methods=['GET', 'POST'])
def change_password():
    if 'user' not in session:
        return redirect('/login')
    
    if request.method == 'POST':
        email = session['user']
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Find user
        user = users_collection.find_one({"email": email})
        
        if not user:
            flash("User not found")
            return redirect('/change-password')
        
        # Verify old password
        if not check_password_hash(user['password'], old_password):
            flash("Current password is incorrect")
            return redirect('/change-password')
        
        # Check if new passwords match
        if new_password != confirm_password:
            flash("New passwords do not match")
            return redirect('/change-password')
        
        if len(new_password) < 7:
            flash("New password must be at least 7 characters long")
            return redirect('/change-password')
        
        # Check if new password is same as old password
        if check_password_hash(user['password'], new_password):
            flash("New password cannot be the same as current password")
            return redirect('/change-password')
        
        # Get current password for history
        current_password = user.get('password')
        
        # Hash new password
        hashed_password = generate_password_hash(new_password)
        
        # Update password and add to history
        users_collection.update_one(
            {"email": email},
            {
                "$set": {"password": hashed_password},
                "$push": {
                    "password_history": {
                        "old_password": current_password,
                        "changed_at": datetime.utcnow()
                    }
                }
            }
        )
        
        session.clear()
        flash("Password changed successfully! Please log in with your new password.", "success")
        return redirect('/login')
    
    return render_template('change_password.html')


def send_contact_email(first_name, last_name, user_email, phone, subject, description):
    import urllib.request
    import urllib.parse

    formspree_url = os.getenv("FORMSPREE_URL")
    
    if not formspree_url:
        print("Warning: FORMSPREE_URL environment variable not set in .env. Email notification skipped.")
        return False

    try:
        # Prepare URL-encoded form data matching Formspree format
        data = urllib.parse.urlencode({
            "First Name": f"{first_name} {last_name}",
            "Email Address": user_email,
            "Phone Number": phone,
            "Subject": subject,
            "Message": description
        }).encode('utf-8')
        
        # Dispatch POST request to Formspree
        req = urllib.request.Request(
            formspree_url,
            data=data,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.status == 200
    except Exception as e:
        print(f"Error sending email via Formspree: {e}")
        return False


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if 'user' not in session:
        return redirect('/login')

    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        subject = request.form.get('subject')
        description = request.form.get('description')

        # Save to MongoDB
        db.contact_messages.insert_one({
            "email_user": session['user'],
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone": phone,
            "subject": subject,
            "description": description,
            "created_at": datetime.utcnow()
        })

        # Send email notification
        send_contact_email(first_name, last_name, email, phone, subject, description)

        flash("Message sent successfully! We will get back to you soon.")
        return redirect('/contact')

    return render_template('contact.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        # Check if user already exists
        existing_user = users_collection.find_one({"email": email})
        if existing_user:
            flash("User already exists")
            return redirect('/signup')

        if len(password) < 7:
            flash("Password must be at least 7 characters long")
            return redirect('/signup')

        # Hash password
        hashed_password = generate_password_hash(password)

        # Save user to MongoDB
        users_collection.insert_one({
            "name": name,
            "email": email,
            "password": hashed_password
        })

        flash("Your account was created successfully! Please log in.", "success")
        return redirect('/login')

    return render_template('signup.html')



@app.route('/test-db')
def test_db():
    users_collection.insert_one({"test": "MongoDB Connected"})
    return "MongoDB Working!"


@app.route('/add-expense', methods=['GET', 'POST'])
def add_expense():
    if 'user' not in session:
        return redirect('/login')

    if request.method == 'POST':
        expense = {
            "email": session['user'],
            "date": request.form['date'],
            "item": request.form['item'],
            "category": request.form.get('category', 'Other'),
            "amount": request.form['amount']
        }
        expenses_collection.insert_one(expense)
        flash("Your expense was added successfully", "success")
        return redirect('/manage-expense')

    return render_template('add_expense.html')



@app.route('/manage-expense')
def manage_expense():
    if 'user' not in session:
        return redirect('/login')

    expenses = expenses_collection.find(
        {"email": session['user']}
    ).sort("_id", -1)

    return render_template(
        'manage_expense.html',
        expenses=expenses
    )



@app.route('/delete-expense/<id>')
def delete_expense(id):
    if 'user' not in session:
        return redirect('/login')

    expenses_collection.delete_one(
        {"_id": ObjectId(id)}
    )
    return redirect('/manage-expense')


@app.route('/edit-expense/<id>', methods=['GET', 'POST'])
def edit_expense(id):
    if 'user' not in session:
        return redirect('/login')

    expense = expenses_collection.find_one(
        {"_id": ObjectId(id)}
    )

    if request.method == 'POST':
        expenses_collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": {
                "date": request.form['date'],
                "item": request.form['item'],
                "category": request.form.get('category', 'Other'),
                "amount": request.form['amount']
            }}
        )
        flash("Expense edited successfully", "success")
        return redirect('/manage-expense')

    return render_template(
        'edit_expense.html',
        expense=expense
    )


@app.route('/expense-report', methods=['GET', 'POST'])
def expense_report():
    if 'user' not in session:
        return redirect('/login')

    expenses = []
    total = 0

    if request.method == 'POST':
        if 'single_date' in request.form:
            single_date = request.form['single_date']
            expenses = list(expenses_collection.find({
                "email": session['user'],
                "date": single_date
            }).sort([("date", -1), ("_id", -1)]))
        elif 'from_date' in request.form and 'to_date' in request.form:
            from_date = request.form['from_date']
            to_date = request.form['to_date']

            expenses = list(expenses_collection.find({
                "email": session['user'],
                "date": {
                    "$gte": from_date,
                    "$lte": to_date
                }
            }).sort([("date", -1), ("_id", -1)]))
        elif 'category' in request.form:
            category = request.form['category']
            expenses = list(expenses_collection.find({
                "email": session['user'],
                "category": category
            }).sort([("date", -1), ("_id", -1)]))
        elif 'amount_condition' in request.form and 'filter_amount' in request.form:
            condition = request.form['amount_condition']
            try:
                amount_int = int(request.form['filter_amount'])
                if condition == 'equal':
                    query_cond = {"$eq": [{"$toInt": "$amount"}, amount_int]}
                elif condition == 'above':
                    query_cond = {"$gt": [{"$toInt": "$amount"}, amount_int]}
                elif condition == 'below':
                    query_cond = {"$lt": [{"$toInt": "$amount"}, amount_int]}
                else:
                    query_cond = {"$eq": [{"$toInt": "$amount"}, amount_int]}

                expenses = list(expenses_collection.find({
                    "email": session['user'],
                    "$expr": query_cond
                }).sort([("date", -1), ("_id", -1)]))
            except ValueError:
                expenses = []

        total = sum(int(exp['amount']) for exp in expenses)

    return render_template(
        'expense_report.html',
        expenses=expenses,
        total=total
    )



@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')

    email = session['user']
    name = session.get('name')
    print("Logged user name:", name)

    # Fetch user for budget
    user = users_collection.find_one({"email": email})
    budget = user.get('budget', 0) if user else 0

    expenses = list(expenses_collection.find({"email": email}))

  
    category_totals = defaultdict(int)
    for exp in expenses:
        category = exp.get('category', 'Other')
        category_totals[category] += int(exp['amount'])

    labels = list(category_totals.keys())
    values = list(category_totals.values())


    today = datetime.today().date()
    yesterday = today - timedelta(days=1)
    last_7 = today - timedelta(days=7)
    last_30 = today - timedelta(days=30)
    year_start = today.replace(month=1, day=1)
    month_start = today.replace(day=1)

    today_total = 0
    yesterday_total = 0
    last7_total = 0
    last30_total = 0
    year_total = 0
    month_total = 0
    total_expense = 0

    for exp in expenses:
        amount = int(exp['amount'])
        exp_date = datetime.strptime(exp['date'], "%Y-%m-%d").date()
        total_expense += amount

        if exp_date == today:
            today_total += amount
        if exp_date == yesterday:
            yesterday_total += amount
        if exp_date >= last_7:
            last7_total += amount
        if exp_date >= last_30:
            last30_total += amount
        if exp_date >= month_start:
            month_total += amount
        if exp_date >= year_start:
            year_total += amount

    # Calculate last 7 months spending for bar chart
    monthly_stats = {}
    temp_date = today.replace(day=1)
    for _ in range(7):
        m_label = temp_date.strftime("%b %Y")
        monthly_stats[m_label] = 0
        if temp_date.month == 1:
            temp_date = temp_date.replace(year=temp_date.year - 1, month=12)
        else:
            temp_date = temp_date.replace(month=temp_date.month - 1)
            
    bar_labels = list(monthly_stats.keys())[::-1]
    for exp in expenses:
        e_date = datetime.strptime(exp['date'], "%Y-%m-%d").date()
        e_label = e_date.strftime("%b %Y")
        if e_label in monthly_stats:
            monthly_stats[e_label] += int(exp['amount'])
    bar_values = [monthly_stats[label] for label in bar_labels]


    return render_template(
        'dashboard.html',
        name=name,
        labels=labels,
        values=values,
        bar_labels=bar_labels,
        bar_values=bar_values,

        # 🔹 box values
        today=today_total,
        yesterday=yesterday_total,
        last7=last7_total,
        last30=last30_total,
        year=year_total,
        total=total_expense,
        budget=budget,
        month_total=month_total,
        budget_exceeded=(budget > 0 and month_total > budget),
        
        # 🔹 Goals data
        goals=list(goals_collection.find({"email": email})),
        current_savings=max(0, budget - month_total) if budget > 0 else 0
    )

@app.route('/set-budget', methods=['POST'])
def set_budget():
    if 'user' not in session:
        return redirect('/login')
    
    email = session['user']
    try:
        budget = int(request.form.get('budget', 0))
    except ValueError:
        budget = 0
        
    users_collection.update_one(
        {"email": email},
        {"$set": {"budget": budget}}
    )
    return redirect('/dashboard')


@app.route('/add-goal', methods=['POST'])
def add_goal():
    if 'user' not in session:
        return redirect('/login')
    
    email = session['user']
    name = request.form.get('goal_name')
    target = request.form.get('goal_target')
    
    if name and target:
        goals_collection.insert_one({
            "email": email,
            "name": name,
            "target": int(target),
            "created_at": datetime.utcnow()
        })
    
    return redirect('/dashboard')


@app.route('/delete-goal/<id>')
def delete_goal(id):
    if 'user' not in session:
        return redirect('/login')
    
    goals_collection.delete_one({"_id": ObjectId(id)})
    return redirect('/dashboard')


@app.route('/logout')
def logout():
    session.clear()
    return render_template('logout.html')


@app.route('/user-dashboard')
def user_dashboard():
    if 'user' not in session:
        return redirect('/login')
    
    email = session['user']
    user = users_collection.find_one({"email": email})
    name = user.get('name') if user else ''
    budget = user.get('budget', 0) if user else 0
    
    # Calculate current month's expenses
    today = datetime.today().date()
    month_start = today.replace(day=1)
    expenses = list(expenses_collection.find({"email": email}))
    month_total = 0
    for exp in expenses:
        amount = int(exp['amount'])
        exp_date = datetime.strptime(exp['date'], "%Y-%m-%d").date()
        if exp_date >= month_start:
            month_total += amount
            
    # Fetch last 5 expenses for the activity timeline
    recent_expenses = list(expenses_collection.find({"email": email}).sort("_id", -1).limit(5))
    category_icons = {
        'Food': '🍔',
        'Transport': '🚗',
        'Electronics': '💻',
        'Clothing': '👕',
        'Entertainment': '🎬',
        'Utilities': '💡',
        'Other': '📦'
    }
    for exp in recent_expenses:
        exp['icon'] = category_icons.get(exp.get('category', 'Other'), '📦')
        
    return render_template(
        'user_dashboard.html',
        name=name,
        email=email,
        budget=budget,
        month_total=month_total,
        recent_expenses=recent_expenses,
        phone=user.get('phone', ''),
        address=user.get('address', ''),
        profile_image=user.get('profile_image', '')
    )


@app.route('/api/ai-insights')
def ai_insights():
    if 'user' not in session:
        return {"error": "Unauthorized"}, 401
        
    email = session['user']
    
    # 1. Fetch budget & goals
    user = users_collection.find_one({"email": email})
    username = user.get('name') if user else 'User'
    budget = user.get('budget', 0) if user else 0
    goals = list(goals_collection.find({"email": email}))
    
    # 2. Fetch current month's expenses for stats
    today = datetime.today().date()
    month_start = today.replace(day=1)
    expenses = list(expenses_collection.find({"email": email}))
    
    month_total = 0
    category_totals = defaultdict(int)
    total_count = len(expenses)
    
    for exp in expenses:
        try:
            amount = int(exp['amount'])
            exp_date = datetime.strptime(exp['date'], "%Y-%m-%d").date()
            if exp_date >= month_start:
                month_total += amount
                category = exp.get('category', 'Other')
                category_totals[category] += amount
        except (ValueError, TypeError, KeyError):
            pass
            
    # 3. Create cache fingerprint
    # Fingerprint includes count of total expenses + sum of all expenses + user's current budget
    total_spending_sum = 0
    for e in expenses:
        try:
            total_spending_sum += int(e['amount'])
        except (ValueError, TypeError):
            pass
    fingerprint = f"{total_count}_{total_spending_sum}_{budget}"
    
    # Check session cache
    cached_fingerprint = session.get('ai_insight_fingerprint')
    cached_insight = session.get('ai_insight')
    
    # Check force refresh flag
    force_refresh = request.args.get('refresh') == 'true'
    
    # If fingerprint matches and we have cache, return it (unless force refresh is True)
    if not force_refresh and cached_fingerprint == fingerprint and cached_insight:
        return {"insights": cached_insight, "cached": True}
        
    # Check if API key exists
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {"error": "API Key is missing", "key_missing": True}, 200
        
    # Build prompt
    category_str = ", ".join([f"{cat}: ₹{amt}" for cat, amt in category_totals.items()])
    goals_str = ", ".join([f"{g['name']} (Target: ₹{g['target']})" for g in goals])
    
    prompt = (
        f"You are an expert personal finance coach. Analyze the user's spending patterns and give them exactly 3 highly specific, "
        f"actionable, and encouraging insights or savings tips that cover their overall financial status. Maintain a helpful and motivational tone.\n\n"
        f"User Name: {username}\n"
        f"Monthly Budget Limit: ₹{budget if budget > 0 else 'Not Set'}\n"
        f"Total spent this month (since {month_start}): ₹{month_total}\n"
        f"Spending category breakdown this month: {category_str if category_str else 'No spending recorded yet'}\n"
        f"Active savings goals: {goals_str if goals_str else 'No active savings goals set'}\n\n"
        f"Instructions:\n"
        f"1. Do NOT write any greeting, introductory paragraph, review paragraph, or summary. Get straight to the 3 points.\n"
        f"2. Format these 3 insights using HTML list items (<li>) with relevant emojis (e.g., 💡, 📈, 🛍️) and wrap them inside <ul>. Use bold tags <strong> for key details.\n"
        f"3. CRITICAL: Keep each of the 3 points extremely brief, direct, and short (exactly 1 or 2 lines maximum per point). Keep each tip to a single short sentence that summarizes a key area (e.g., overall spending health, category review, and goal progress).\n"
        f"4. Keep the response concise, motivational, and easy to read. Do NOT wrap the code in ```html or other markdown wrappers, just return the raw HTML string."
    )
    
    # Call Gemini API via urllib
    import urllib.request
    import urllib.error
    import json
    
    url = "https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent"
    headers = {
        'Content-Type': 'application/json',
        'x-goog-api-key': api_key
    }
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode('utf-8'),
            headers=headers,
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=12) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            ai_text = res_data['candidates'][0]['content']['parts'][0]['text']
            
            # Clean up the output if AI wrapped it in markdown code blocks
            ai_text = ai_text.strip()
            if ai_text.startswith("```html"):
                ai_text = ai_text[7:]
            elif ai_text.startswith("```"):
                ai_text = ai_text[3:]
            if ai_text.endswith("```"):
                ai_text = ai_text[:-3]
            ai_text = ai_text.strip()
            
            # Cache in session
            session['ai_insight'] = ai_text
            session['ai_insight_fingerprint'] = fingerprint
            
            return {"insights": ai_text, "cached": False}
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        print(f"Gemini API HTTPError: {error_body}")
        try:
            err_json = json.loads(error_body)
            error_message = err_json['error']['message']
        except Exception:
            error_message = error_body
        return {"error": f"API Error: {error_message}", "key_missing": False}, 200
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return {"error": f"Local Server Error: {str(e)}", "key_missing": False}, 200


@app.route('/edit-profile', methods=['GET', 'POST'])
def edit_profile():
    if 'user' not in session:
        return redirect('/login')
    
    email = session['user']
    user = users_collection.find_one({"email": email})
    
    if request.method == 'POST':
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        new_email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()
        
        if not first_name or not last_name or not new_email:
            flash("First Name, Last Name, and Email are required.", "error")
            return redirect('/edit-profile')
        
        # Check email uniqueness
        if new_email != email:
            existing_user = users_collection.find_one({"email": new_email})
            if existing_user:
                flash("Email address is already in use by another account.", "error")
                return redirect('/edit-profile')
        
        # Profile image upload handling
        profile_image_path = user.get('profile_image')
        if 'profile_image' in request.files:
            file = request.files['profile_image']
            if file and file.filename != '':
                upload_folder = os.path.join(app.root_path, 'static', 'images', 'profiles')
                os.makedirs(upload_folder, exist_ok=True)
                
                _, ext = os.path.splitext(file.filename)
                filename = f"profile_{str(user['_id'])}{ext}"
                file_path = os.path.join(upload_folder, filename)
                file.save(file_path)
                
                profile_image_path = f"/static/images/profiles/{filename}"
        
        full_name = f"{first_name} {last_name}"
        
        # Cascading updates if email changed
        if new_email != email:
            expenses_collection.update_many({"email": email}, {"$set": {"email": new_email}})
            goals_collection.update_many({"email": email}, {"$set": {"email": new_email}})
            db.contact_messages.update_many({"email_user": email}, {"$set": {"email_user": new_email}})
            session['user'] = new_email
        
        # Update user doc
        users_collection.update_one(
            {"email": session['user']},
            {
                "$set": {
                    "first_name": first_name,
                    "last_name": last_name,
                    "name": full_name,
                    "email": new_email,
                    "phone": phone,
                    "address": address,
                    "profile_image": profile_image_path
                }
            }
        )
        
        session['name'] = full_name
        flash("Profile updated successfully!", "success")
        return redirect('/user-dashboard')
        
    first_name = user.get('first_name', '')
    last_name = user.get('last_name', '')
    if not first_name and not last_name:
        name_parts = user.get('name', '').split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ''
        
    return render_template(
        'edit_profile.html',
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone=user.get('phone', ''),
        address=user.get('address', ''),
        profile_image=user.get('profile_image', '')
    )




@app.route('/admin')
def admin_panel():
    if 'user' not in session or session['user'] != '24ucs046@muthayammal.in':
        flash("Access Denied: Admin access required.", "error")
        return redirect('/dashboard')
    
    # Fetch all users
    all_users = list(users_collection.find())
    
    # Stats aggregations
    total_users_count = len(all_users)
    total_expenses_count = expenses_collection.count_documents({})
    
    total_budget_sum = 0
    total_spend_all_users = 0
    global_category_totals = defaultdict(int)
    
    # Pre-fetch all expenses to optimize calculations
    all_expenses = list(expenses_collection.find())
    
    # Map expenses by user email
    user_expenses_map = defaultdict(list)
    for exp in all_expenses:
        user_expenses_map[exp.get('email')].append(exp)
        
        # Accumulate global category totals
        cat = exp.get('category', 'Other')
        try:
            global_category_totals[cat] += int(exp.get('amount', 0))
        except (ValueError, TypeError):
            pass
    
    user_details = []
    for u in all_users:
        u_email = u.get('email')
        u_name = u.get('name', 'N/A')
        u_budget = u.get('budget', 0)
        
        # Calculate budget sum
        try:
            total_budget_sum += int(u_budget)
        except (ValueError, TypeError):
            pass
            
        # User expenses
        user_expenses = user_expenses_map[u_email]
        exp_count = len(user_expenses)
        
        u_spend = 0
        for exp in user_expenses:
            try:
                u_spend += int(exp.get('amount', 0))
            except (ValueError, TypeError):
                pass
        
        total_spend_all_users += u_spend
        
        user_details.append({
            "id": str(u.get('_id')),
            "name": u_name,
            "email": u_email,
            "phone": u.get('phone', ''),
            "address": u.get('address', ''),
            "budget": u_budget,
            "exp_count": exp_count,
            "total_spend": u_spend,
            "profile_image": u.get('profile_image', '')
        })
        
    # Get contact messages
    contact_messages = list(db.contact_messages.find().sort("_id", -1))
    contact_count = sum(1 for msg in contact_messages if not msg.get('resolved', False))
    
    avg_expense = round(total_spend_all_users / total_expenses_count) if total_expenses_count > 0 else 0
    
    # Calculate top spending users (top 5) for charts
    top_spending_users = sorted(user_details, key=lambda x: x['total_spend'], reverse=True)[:5]
    top_users_labels = [u['name'] for u in top_spending_users if u['total_spend'] > 0]
    top_users_values = [u['total_spend'] for u in top_spending_users if u['total_spend'] > 0]
    
    # Format global category totals for charts
    global_labels = list(global_category_totals.keys())
    global_values = list(global_category_totals.values())
    
    return render_template(
        'admin.html',
        users=user_details,
        total_users=total_users_count,
        total_expenses=total_expenses_count,
        total_budget=total_budget_sum,
        total_spend=total_spend_all_users,
        avg_expense=avg_expense,
        contact_messages=contact_messages,
        contact_count=contact_count,
        top_users_labels=top_users_labels,
        top_users_values=top_users_values,
        global_labels=global_labels,
        global_values=global_values
    )

@app.route('/admin/user-expenses/<email>')
def admin_user_expenses(email):
    if 'user' not in session or session['user'] != '24ucs046@muthayammal.in':
        return {"error": "Access Denied"}, 403
        
    expenses = list(expenses_collection.find({"email": email}).sort("_id", -1))
    # Convert ObjectIds to strings
    for exp in expenses:
        exp['_id'] = str(exp['_id'])
        
    return {"expenses": expenses}

@app.route('/admin/update-user/<id>', methods=['POST'])
def admin_update_user(id):
    if 'user' not in session or session['user'] != '24ucs046@muthayammal.in':
        flash("Access Denied: Admin access required.", "error")
        return redirect('/dashboard')
        
    name = request.form.get('name', '').strip()
    phone = request.form.get('phone', '').strip()
    address = request.form.get('address', '').strip()
    try:
        budget = int(request.form.get('budget', 0))
    except ValueError:
        budget = 0
        
    if not name:
        flash("User name cannot be empty", "error")
        return redirect('/admin')
        
    users_collection.update_one(
        {"_id": ObjectId(id)},
        {"$set": {
            "name": name,
            "phone": phone,
            "address": address,
            "budget": budget
        }}
    )
    flash("User details updated successfully!", "success")
    return redirect('/admin')

@app.route('/admin/delete-user/<id>')
def admin_delete_user(id):
    if 'user' not in session or session['user'] != '24ucs046@muthayammal.in':
        flash("Access Denied: Admin access required.", "error")
        return redirect('/dashboard')
        
    user = users_collection.find_one({"_id": ObjectId(id)})
    if not user:
        flash("User not found", "error")
        return redirect('/admin')
        
    email = user.get('email')
    
    # Don't delete the admin themselves from admin panel by mistake
    if email == '24ucs046@muthayammal.in':
        flash("Cannot delete the main admin account!", "error")
        return redirect('/admin')
        
    # Perform cascading deletes
    users_collection.delete_one({"_id": ObjectId(id)})
    expenses_collection.delete_many({"email": email})
    goals_collection.delete_many({"email": email})
    reset_tokens_collection.delete_many({"email": email})
    db.contact_messages.delete_many({"email_user": email})
    
    flash(f"User {email} and all associated data deleted successfully.", "success")
    return redirect('/admin')

@app.route('/admin/delete-message/<id>')
def admin_delete_message(id):
    if 'user' not in session or session['user'] != '24ucs046@muthayammal.in':
        flash("Access Denied: Admin access required.", "error")
        return redirect('/dashboard')
        
    db.contact_messages.delete_one({"_id": ObjectId(id)})
    flash("Message deleted successfully.", "success")
    return redirect('/admin')


@app.route('/admin/toggle-resolved/<id>', methods=['POST'])
def admin_toggle_resolved(id):
    if 'user' not in session or session['user'] != '24ucs046@muthayammal.in':
        return {"error": "Access Denied"}, 403
        
    data = request.get_json() or {}
    resolved = data.get('resolved', False)
    
    db.contact_messages.update_one(
        {"_id": ObjectId(id)},
        {"$set": {"resolved": resolved}}
    )
    return {"success": True, "resolved": resolved}





if __name__ == '__main__':
    app.run(debug=True)


