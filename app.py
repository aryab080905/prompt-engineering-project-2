import os
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for
from utils.openai_helper import analyze_portfolio
from flask_sqlalchemy import SQLAlchemy

# Define db here instead of importing from models
db = SQLAlchemy()

# Import Investment model after db is defined
class Investment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    investment_type = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    interest_rate = db.Column(db.Float)
    expected_return = db.Column(db.Float)
    years = db.Column(db.Integer)
    start_date = db.Column(db.Date, default=datetime.now().date())
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    def to_dict(self):
        return {
            'id': self.id,
            'investment_type': self.investment_type,
            'amount': self.amount,
            'interest_rate': self.interest_rate,
            'expected_return': self.expected_return,
            'years': self.years,
            'start_date': self.start_date.strftime('%Y-%m-%d') if self.start_date else None,
            'description': self.description,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the database
db.init_app(app)

# Create tables if they don't exist
with app.app_context():
    db.create_all()

# Investment types with descriptions
INVESTMENT_TYPES = {
    "stocks": "Individual company stocks or shares",
    "bonds": "Government or corporate bonds",
    "mutual_funds": "Professionally managed investment funds",
    "etfs": "Exchange-Traded Funds",
    "real_estate": "Property investments",
    "commodities": "Gold, silver, oil and other physical goods",
    "cryptocurrencies": "Bitcoin, Ethereum and other digital currencies",
    "cds": "Certificates of Deposit",
    "options": "Contracts for future potential transactions",
    "futures": "Agreements to buy/sell assets at predetermined prices",
    "annuities": "Insurance products that provide income streams",
    "savings": "Savings accounts with financial institutions",
    "fixed_deposits": "Fixed term deposits with guaranteed interest",
    "rds": "Recurring Deposits with regular contributions",
    "p2p": "Peer-to-Peer Lending investments",
    "hedge_funds": "Alternative investments for high net worth individuals",
    "private_equity": "Investments in private companies",
    "provident_fund": "Retirement savings with tax benefits",
    "sips": "Systematic Investment Plans"
}

# Map investment types to font awesome icons
def get_icon_for_investment(investment_type):
    icons = {
        "stocks": "fa-chart-line",
        "bonds": "fa-file-contract",
        "mutual_funds": "fa-money-bill-trend-up",
        "etfs": "fa-chart-pie",
        "real_estate": "fa-house-chimney",
        "commodities": "fa-coins",
        "cryptocurrencies": "fa-bitcoin",
        "cds": "fa-piggy-bank",
        "options": "fa-chart-simple",
        "futures": "fa-forward",
        "annuities": "fa-hand-holding-dollar",
        "savings": "fa-vault",
        "fixed_deposits": "fa-money-bill-wave",
        "rds": "fa-money-bill-transfer",
        "p2p": "fa-handshake",
        "hedge_funds": "fa-shield-alt",
        "private_equity": "fa-building",
        "provident_fund": "fa-umbrella",
        "sips": "fa-calendar-check"
    }
    return icons.get(investment_type, "fa-dollar-sign")

@app.route('/')
def index():
    """Render the main page of the application"""
    return render_template('index.html')

@app.route('/investments')
def investments():
    """Display investment types page"""
    return render_template('investments.html', investment_types=INVESTMENT_TYPES, get_icon_for_investment=get_icon_for_investment)

@app.route('/investment/<investment_type>')
def investment_options(investment_type):
    """Show options for existing or new investment"""
    if investment_type not in INVESTMENT_TYPES:
        return redirect(url_for('investments'))
    
    return render_template('investment_options.html', 
                          investment_type=investment_type,
                          investment_name=INVESTMENT_TYPES[investment_type])

# This route has been deprecated as it was causing errors
# @app.route('/analyze', methods=['POST'])
# def analyze():
#     """Process the portfolio data and return analysis"""
#     try:
#         # Get portfolio text from request
#         portfolio_data = request.form.get('portfolio_data')
#         
#         if not portfolio_data:
#             return jsonify({
#                 'error': 'No portfolio data provided'
#             }), 400
#             
#         # Analyze portfolio using OpenAI
#         analysis_result = analyze_portfolio(portfolio_data)
#         
#         return jsonify(analysis_result)
#     
#     except Exception as e:
#         logging.error(f"Error analyzing portfolio: {str(e)}")
#         return jsonify({
#             'error': f"An error occurred: {str(e)}"
#         }), 500

@app.route('/existing_investments/<investment_type>')
def existing_investments(investment_type):
    """Show existing investments of a specific type"""
    if investment_type not in INVESTMENT_TYPES:
        return redirect(url_for('investments'))
    
    investments = Investment.query.filter_by(investment_type=investment_type).all()
    
    return render_template('existing_investments.html',
                          investment_type=investment_type,
                          investment_name=INVESTMENT_TYPES[investment_type],
                          investments=investments)

@app.route('/new_investment/<investment_type>', methods=['GET', 'POST'])
def new_investment(investment_type):
    """Handle new investment creation"""
    if investment_type not in INVESTMENT_TYPES:
        return redirect(url_for('investments'))
    
    if request.method == 'POST':
        try:
            # Get form data
            amount = float(request.form.get('amount', 0))
            interest_rate = float(request.form.get('interest_rate', 0))
            expected_return = float(request.form.get('expected_return', 0)) if request.form.get('expected_return') else None
            years = int(request.form.get('years', 0))
            start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date()
            description = request.form.get('description', '')
            
            # Create new investment
            investment = Investment(
                investment_type=investment_type,
                amount=amount,
                interest_rate=interest_rate,
                expected_return=expected_return,
                years=years,
                start_date=start_date,
                description=description
            )
            
            # Save to database
            db.session.add(investment)
            db.session.commit()
            
            return redirect(url_for('investment_details', investment_id=investment.id))
            
        except Exception as e:
            logging.error(f"Error creating investment: {str(e)}")
            return render_template('new_investment.html',
                                  investment_type=investment_type,
                                  investment_name=INVESTMENT_TYPES[investment_type],
                                  today_date=datetime.now().strftime('%Y-%m-%d'),
                                  error=str(e))
    
    # GET request
    return render_template('new_investment.html',
                          investment_type=investment_type,
                          investment_name=INVESTMENT_TYPES[investment_type],
                          today_date=datetime.now().strftime('%Y-%m-%d'))

@app.route('/investment_details/<int:investment_id>')
def investment_details(investment_id):
    """Show details for a specific investment"""
    investment = Investment.query.get_or_404(investment_id)
    
    # Calculate future value using compound interest formula
    # FV = P(1 + r)^t
    future_value = investment.amount * (1 + (investment.interest_rate / 100)) ** investment.years
    
    # Calculate year-by-year growth for the chart
    years_data = []
    for year in range(investment.years + 1):
        value = investment.amount * (1 + (investment.interest_rate / 100)) ** year
        years_data.append({
            'year': year,
            'value': round(value, 2)
        })
    
    return render_template('investment_details.html',
                          investment=investment,
                          investment_name=INVESTMENT_TYPES[investment.investment_type],
                          future_value=round(future_value, 2),
                          growth_percentage=round(((future_value - investment.amount) / investment.amount) * 100, 2),
                          years_data=years_data)
