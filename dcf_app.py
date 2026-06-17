import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="DCF Valuation", layout="wide", page_icon="◈")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #080c14; color: #e2e8f0; }
.main { background-color: #080c14; }
.block-container { padding: 2rem 3rem; max-width: 1400px; }
.dashboard-header { border-bottom: 1px solid #1e293b; padding-bottom: 1.2rem; margin-bottom: 2rem; }
.dashboard-title { font-size: 1.1rem; font-weight: 600; letter-spacing: 0.12em; text-transform: uppercase; color: #94a3b8; }
.dashboard-subtitle { font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #475569; margin-top: 0.2rem; }
.metric-card { background: #0f172a; border: 1px solid #1e293b; border-radius: 6px; padding: 1rem 1.2rem; }
.metric-label { font-size: 0.65rem; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase; color: #475569; margin-bottom: 0.3rem; }
.metric-value { font-family: 'JetBrains Mono', monospace; font-size: 1.4rem; font-weight: 500; color: #f1f5f9; }
.metric-positive { color: #22c55e; }
.metric-negative { color: #ef4444; }
.metric-delta { font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; margin-top: 0.2rem; }
.section-label { font-size: 0.65rem; font-weight: 700; letter-spacing: 0.15em; text-transform: uppercase; color: #475569; border-left: 2px solid #3b82f6; padding-left: 0.6rem; margin-bottom: 1rem; }
#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
.stTextInput input, .stNumberInput input { background-color: #0f172a !important; color: #e2e8f0 !important; border: 1px solid #1e293b !important; font-family: 'JetBrains Mono', monospace !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="dashboard-header">
    <div class="dashboard-title">◈ DCF Valuation Terminal</div>
    <div class="dashboard-subtitle">AUTOMATED DISCOUNTED CASH FLOW MODEL · ANNUAL / LTM TOGGLE</div>
</div>
""", unsafe_allow_html=True)

c_ticker, c_basis = st.columns([2, 1])
with c_ticker:
    ticker = st.text_input("Enter Ticker", value="AAPL").upper()
with c_basis:
    basis = st.radio("Data Basis", ["Annual (Last 10-K)", "LTM (Last 4 Quarters)"], horizontal=True)

if not ticker:
    st.stop()

try:
    stock = yf.Ticker(ticker)
    annual_income = stock.financials
    annual_cash = stock.cashflow
    quarterly_income = stock.quarterly_financials
    quarterly_cash = stock.quarterly_cashflow
    balance_sheet = stock.balance_sheet
    info = stock.info
    current_price = info.get('currentPrice', None)
    company_name = info.get('shortName', ticker)
except:
    st.error("Could not pull data for that ticker")
    st.stop()

sector = info.get('sector', 'Unknown')
recent_growth = info.get('revenueGrowth', 0.05)
profit_margin = info.get('profitMargins', 0.15)
beta = info.get('beta', 1.0)

risk_free = 0.045
market_premium = 0.055
suggested_wacc = round(risk_free + beta * market_premium, 2)

if sector in ['Technology', 'Communication Services']:
    suggested_terminal = 0.03
elif sector in ['Consumer Defensive', 'Utilities']:
    suggested_terminal = 0.02
else:
    suggested_terminal = 0.025

# Determine data period label
if basis == "LTM (Last 4 Quarters)":
    period_end = quarterly_income.columns[0].strftime('%b %Y')
    period_label = f"LTM through {period_end}"
else:
    period_end = annual_income.columns[0].strftime('%b %Y')
    period_label = f"FY ending {period_end}"

st.markdown(f'<div class="section-label">Company: {company_name}  ·  Sector: {sector}  ·  Beta: {beta:.2f}  ·  {period_label}</div>', unsafe_allow_html=True)

st.markdown('<div class="section-label" style="margin-top:1rem">Assumptions (Edit to Test Scenarios)</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
with c1:
    growth_rate = st.number_input("Year 1 Growth (%)", value=float(recent_growth * 100), step=0.5) / 100
with c2:
    ufcf_margin = st.number_input("UFCF Margin (%)", value=float(profit_margin * 120), step=0.5) / 100
with c3:
    wacc = st.number_input("WACC (%)", value=float(suggested_wacc * 100), step=0.25) / 100
with c4:
    terminal_growth_rate = st.number_input("Terminal Growth (%)", value=float(suggested_terminal * 100), step=0.25) / 100

try:
    if basis == "LTM (Last 4 Quarters)":
        revenue = quarterly_income.loc['Total Revenue'].iloc[:4].sum()
        ebit = quarterly_income.loc['EBIT'].iloc[:4].sum()
        tax_provision = quarterly_income.loc['Tax Provision'].iloc[:4].sum()
        pretax_income = quarterly_income.loc['Pretax Income'].iloc[:4].sum()
        da = quarterly_cash.loc['Depreciation And Amortization'].iloc[:4].sum()
        capital_expenditure = quarterly_cash.loc['Capital Expenditure'].iloc[:4].sum()
        diluted_average_shares = quarterly_income.loc['Diluted Average Shares'].iloc[0]
    else:
        date = annual_income.columns[0]
        revenue = annual_income.loc['Total Revenue', date]
        ebit = annual_income.loc['EBIT', date]
        tax_provision = annual_income.loc['Tax Provision', date]
        pretax_income = annual_income.loc['Pretax Income', date]
        da = annual_cash.loc['Depreciation And Amortization', date]
        capital_expenditure = annual_cash.loc['Capital Expenditure', date]
        diluted_average_shares = annual_income.loc['Diluted Average Shares', date]
    
    bs_date = balance_sheet.columns[0]
    try:
        net_debt = balance_sheet.loc['Net Debt', bs_date]
        if pd.isna(net_debt):
            net_debt = balance_sheet.loc['Total Debt', bs_date] - balance_sheet.loc['Cash And Cash Equivalents', bs_date]
    except:
        net_debt = balance_sheet.loc['Total Debt', bs_date] - balance_sheet.loc['Cash And Cash Equivalents', bs_date]
    
    effective_tax_rate = tax_provision / pretax_income
    
    projected_ufcfs = []
    projection_data = []
    current_rev = revenue
    for year in range(1, 6):
        year_growth = growth_rate - (growth_rate - terminal_growth_rate) * (year - 1) / 4
        current_rev = current_rev * (1 + year_growth)
        projected_ufcf = current_rev * ufcf_margin
        projected_ufcfs.append(projected_ufcf)
        projection_data.append({
            'Year': f'Year {year}',
            'Growth Rate': f'{year_growth:.1%}',
            'Revenue': f'${current_rev/1e9:,.1f}B',
            'UFCF': f'${projected_ufcf/1e9:,.1f}B'
        })
    
    discounted_ufcfs = []
    for year, cf in enumerate(projected_ufcfs, 1):
        pv = cf / (1 + wacc) ** year
        discounted_ufcfs.append(pv)
    
    terminal_value = projected_ufcfs[-1] * (1 + terminal_growth_rate) / (wacc - terminal_growth_rate)
    pv_terminal_value = terminal_value / (1 + wacc) ** 5
    
    enterprise_value = sum(discounted_ufcfs) + pv_terminal_value
    equity_value = enterprise_value - net_debt
    price_per_share = equity_value / diluted_average_shares
    
    st.markdown('<div class="section-label" style="margin-top:1.5rem">Valuation Output</div>', unsafe_allow_html=True)
    
    if current_price:
        upside = (price_per_share / current_price - 1) * 100
        col_class = 'metric-positive' if upside > 0 else 'metric-negative'
        verdict = "UNDERVALUED" if upside > 0 else "OVERVALUED"
    else:
        upside = 0
        col_class = ''
        verdict = "N/A"
    
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-label">Implied Price</div>
            <div class="metric-value">${price_per_share:,.2f}</div>
        </div>""", unsafe_allow_html=True)
    with m2:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-label">Current Price</div>
            <div class="metric-value">${current_price:,.2f}</div>
        </div>""", unsafe_allow_html=True)
    with m3:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-label">Upside / (Downside)</div>
            <div class="metric-value {col_class}">{upside:+.1f}%</div>
        </div>""", unsafe_allow_html=True)
    with m4:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-label">Verdict</div>
            <div class="metric-value {col_class}">{verdict}</div>
        </div>""", unsafe_allow_html=True)
    
    st.markdown(f'<div class="section-label" style="margin-top:1.5rem">5-Year Projections (Starting Revenue: ${revenue/1e9:,.1f}B)</div>', unsafe_allow_html=True)
    st.dataframe(pd.DataFrame(projection_data), use_container_width=True, hide_index=True)
    
    st.markdown('<div class="section-label" style="margin-top:1.5rem">Value Breakdown</div>', unsafe_allow_html=True)
    
    b1, b2, b3 = st.columns(3)
    with b1:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-label">PV of 5-Year UFCF</div>
            <div class="metric-value">${sum(discounted_ufcfs)/1e9:,.1f}B</div>
            <div class="metric-delta" style="color:#475569">{sum(discounted_ufcfs)/enterprise_value:.0%} of EV</div>
        </div>""", unsafe_allow_html=True)
    with b2:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-label">PV of Terminal Value</div>
            <div class="metric-value">${pv_terminal_value/1e9:,.1f}B</div>
            <div class="metric-delta" style="color:#475569">{pv_terminal_value/enterprise_value:.0%} of EV</div>
        </div>""", unsafe_allow_html=True)
    with b3:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-label">Enterprise Value</div>
            <div class="metric-value">${enterprise_value/1e9:,.1f}B</div>
            <div class="metric-delta" style="color:#475569">Net Debt: ${net_debt/1e9:,.1f}B</div>
        </div>""", unsafe_allow_html=True)

except Exception as e:
    st.error(f"Error calculating DCF: {e}")