import os
import json
import logging
from openai import OpenAI

# Get API key from environment variable
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai = OpenAI(api_key=OPENAI_API_KEY)

def analyze_portfolio(portfolio_text):
    """
    Analyze the investment portfolio using OpenAI's GPT-3.5
    
    Args:
        portfolio_text (str): Plain text describing the user's investments
        
    Returns:
        dict: Analysis results including allocation, top performers, risk level, and suggestions
    """
    try:
        # Craft a detailed prompt for the LLM
        prompt = f"""
        You are an investment analysis expert. Analyze the following investment portfolio and provide detailed insights.
        
        Portfolio: {portfolio_text}
        
        Provide the following analysis in JSON format:
        1. allocation_breakdown: A breakdown of the portfolio allocation by asset type (stocks, bonds, crypto, etc.). 
           Format as an array of objects with 'category' and 'percentage' fields.
        2. top_performers: List of top 3 gainers with their names and percentages.
        3. bottom_performers: List of top 3 losers with their names and percentages.
        4. risk_level: Overall risk assessment of the portfolio (Low, Medium, or High) with a brief explanation.
        5. suggestions: List of 3-5 specific, actionable suggestions to improve the portfolio.
        
        Response must be valid JSON with these exact keys. Make reasonable assumptions if specific information is missing.
        """
        
        logging.debug("Sending portfolio to OpenAI for analysis")
        
        # Make request to OpenAI
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an investment analysis expert that provides insights in JSON format."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.5,
            max_tokens=1000
        )
        
        # Parse the response
        analysis_json = json.loads(response.choices[0].message.content)
        logging.debug("Received analysis from OpenAI")
        
        return analysis_json
        
    except Exception as e:
        logging.error(f"OpenAI API error: {str(e)}")
        raise Exception(f"Failed to analyze portfolio: {str(e)}")
