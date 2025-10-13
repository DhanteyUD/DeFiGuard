; ============================================
; DeFiGuard Risk Knowledge Graph
; Powered by SingularityNET MeTTa
; ============================================

; Define types
(: Asset Type)
(: RiskLevel Type)
(: Token Type)
(: Threshold Type)

; ============================================
; ASSET RISK CLASSIFICATIONS
; ============================================

; Low-risk assets (established cryptocurrencies)
(has-risk bitcoin low)
(has-risk btc low)
(has-risk ethereum low)
(has-risk eth low)
(has-risk bnb low)
(has-risk cardano low)
(has-risk ada low)
(has-risk solana low)
(has-risk sol low)
(has-risk polkadot low)
(has-risk dot low)

; Stablecoins (lowest risk)
(has-risk usdc low)
(has-risk usdt low)
(has-risk dai low)
(has-risk busd low)
(has-risk frax low)
(has-risk tusd low)

; Medium-risk DeFi tokens
(has-risk uniswap medium)
(has-risk uni medium)
(has-risk aave medium)
(has-risk compound medium)
(has-risk comp medium)
(has-risk curve medium)
(has-risk crv medium)

; ============================================
; HIGH-RISK ASSET PATTERNS
; ============================================

; Leveraged tokens (critical risk)
(has-risk-pattern leverage critical)
(has-risk-pattern 3x critical)
(has-risk-pattern 5x critical)
(has-risk-pattern 10x critical)
(has-risk-pattern 2x high)

; Directional tokens (high risk)
(has-risk-pattern short high)
(has-risk-pattern bear high)
(has-risk-pattern bull high)
(has-risk-pattern long high)

; Meme/speculative tokens (critical risk)
(has-risk-pattern safemoon critical)
(has-risk-pattern baby critical)
(has-risk-pattern elon critical)
(has-risk-pattern moon high)
(has-risk-pattern doge high)
(has-risk-pattern shib high)
(has-risk-pattern inu high)

; New/unverified tokens
(has-risk-pattern new critical)
(has-risk-pattern launch critical)
(has-risk-pattern presale critical)

; ============================================
; CONCENTRATION RISK RULES
; ============================================

; Critical: Over 70% in single asset
(concentration-threshold critical 0.70)
(concentration-rule
    (if (> single-asset-percentage 0.70)
        (alert "Extreme concentration - critical risk")
        (action "Diversify immediately")))

; High: Over 50% in single asset  
(concentration-threshold high 0.50)
(concentration-rule
    (if (> single-asset-percentage 0.50)
        (alert "High concentration risk")
        (action "Reduce top holding to under 50%")))

; Medium: Over 30% in single asset
(concentration-threshold medium 0.30)
(concentration-rule
    (if (> single-asset-percentage 0.30)
        (alert "Moderate concentration")
        (action "Consider diversification")))

; ============================================
; VOLATILITY RISK RULES
; ============================================

; Extreme volatility (>50% change in 24h)
(volatility-threshold extreme 50)
(volatility-rule
    (if (> price-change-24h 50)
        (alert "Extreme volatility detected")
        (action "Consider stop-loss orders")))

; High volatility (>20% change in 24h)
(volatility-threshold high 20)
(volatility-rule
    (if (> price-change-24h 20)
        (alert "High volatility")
        (action "Monitor closely - set alerts")))

; Medium volatility (>10% change in 24h)
(volatility-threshold medium 10)
(volatility-rule
    (if (> price-change-24h 10)
        (alert "Elevated volatility")
        (action "Normal for crypto - stay informed")))

; ============================================
; PORTFOLIO COMPOSITION RULES
; ============================================

; Stablecoin allocation recommendations
(rule (stablecoin-ratio)
    (if (< stablecoin-percentage 0.10)
        (recommend "Increase stablecoin allocation to at least 10%")))

(rule (high-risk-exposure)
    (if (> high-risk-assets-percentage 0.30)
        (alert "High exposure to risky assets")
        (recommend "Reduce high-risk allocation below 30%")))

; ============================================
; RISK SCORING WEIGHTS
; ============================================

; Multi-factor risk calculation weights
(weight concentration 0.3)
(weight volatility 0.4)
(weight asset-quality 0.3)

; ============================================
; MARKET CONDITION RULES
; ============================================

(market-condition
    (if (and (< btc-dominance 0.40) (> market-cap 2000000000000))
        (context "Altcoin season - higher risk/reward")
        (recommendation "Diversification more important")))

(market-condition
    (if (and (> btc-dominance 0.60) (< market-cap 1000000000000))
        (context "Bitcoin dominance - defensive posture")
        (recommendation "Flight to quality - reduce altcoin exposure")))

; ============================================
; CORRELATION RISK
; ============================================

(correlation-rule
    (if (> asset-correlation 0.80)
        (alert "High correlation between assets")
        (recommendation "Limited true diversification")))

; ============================================
; LIQUIDITY RISK
; ============================================

(liquidity-rule
    (if (< daily-volume 100000)
        (alert "Low liquidity")
        (risk-level high)))

(liquidity-rule
    (if (< daily-volume 10000)
        (alert "Very low liquidity - exit difficulty")
        (risk-level critical)))

; ============================================
; REBALANCING TRIGGERS
; ============================================

(rebalancing-rule
    (if (> portfolio-drift 0.15)
        (action "Rebalance recommended")
        (priority medium)))

(rebalancing-rule
    (if (> portfolio-drift 0.25)
        (action "Urgent rebalancing needed")
        (priority high)))

; ============================================
; FRAUD/SCAM INDICATORS
; ============================================

(fraud-indicator honeypot critical)
(fraud-indicator unverified-contract critical)
(fraud-indicator no-liquidity-lock critical)
(fraud-indicator ownership-not-renounced high)
(fraud-indicator high-tax high)

; ============================================
; KNOWLEDGE GRAPH METADATA
; ============================================

; Version and attribution
(metadata version "1.0")
(metadata author "DeFiGuard")
(metadata powered-by "SingularityNET MeTTa")
(metadata last-updated "2025-10-12")

; Knowledge graph statistics
(metadata total-assets 50)
(metadata total-rules 25)
(metadata risk-factors 10)

; End of DeFiGuard Risk Knowledge Graph