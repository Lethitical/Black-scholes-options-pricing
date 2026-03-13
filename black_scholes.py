import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
from scipy.stats import norm
from scipy.optimize import brentq

# ─────────────────────────────────────
# BLACK-SCHOLES FORMULA
# ─────────────────────────────────────

def black_scholes(S, K, T, r, sigma, option_type='call'):
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    if option_type == 'call':
        return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    else:
        return K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)


# ─────────────────────────────────────
# IMPLIED VOLATILITY CALCULATOR
# ─────────────────────────────────────

def implied_volatility(market_price, S, K, T, r, option_type='call'):
    try:
        iv = brentq(
            lambda sigma: black_scholes(S, K, T, r, sigma, option_type) - market_price,
            0.001,
            10.0
        )
        return iv
    except:
        return np.nan


# ─────────────────────────────────────
# TEST THE FORMULA
# ─────────────────────────────────────

print("=" * 50)
print("BLACK-SCHOLES PRICING TEST")
print("=" * 50)

S = 200
K = 200
T = 0.25
r = 0.05
sigma = 0.40

call_price = black_scholes(S, K, T, r, sigma, 'call')
put_price  = black_scholes(S, K, T, r, sigma, 'put')

print(f"Stock price:      £{S}")
print(f"Strike price:     £{K}")
print(f"Time to expiry:   {T} years (3 months)")
print(f"Risk free rate:   {r*100}%")
print(f"Volatility:       {sigma*100}%")
print(f"\nCall option price: £{call_price:.2f}")
print(f"Put option price:  £{put_price:.2f}")

# Verify put-call parity
parity = call_price - put_price
expected = S - K * np.exp(-r * T)
print(f"\nPut-call parity check:")
print(f"Call - Put = £{parity:.2f}")
print(f"S - Ke^-rT = £{expected:.2f}")


# ─────────────────────────────────────
# PULL REAL TESLA OPTIONS DATA
# ─────────────────────────────────────

print("\n" + "=" * 50)
print("PULLING REAL TESLA OPTIONS DATA")
print("=" * 50)

tsla = yf.Ticker("TSLA")
current_price = tsla.history(period='1d')['Close'].iloc[-1]
print(f"Tesla current price: ${current_price:.2f}")

# Get available expiry dates
expiry_dates = tsla.options
print(f"Available expiry dates: {expiry_dates[:5]}")

# Pick the 3rd expiry date (roughly 1-3 months out)
chosen_expiry = expiry_dates[2]
print(f"\nUsing expiry date: {chosen_expiry}")

# Pull the options chain
chain = tsla.option_chain(chosen_expiry)
calls = chain.calls
puts  = chain.puts

# Filter to options near the current price (within 20%)
calls = calls[
    (calls['strike'] >= current_price * 0.80) &
    (calls['strike'] <= current_price * 1.20)
].copy()

print(f"\nCall options near current price:")
print(calls[['strike', 'lastPrice', 'impliedVolatility', 'volume']].to_string(index=False))


# ─────────────────────────────────────
# CALCULATE IMPLIED VOLATILITY
# ─────────────────────────────────────

print("\n" + "=" * 50)
print("CALCULATING IMPLIED VOLATILITY")
print("=" * 50)

# Time to expiry in years
from datetime import datetime
expiry_dt = datetime.strptime(chosen_expiry, '%Y-%m-%d')
T_real = (expiry_dt - datetime.today()).days / 365
r_real = 0.05

print(f"Days to expiry: {(expiry_dt - datetime.today()).days}")
print(f"T (years): {T_real:.4f}")

# Calculate IV for each strike
ivs = []
for _, row in calls.iterrows():
    if row['lastPrice'] > 0.01:
        iv = implied_volatility(
            market_price=row['lastPrice'],
            S=current_price,
            K=row['strike'],
            T=T_real,
            r=r_real,
            option_type='call'
        )
        ivs.append({'strike': row['strike'], 'iv': iv, 'market_price': row['lastPrice']})

iv_df = [x for x in ivs if not np.isnan(x['iv'])]
strikes = [x['strike'] for x in iv_df]
iv_values = [x['iv'] * 100 for x in iv_df]

print(f"\nStrike prices and implied volatilities:")
for x in iv_df:
    print(f"  Strike ${x['strike']:.0f}: IV = {x['iv']*100:.1f}%")


# ─────────────────────────────────────
# PLOT THE VOLATILITY SMILE
# ─────────────────────────────────────

plt.figure(figsize=(12, 7))

plt.plot(strikes, iv_values, 'b-o', linewidth=2, markersize=6, label='Implied Volatility')

# Mark the current stock price
plt.axvline(x=current_price, color='red', linestyle='--', linewidth=1.5,
            label=f'Current Price (${current_price:.0f})')

# Mark the minimum IV point
min_iv_idx = iv_values.index(min(iv_values))
plt.scatter(strikes[min_iv_idx], iv_values[min_iv_idx], color='green',
            zorder=5, s=150, label=f'Min IV: {iv_values[min_iv_idx]:.1f}%')

plt.xlabel('Strike Price ($)', fontsize=13)
plt.ylabel('Implied Volatility (%)', fontsize=13)
plt.title(f'Tesla Implied Volatility Smile\nExpiry: {chosen_expiry}  |  Current Price: ${current_price:.2f}',
          fontsize=14)
plt.legend(fontsize=11)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('volatility_smile.png', dpi=150)
plt.show()

print("\nPlot saved as volatility_smile.png")
print("\nDone!")