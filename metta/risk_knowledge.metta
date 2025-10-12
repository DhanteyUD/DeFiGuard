; DeFiGuard Risk Analysis Knowledge Base

; Define types
(: Risk Type)
(: Asset Type)
(: Pattern Type)
(: Alert Type)

; Risk levels
(: low Risk)
(: medium Risk)
(: high Risk)
(: critical Risk)

; Asset risk profiles
(risk-profile bitcoin low)
(risk-profile ethereum low)
(risk-profile usdc low)
(risk-profile usdt low)

; High-risk assets
(risk-profile meme-coin high)
(risk-profile new-token critical)
(risk-profile leverage-token critical)

; Portfolio concentration rules
(concentration-rule
    (if (> single-asset-percentage 50)
        (risk-level high)
        (reason "Over-concentrated in single asset")))

(concentration-rule
    (if (> single-asset-percentage 70)
        (risk-level critical)
        (reason "Extreme concentration - diversification needed")))

; Volatility patterns
(volatility-pattern
    (if (> price-change-24h 20)
        (alert "High volatility detected")
        (action "Consider stop-loss")))

(volatility-pattern
    (if (> price-change-24h 50)
        (alert "Extreme volatility")
        (action "Immediate review recommended")))

; Liquidity risks
(liquidity-risk
    (if (< daily-volume 100000)
        (risk-level high)
        (reason "Low liquidity - exit difficulty")))

; Correlation risks
(correlation-risk
    (if (> asset-correlation 0.8)
        (risk-level medium)
        (reason "High correlation - limited diversification")))

; Smart contract risks
(contract-risk unaudited critical)
(contract-risk audit-failed critical)
(contract-risk audit-passed low)
(contract-risk verified low)

; Fraud patterns
(fraud-indicator
    (pattern honeypot)
    (severity critical)
    (action "Immediate exit recommended"))

(fraud-indicator
    (pattern rug-pull-signs)
    (severity critical)
    (action "High risk - avoid"))

(fraud-indicator
    (pattern wash-trading)
    (severity high)
    (action "Suspicious activity - investigate"))

; Market condition rules
(market-condition
    (if (and (> btc-dominance 60) (< total-market-cap 1T))
        (sentiment bearish)
        (recommendation "Increase stablecoin allocation")))

(market-condition
    (if (and (< btc-dominance 40) (> total-market-cap 2T))
        (sentiment bullish)
        (recommendation "Altcoin season - diversify")))

; Rebalancing rules
(rebalancing-rule
    (if (> portfolio-drift 15)
        (action "Rebalance recommended")
        (priority medium)))

(rebalancing-rule
    (if (> portfolio-drift 25)
        (action "Urgent rebalancing needed")
        (priority high)))

; Risk scoring functions
(define (calculate-portfolio-risk assets)
    (let ((concentration (concentration-score assets))
          (volatility (volatility-score assets))
          (liquidity (liquidity-score assets)))
        (weighted-average concentration 0.3
                         volatility 0.4
                         liquidity 0.3)))

; Alert prioritization
(alert-priority critical immediate)
(alert-priority high within-hour)
(alert-priority medium within-day)
(alert-priority low review-weekly)

; Historical pattern matching
(pattern-match crash-warning
    (conditions
        (sudden-volume-spike 10x)
        (price-drop 15)
        (within-hours 1))
    (probability 0.8)
    (action "Risk of further decline"))

(pattern-match recovery-signal
    (conditions
        (volume-increase gradual)
        (price-stabilization 3-days)
        (support-level-hold))
    (probability 0.7)
    (action "Potential recovery"))

; Cross-chain risk
(cross-chain-risk
    (if (assets-on-multiple-chains)
        (consideration "Bridge risk")
        (mitigation "Monitor bridge security")))

; Stablecoin depeg detection
(depeg-warning
    (if (< stablecoin-price 0.98)
        (alert "Depeg risk")
        (action "Consider alternative stablecoins")))

(depeg-critical
    (if (< stablecoin-price 0.95)
        (alert "Critical depeg")
        (action "Immediate exit recommended")))