from core.position_sizing import calculate_position_size

capital = 10_000

print("=== Skenario BTC (volatilitas lebih rendah, stop-loss lebih sempit) ===")
btc_sl = 0.8 * 0.0354  # ATR% BTC (3.54%) x multiplier 0.8x
result = calculate_position_size(capital, stop_loss_pct=btc_sl, risk_per_trade_pct=0.01)
print(f"Stop-loss: {btc_sl*100:.2f}%")
print(result)

print("\n=== Skenario ETH (volatilitas lebih tinggi, stop-loss lebih lebar) ===")
eth_sl = 0.8 * 0.0543  # ATR% ETH (5.43%) x multiplier 0.8x
result = calculate_position_size(capital, stop_loss_pct=eth_sl, risk_per_trade_pct=0.01)
print(f"Stop-loss: {eth_sl*100:.2f}%")
print(result)