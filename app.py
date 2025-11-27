"""
BOT HOSTING PANEL - Backend Server
Earn money by hosting user bots 24/7
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import subprocess
import json
import uuid
from datetime import datetime, timedelta
import threading
import time
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Ensure Flask uses the templates folder next to this file (helps in deployments)
app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, 'templates'),
    static_folder=os.path.join(BASE_DIR, 'static')
)
app.config['SECRET_KEY'] = 'your-secret-key-change-this'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hosting_panel.db'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max upload
app.config['UPLOAD_FOLDER'] = 'user_bots'

db = SQLAlchemy(app)

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ═══════════════════════════════════════════════════════════════════════
# DATABASE MODELS
# ═══════════════════════════════════════════════════════════════════════

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    balance = db.Column(db.Float, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    bots = db.relationship('HostedBot', backref='owner', lazy=True)
    payments = db.relationship('Payment', backref='user', lazy=True)

class HostedBot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bot_id = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    bot_name = db.Column(db.String(100), nullable=False)
    main_file = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(20), default='stopped')  # running, stopped, error
    process_id = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)
    upload_path = db.Column(db.String(200), nullable=False)
    logs = db.relationship('BotLog', backref='bot', lazy=True, cascade='all, delete-orphan')

class BotLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bot_id = db.Column(db.Integer, db.ForeignKey('hosted_bot.id'), nullable=False)
    message = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    plan = db.Column(db.String(50), nullable=False)  # 1month, 3month, etc
    transaction_id = db.Column(db.String(100), unique=True)
    status = db.Column(db.String(20), default='pending')  # pending, completed, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ═══════════════════════════════════════════════════════════════════════
# AUTHENTICATION ROUTES
# ═══════════════════════════════════════════════════════════════════════

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already exists'}), 400
        
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already exists'}), 400
        
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        
        return jsonify({'message': 'Registration successful'}), 201
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            return jsonify({'message': 'Login successful'}), 200
        
        return jsonify({'error': 'Invalid credentials'}), 401
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# ═══════════════════════════════════════════════════════════════════════
# DASHBOARD
# ═══════════════════════════════════════════════════════════════════════

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    bots = HostedBot.query.filter_by(user_id=user.id).all()
    
    return render_template('dashboard.html', user=user, bots=bots)

# ═══════════════════════════════════════════════════════════════════════
# BOT MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════

@app.route('/api/upload-bot', methods=['POST'])
def upload_bot():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    bot_name = request.form.get('bot_name', 'MyBot')
    main_file = request.form.get('main_file', 'app.py')
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    user_id = session['user_id']
    bot_id = str(uuid.uuid4())
    bot_folder = os.path.join(app.config['UPLOAD_FOLDER'], bot_id)
    
    os.makedirs(bot_folder, exist_ok=True)
    
    # If ZIP, extract it
    if file.filename.endswith('.zip'):
        zip_path = os.path.join(bot_folder, 'upload.zip')
        file.save(zip_path)
        shutil.unpack_archive(zip_path, bot_folder)
        os.remove(zip_path)
    else:
        file.save(os.path.join(bot_folder, file.filename))
    
    bot = HostedBot(
        bot_id=bot_id,
        user_id=user_id,
        bot_name=bot_name,
        main_file=main_file,
        upload_path=bot_folder
    )
    db.session.add(bot)
    db.session.commit()
    
    return jsonify({'message': 'Bot uploaded', 'bot_id': bot_id}), 201

@app.route('/api/bot/<bot_id>/start', methods=['POST'])
def start_bot(bot_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    bot = HostedBot.query.filter_by(bot_id=bot_id).first()
    
    if not bot or bot.user_id != session['user_id']:
        return jsonify({'error': 'Bot not found'}), 404
    
    # Check if expired
    if bot.expires_at and datetime.utcnow() > bot.expires_at:
        return jsonify({'error': 'Bot hosting expired'}), 403
    
    bot_folder = bot.upload_path
    main_file_path = os.path.join(bot_folder, bot.main_file)
    
    if not os.path.exists(main_file_path):
        return jsonify({'error': f'{bot.main_file} not found'}), 400
    
    try:
        # Start bot in background
        process = subprocess.Popen(
            ['python', bot.main_file],
            cwd=bot_folder,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True
        )
        
        bot.process_id = process.pid
        bot.status = 'running'
        db.session.commit()
        
        log = BotLog(bot_id=bot.id, message=f'✅ Bot started (PID: {process.pid})')
        db.session.add(log)
        db.session.commit()
        
        return jsonify({'message': 'Bot started', 'pid': process.pid}), 200
    
    except Exception as e:
        bot.status = 'error'
        db.session.commit()
        return jsonify({'error': str(e)}), 500

@app.route('/api/bot/<bot_id>/stop', methods=['POST'])
def stop_bot(bot_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    bot = HostedBot.query.filter_by(bot_id=bot_id).first()
    
    if not bot or bot.user_id != session['user_id']:
        return jsonify({'error': 'Bot not found'}), 404
    
    try:
        if bot.process_id:
            os.kill(bot.process_id, 15)  # SIGTERM
        
        bot.status = 'stopped'
        bot.process_id = None
        db.session.commit()
        
        log = BotLog(bot_id=bot.id, message='⛔ Bot stopped')
        db.session.add(log)
        db.session.commit()
        
        return jsonify({'message': 'Bot stopped'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/bot/<bot_id>/status', methods=['GET'])
def get_bot_status(bot_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    bot = HostedBot.query.filter_by(bot_id=bot_id).first()
    
    if not bot or bot.user_id != session['user_id']:
        return jsonify({'error': 'Bot not found'}), 404
    
    # Check if process still running
    if bot.process_id:
        try:
            os.kill(bot.process_id, 0)  # Check if exists
        except:
            bot.status = 'stopped'
            bot.process_id = None
            db.session.commit()
    
    return jsonify({
        'bot_id': bot.bot_id,
        'name': bot.bot_name,
        'status': bot.status,
        'pid': bot.process_id,
        'created_at': bot.created_at.isoformat(),
        'expires_at': bot.expires_at.isoformat() if bot.expires_at else None
    }), 200

@app.route('/api/bot/<bot_id>/logs', methods=['GET'])
def get_bot_logs(bot_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    bot = HostedBot.query.filter_by(bot_id=bot_id).first()
    
    if not bot or bot.user_id != session['user_id']:
        return jsonify({'error': 'Bot not found'}), 404
    
    logs = BotLog.query.filter_by(bot_id=bot.id).order_by(BotLog.timestamp.desc()).limit(50).all()
    
    return jsonify({
        'logs': [{'timestamp': log.timestamp.isoformat(), 'message': log.message} for log in logs]
    }), 200

# ═══════════════════════════════════════════════════════════════════════
# PAYMENT PLANS
# ═══════════════════════════════════════════════════════════════════════

PLANS = {
    '1month': {'price': 100, 'duration': 30, 'name': '1 Month'},
    '3month': {'price': 250, 'duration': 90, 'name': '3 Months'},
    '6month': {'price': 450, 'duration': 180, 'name': '6 Months'},
    '1year': {'price': 800, 'duration': 365, 'name': '1 Year'},
}

@app.route('/api/purchase/<plan_id>', methods=['POST'])
def purchase_plan(plan_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    if plan_id not in PLANS:
        return jsonify({'error': 'Invalid plan'}), 400
    
    bot_id = request.json.get('bot_id')
    bot = HostedBot.query.filter_by(bot_id=bot_id).first()
    
    if not bot or bot.user_id != session['user_id']:
        return jsonify({'error': 'Bot not found'}), 404
    
    plan = PLANS[plan_id]
    price = plan['price']
    
    # TODO: Integrate with Stripe/PayPal here
    # For now, just simulate payment
    
    # Update bot expiry
    bot.expires_at = datetime.utcnow() + timedelta(days=plan['duration'])
    
    # Create payment record
    payment = Payment(
        user_id=session['user_id'],
        amount=price,
        plan=plan_id,
        status='completed',
        transaction_id=str(uuid.uuid4())
    )
    
    db.session.add(payment)
    db.session.commit()
    
    return jsonify({
        'message': f'Purchase successful! Bot active until {bot.expires_at}',
        'expires_at': bot.expires_at.isoformat()
    }), 200

# ═══════════════════════════════════════════════════════════════════════
# PRICING PAGE
# ═══════════════════════════════════════════════════════════════════════

@app.route('/pricing')
def pricing():
    return render_template('pricing.html', plans=PLANS)

# ═══════════════════════════════════════════════════════════════════════
# INITIALIZATION
# ═══════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=False, host='0.0.0.0', port=5000)
