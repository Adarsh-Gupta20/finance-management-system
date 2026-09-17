import os
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json
from sqlalchemy import func
from currency_utils import get_currency_list, get_exchange_rate

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-key-for-finance-app'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'sqlite:///finance.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# Context processor for templates
@app.context_processor
def inject_current_year():
    return {'current_year': datetime.now().year}

# Define database models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    preferred_currency = db.Column(db.String(3), default='USD')
    transactions = db.relationship('Transaction', backref='user', lazy=True, cascade="all, delete-orphan")
    goals = db.relationship('Goal', backref='user', lazy=True, cascade="all, delete-orphan")
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    def __repr__(self):
        return f'<User {self.username}>'

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(10), nullable=False)  # 'income' or 'expense'
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200))
    date = db.Column(db.Date, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def __repr__(self):
        return f'<Transaction {self.id} - {self.type} - {self.amount}>'

class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    target_amount = db.Column(db.Float, nullable=False)
    current_amount = db.Column(db.Float, default=0.0)
    category = db.Column(db.String(50), nullable=False)
    deadline = db.Column(db.Date, nullable=True)
    description = db.Column(db.String(200))
    is_completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.Date, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def progress_percentage(self):
        if self.target_amount == 0:
            return 100
        return min(int((self.current_amount / self.target_amount) * 100), 100)
    
    def __repr__(self):
        return f'<Goal {self.id} - {self.name} - {self.progress_percentage()}%>'

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        currency = request.form.get('currency')
        
        # Check if username or email already exists
        user_exists = User.query.filter((User.username == username) | (User.email == email)).first()
        if user_exists:
            flash('Username or email already exists', 'danger')
            return redirect(url_for('register'))
            
        # Validate password strength
        if len(password) < 8:
            flash('Password must be at least 8 characters long', 'danger')
            return redirect(url_for('register'))
        
        if not any(c.isupper() for c in password):
            flash('Password must contain at least one uppercase letter', 'danger')
            return redirect(url_for('register'))
            
        if not any(c.islower() for c in password):
            flash('Password must contain at least one lowercase letter', 'danger')
            return redirect(url_for('register'))
            
        if not any(c.isdigit() for c in password):
            flash('Password must contain at least one number', 'danger')
            return redirect(url_for('register'))
            
        if not any(c in '!@#$%^&*(),.?":{}|<>' for c in password):
            flash('Password must contain at least one special character', 'danger')
            return redirect(url_for('register'))
            
        # Create new user
        new_user = User(username=username, email=email, preferred_currency=currency)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful. Please login.', 'success')
        return redirect(url_for('login'))
        
    currencies = get_currency_list()
    return render_template('register.html', currencies=currencies)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            # In a real app, you would use Flask-Login here
            # For simplicity, we'll use session
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
            
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    # Check if user is logged in
    if 'user_id' not in session:
        flash('Please login first', 'danger')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    user = User.query.get_or_404(user_id)
    
    # Get transactions
    transactions = Transaction.query.filter_by(user_id=user_id).order_by(Transaction.date.desc()).limit(5).all()
    
    # Calculate totals
    income = db.session.query(func.sum(Transaction.amount)).filter_by(
        user_id=user_id, type='income').scalar() or 0
    expenses = db.session.query(func.sum(Transaction.amount)).filter_by(
        user_id=user_id, type='expense').scalar() or 0
    
    # Get expense by category
    expenses_by_category = db.session.query(
        Transaction.category, func.sum(Transaction.amount)
    ).filter_by(
        user_id=user_id, type='expense'
    ).group_by(
        Transaction.category
    ).all()
    
    # Format for pie chart
    categories = [cat for cat, _ in expenses_by_category]
    amounts = [float(amt) for _, amt in expenses_by_category]
    
    return render_template(
        'dashboard.html',
        user=user,
        transactions=transactions,
        income=income,
        expenses=expenses,
        balance=income-expenses,
        categories=json.dumps(categories),
        amounts=json.dumps(amounts)
    )

@app.route('/transactions')
def transactions():
    if 'user_id' not in session:
        flash('Please login first', 'danger')
        return redirect(url_for('login'))
        
    user_id = session['user_id']
    user = User.query.get_or_404(user_id)
    
    # Get filter parameters
    transaction_type = request.args.get('type')
    category = request.args.get('category')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Base query
    query = Transaction.query.filter_by(user_id=user_id)
    
    # Apply filters if provided
    if transaction_type and transaction_type != 'all':
        query = query.filter_by(type=transaction_type)
        
    if category and category != 'all':
        query = query.filter_by(category=category)
        
    if start_date:
        start = datetime.strptime(start_date, '%Y-%m-%d').date()
        query = query.filter(Transaction.date >= start)
        
    if end_date:
        end = datetime.strptime(end_date, '%Y-%m-%d').date()
        query = query.filter(Transaction.date <= end)
    
    # Get all transactions with applied filters
    transactions = query.order_by(Transaction.date.desc()).all()
    
    # Get unique categories for filter dropdown
    categories = db.session.query(Transaction.category).filter_by(user_id=user_id).distinct().all()
    categories = [cat[0] for cat in categories]
    
    return render_template(
        'transactions.html', 
        user=user, 
        transactions=transactions,
        categories=categories,
        selected_type=transaction_type,
        selected_category=category,
        start_date=start_date,
        end_date=end_date
    )

@app.route('/delete_transaction/<int:transaction_id>')
def delete_transaction(transaction_id):
    if 'user_id' not in session:
        flash('Please login first', 'danger')
        return redirect(url_for('login'))
        
    user_id = session['user_id']
    
    # Get the transaction
    transaction = Transaction.query.get_or_404(transaction_id)
    
    # Check if the transaction belongs to the user
    if transaction.user_id != user_id:
        flash('Access denied', 'danger')
        return redirect(url_for('transactions'))
    
    # Delete the transaction
    db.session.delete(transaction)
    db.session.commit()
    
    flash('Transaction deleted successfully', 'success')
    return redirect(url_for('transactions'))

@app.route('/add_transaction', methods=['GET', 'POST'])
def add_transaction():
    if 'user_id' not in session:
        flash('Please login first', 'danger')
        return redirect(url_for('login'))
        
    user_id = session['user_id']
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        transaction_type = request.form.get('type')
        amount = float(request.form.get('amount'))
        category = request.form.get('category')
        description = request.form.get('description')
        date_str = request.form.get('date')
        
        # Parse date
        date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else datetime.utcnow().date()
        
        # Create transaction
        transaction = Transaction(
            amount=amount,
            type=transaction_type,
            category=category,
            description=description,
            date=date,
            user_id=user_id
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        flash('Transaction added successfully', 'success')
        return redirect(url_for('dashboard'))
    
    today = datetime.now().strftime('%Y-%m-%d')
    return render_template('add_transaction.html', user=user, today=today)

@app.route('/change_currency', methods=['GET', 'POST'])
def change_currency():
    if 'user_id' not in session:
        flash('Please login first', 'danger')
        return redirect(url_for('login'))
        
    user_id = session['user_id']
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        new_currency = request.form.get('currency')
        old_currency = user.preferred_currency
        
        if new_currency != old_currency:
            # Get exchange rate
            exchange_rate = get_exchange_rate(old_currency, new_currency)
            
            # Update all transactions
            transactions = Transaction.query.filter_by(user_id=user_id).all()
            for transaction in transactions:
                transaction.amount = round(transaction.amount * exchange_rate, 2)
                
            # Update user's preferred currency
            user.preferred_currency = new_currency
            db.session.commit()
            
            flash(f'Currency changed to {new_currency}', 'success')
        else:
            flash('No currency change needed', 'info')
            
        return redirect(url_for('dashboard'))
        
    currencies = get_currency_list()
    return render_template('change_currency.html', user=user, currencies=currencies)

@app.route('/reports')
def reports():
    if 'user_id' not in session:
        flash('Please login first', 'danger')
        return redirect(url_for('login'))
        
    user_id = session['user_id']
    user = User.query.get_or_404(user_id)
    
    # Get current year and month
    year = int(request.args.get('year', datetime.utcnow().year))
    month = int(request.args.get('month', datetime.utcnow().month))
    
    # Get monthly data
    start_date = datetime(year, month, 1).date()
    if month == 12:
        end_date = datetime(year + 1, 1, 1).date()
    else:
        end_date = datetime(year, month + 1, 1).date()
        
    monthly_income = db.session.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == user_id,
        Transaction.type == 'income',
        Transaction.date >= start_date,
        Transaction.date < end_date
    ).scalar() or 0
    
    monthly_expenses = db.session.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == user_id,
        Transaction.type == 'expense',
        Transaction.date >= start_date,
        Transaction.date < end_date
    ).scalar() or 0
    
    # Get expense by category for the month
    monthly_expenses_by_category = db.session.query(
        Transaction.category, func.sum(Transaction.amount)
    ).filter(
        Transaction.user_id == user_id,
        Transaction.type == 'expense',
        Transaction.date >= start_date,
        Transaction.date < end_date
    ).group_by(
        Transaction.category
    ).all()
    
    return render_template(
        'reports.html',
        user=user,
        year=year,
        month=month,
        monthly_income=monthly_income,
        monthly_expenses=monthly_expenses,
        monthly_balance=monthly_income - monthly_expenses,
        expenses_by_category=monthly_expenses_by_category
    )

@app.route('/api/expenses_by_category')
def api_expenses_by_category():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
        
    user_id = session['user_id']
    
    # Get expense by category
    expenses_by_category = db.session.query(
        Transaction.category, func.sum(Transaction.amount)
    ).filter_by(
        user_id=user_id, type='expense'
    ).group_by(
        Transaction.category
    ).all()
    
    data = [{"category": category, "amount": float(amount)} for category, amount in expenses_by_category]
    
    return jsonify(data)

@app.route('/api/monthly_data')
def api_monthly_data():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
        
    user_id = session['user_id']
    year = int(request.args.get('year', datetime.utcnow().year))
    
    monthly_data = []
    
    for month in range(1, 13):
        start_date = datetime(year, month, 1).date()
        if month == 12:
            end_date = datetime(year + 1, 1, 1).date()
        else:
            end_date = datetime(year, month + 1, 1).date()
            
        income = db.session.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == user_id,
            Transaction.type == 'income',
            Transaction.date >= start_date,
            Transaction.date < end_date
        ).scalar() or 0
        
        expense = db.session.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == user_id,
            Transaction.type == 'expense',
            Transaction.date >= start_date,
            Transaction.date < end_date
        ).scalar() or 0
        
        monthly_data.append({
            "month": month,
            "income": float(income),
            "expense": float(expense),
            "balance": float(income - expense)
        })
    
    return jsonify(monthly_data)

# Financial Goals Routes
@app.route('/goals')
def goals():
    if 'user_id' not in session:
        flash('Please login first', 'danger')
        return redirect(url_for('login'))
        
    user_id = session['user_id']
    user = User.query.get_or_404(user_id)
    
    # Get all goals for the user
    user_goals = Goal.query.filter_by(user_id=user_id).order_by(
        Goal.is_completed.asc(), Goal.deadline.asc()).all()
    
    # Get total savings
    total_savings = sum([goal.current_amount for goal in user_goals])
    
    # Get pending and completed goals
    pending_goals = [goal for goal in user_goals if not goal.is_completed]
    completed_goals = [goal for goal in user_goals if goal.is_completed]
    
    # Add today's date for deadline comparison
    today = datetime.now().date()
    
    return render_template(
        'goals.html',
        user=user,
        goals=user_goals,
        pending_goals=pending_goals,
        completed_goals=completed_goals,
        total_savings=total_savings,
        today=today
    )

@app.route('/add_goal', methods=['GET', 'POST'])
def add_goal():
    if 'user_id' not in session:
        flash('Please login first', 'danger')
        return redirect(url_for('login'))
        
    user_id = session['user_id']
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        name = request.form.get('name')
        target_amount = float(request.form.get('target_amount'))
        current_amount = float(request.form.get('current_amount', 0))
        category = request.form.get('category')
        description = request.form.get('description', '')
        deadline_str = request.form.get('deadline', '')
        
        # Parse deadline if provided
        deadline = None
        if deadline_str:
            deadline = datetime.strptime(deadline_str, '%Y-%m-%d').date()
        
        # Create goal
        goal = Goal(
            name=name,
            target_amount=target_amount,
            current_amount=current_amount,
            category=category,
            description=description,
            deadline=deadline,
            user_id=user_id
        )
        
        db.session.add(goal)
        db.session.commit()
        
        flash('Financial goal added successfully', 'success')
        return redirect(url_for('goals'))
    
    # Common saving categories
    categories = ['Emergency Fund', 'Retirement', 'Home Purchase', 'Car Purchase', 
                  'Education', 'Vacation', 'Wedding', 'Debt Payoff', 'Other']
    
    today = datetime.now().strftime('%Y-%m-%d')
    return render_template(
        'add_goal.html', 
        user=user, 
        categories=categories,
        today=today
    )

@app.route('/edit_goal/<int:goal_id>', methods=['GET', 'POST'])
def edit_goal(goal_id):
    if 'user_id' not in session:
        flash('Please login first', 'danger')
        return redirect(url_for('login'))
        
    user_id = session['user_id']
    user = User.query.get_or_404(user_id)
    
    # Get the goal
    goal = Goal.query.get_or_404(goal_id)
    
    # Check if the goal belongs to the user
    if goal.user_id != user_id:
        flash('Access denied', 'danger')
        return redirect(url_for('goals'))
    
    if request.method == 'POST':
        goal.name = request.form.get('name')
        goal.target_amount = float(request.form.get('target_amount'))
        goal.current_amount = float(request.form.get('current_amount', 0))
        goal.category = request.form.get('category')
        goal.description = request.form.get('description', '')
        
        deadline_str = request.form.get('deadline', '')
        if deadline_str:
            goal.deadline = datetime.strptime(deadline_str, '%Y-%m-%d').date()
        else:
            goal.deadline = None
            
        # Check if goal is completed
        if goal.current_amount >= goal.target_amount:
            goal.is_completed = True
        
        db.session.commit()
        
        flash('Goal updated successfully', 'success')
        return redirect(url_for('goals'))
    
    # Common saving categories
    categories = ['Emergency Fund', 'Retirement', 'Home Purchase', 'Car Purchase', 
                  'Education', 'Vacation', 'Wedding', 'Debt Payoff', 'Other']
    
    # Format the deadline for the date input
    deadline = goal.deadline.strftime('%Y-%m-%d') if goal.deadline else ''
    
    # Get today's date for the template
    today = datetime.now().date()
    
    return render_template(
        'edit_goal.html',
        user=user,
        goal=goal,
        categories=categories,
        deadline=deadline,
        today=today
    )

@app.route('/delete_goal/<int:goal_id>')
def delete_goal(goal_id):
    if 'user_id' not in session:
        flash('Please login first', 'danger')
        return redirect(url_for('login'))
        
    user_id = session['user_id']
    
    # Get the goal
    goal = Goal.query.get_or_404(goal_id)
    
    # Check if the goal belongs to the user
    if goal.user_id != user_id:
        flash('Access denied', 'danger')
        return redirect(url_for('goals'))
    
    db.session.delete(goal)
    db.session.commit()
    
    flash('Goal deleted successfully', 'success')
    return redirect(url_for('goals'))

@app.route('/update_goal_progress/<int:goal_id>', methods=['POST'])
def update_goal_progress(goal_id):
    if 'user_id' not in session:
        flash('Please login first', 'danger')
        return redirect(url_for('login'))
        
    user_id = session['user_id']
    
    # Get the goal
    goal = Goal.query.get_or_404(goal_id)
    
    # Check if the goal belongs to the user
    if goal.user_id != user_id:
        flash('Access denied', 'danger')
        return redirect(url_for('goals'))
    
    # Update current amount
    amount = float(request.form.get('amount', 0))
    action = request.form.get('action')
    
    if action == 'add':
        goal.current_amount += amount
    elif action == 'subtract':
        goal.current_amount = max(0, goal.current_amount - amount)
    
    # Check if goal is completed
    if goal.current_amount >= goal.target_amount:
        goal.is_completed = True
    else:
        goal.is_completed = False
    
    db.session.commit()
    
    flash('Goal progress updated successfully', 'success')
    return redirect(url_for('goals'))

@app.route('/mark_goal_complete/<int:goal_id>')
def mark_goal_complete(goal_id):
    if 'user_id' not in session:
        flash('Please login first', 'danger')
        return redirect(url_for('login'))
        
    user_id = session['user_id']
    
    # Get the goal
    goal = Goal.query.get_or_404(goal_id)
    
    # Check if the goal belongs to the user
    if goal.user_id != user_id:
        flash('Access denied', 'danger')
        return redirect(url_for('goals'))
    
    # Toggle completion status
    goal.is_completed = not goal.is_completed
    
    db.session.commit()
    
    status = "completed" if goal.is_completed else "active"
    flash(f'Goal marked as {status}', 'success')
    return redirect(url_for('goals'))

@app.route('/logout')
def logout():
    # Clear session data
    session.pop('user_id', None)
    session.pop('username', None)
    flash('You have been logged out', 'success')
    return redirect(url_for('login'))

@app.route('/delete_account', methods=['GET', 'POST'])
def delete_account():
    if 'user_id' not in session:
        flash('Please login first', 'danger')
        return redirect(url_for('login'))
        
    user_id = session['user_id']
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        password = request.form.get('password')
        
        # Verify password before deletion
        if user.check_password(password):
            # Delete user account and all associated data
            db.session.delete(user)
            db.session.commit()
            
            # Clear session
            session.clear()
            
            flash('Your account and all associated data have been deleted', 'success')
            return redirect(url_for('index'))
        else:
            flash('Incorrect password. Account deletion failed.', 'danger')
            
    return render_template('delete_account.html', user=user)

# Create database tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True) 