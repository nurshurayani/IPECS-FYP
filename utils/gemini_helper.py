import os
import streamlit as st
import google.generativeai as genai
import json

def summarise_spending(transactions):
    summary = {}
    for tx in transactions:
        cat = tx["category"]
        summary[cat] = summary.get(cat, 0.0) + float(tx["amount"])
    return summary

def generate_forecast(transactions: list, budgets: dict) -> dict:
    # Try and read key from st.secrets or environmental variable
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        try:
            api_key = st.secrets["GEMINI_API_KEY"]
        except Exception:
            pass
            
    if not api_key:
        return {
            "projected_total": 650.00,
            "by_category": {cat: val * 0.95 for cat, val in budgets.items()},
            "confidence": "Medium",
            "tip": "Mamak sessions cost RM15! Set limit to maximum twice a week, buddy. Add GEMINI_API_KEY secret for active forecasts."
        }
        
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash") # Fallback to stable for general python compatibility
    
    # Summarise last 90 days spending per category
    summary = summarise_spending(transactions)
    
    prompt = f"""
    You are a personal finance assistant for a Malaysian university student.
    Based on the spending data below, forecast total spending for the next 30 days
    and per-category projections. Return a raw JSON block only:
    {{"projected_total": float, "by_category": {{"category": float}}, "confidence": "High/Medium/Low", "tip": "one short saving tip in Malaysian slang English"}}
    
    Spending last 90 days by category (RM):
    {summary}
    
    Monthly budgets set:
    {budgets}
    """
    
    try:
      response = model.generate_content(prompt)
      txt = response.text.replace("```json", "").replace("```", "").strip()
      return json.loads(txt)
    except Exception as e:
      return {
          "projected_total": 595.0,
          "by_category": {cat: val * 0.9 for cat, val in budgets.items()},
          "confidence": "Low",
          "tip": f"Error loading AI predictions. Using fallback baseline calculations. Error details: {str(e)}"
      }
