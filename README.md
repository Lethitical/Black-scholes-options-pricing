# Black-Scholes Options Pricing & Implied Volatility

Python implementation of the Black-Scholes-Merton model applied to live
Tesla (TSLA) options data. Prices European calls and puts, back-solves
for implied volatility using Brent's method, and visualises the
resulting volatility smile.

![Volatility Smile](volatility_smile.png)

## What It Does

1. Implements BSM from scratch — no pricing libraries
2. Verifies correctness via put-call parity
3. Fetches live TSLA option chain data via `yfinance`
4. Inverts the model numerically to extract implied volatility per strike
5. Plots the IV smile and analyses the skew structure

## The Model

$$C = S \cdot N(d_1) - K \cdot e^{-rT} \cdot N(d_2)$$

$$d_1 = \frac{\ln(S/K) + (r + \sigma^2/2)T}{\sigma\sqrt{T}}, \quad d_2 = d_1 - \sigma\sqrt{T}$$

| Symbol | Meaning |
|--------|---------|
| $S$ | Spot price |
| $K$ | Strike price |
| $T$ | Time to expiry (years) |
| $r$ | Risk-free rate |
| $\sigma$ | Volatility |
| $N(\cdot)$ | Cumulative normal CDF |
## Key Findings (TSLA, fetched ~April 2025)

- ATM implied volatility: ~43.6% at spot ≈ $395
- Pronounced left skew — deep OTM puts carry IV of 200%+
- The skew reflects asymmetric tail-risk pricing: markets price
  a sharp downside move far more heavily than an equivalent rally
- Confirms BSM's constant-volatility assumption breaks down in
  practice — the smile itself is evidence of model misspecification

## Limitations & Extensions

BSM assumes constant volatility and log-normal returns — both
violated empirically. The volatility smile is a direct consequence
of this. Natural extensions include:

- **Stochastic volatility**: Heston model allows σ to follow its
  own mean-reverting process, producing a more realistic smile
- **Local volatility**: Dupire's framework back-solves for a
  deterministic σ(S,t) surface consistent with all market prices
- **Jump diffusion**: Merton's jump model adds Poisson-distributed
  price jumps, better capturing crash risk priced into OTM puts

## Stack

`numpy` · `scipy` · `matplotlib` · `yfinance`

## Run

```bash
pip install numpy scipy matplotlib yfinance
python black_scholes.py
```
