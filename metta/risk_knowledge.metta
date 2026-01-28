; ============================================
; DeFiGuard Risk Knowledge Graph
; Powered by SingularityNET MeTTa
; Enhanced with Solana-specific rules
; ============================================

; Define types
(: Asset Type)
(: RiskLevel Type)
(: Token Type)
(: Threshold Type)
(: Chain Type)

; ============================================
; CHAIN DEFINITIONS
; ============================================

(chain solana non-evm)
(chain ethereum evm)
(chain bsc evm)
(chain polygon evm)
(chain arbitrum evm)
(chain optimism evm)
(chain base evm)
(chain avalanche evm)

; ============================================
; ASSET RISK CLASSIFICATIONS - EVM
; ============================================

; Low-risk assets (established cryptocurrencies)
(has-risk bitcoin low)
(has-risk btc low)
(has-risk ethereum low)
(has-risk eth low)
(has-risk bnb low)
(has-risk cardano low)
(has-risk ada low)

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
; SOLANA-SPECIFIC ASSET CLASSIFICATIONS
; ============================================

; Solana Native (low risk)
(has-risk solana low)
(has-risk sol low)

; Major Solana DeFi (medium risk)
(has-risk raydium medium)
(has-risk ray medium)
(has-risk orca medium)
(has-risk jupiter medium)
(has-risk jup medium)
(has-risk marinade medium)
(has-risk mnde medium)
(has-risk jito medium)
(has-risk pyth medium)

; Solana Liquid Staking (low-medium risk)
(has-risk msol low)
(has-risk jitosol low)
(has-risk bsol medium)

; Solana Meme Coins (high risk)
(has-risk bonk high)
(has-risk wif high)
(has-risk dogwifhat high)
(has-risk popcat high)
(has-risk myro high)
(has-risk wen high)
(has-risk slerf critical)

; ============================================
; HIGH-RISK ASSET PATTERNS (ALL CHAINS)
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
(has-risk-pattern pepe high)
(has-risk-pattern floki high)

; New/unverified tokens
(has-risk-pattern new critical)
(has-risk-pattern launch critical)
(has-risk-pattern presale critical)
(has-risk-pattern fair-launch high)

; ============================================
; SOLANA-SPECIFIC RISK PATTERNS
; ============================================

; Solana meme coin patterns
(has-solana-risk-pattern cat high)
(has-solana-risk-pattern dog high)
(has-solana-risk-pattern pump critical)
(has-solana-risk-pattern fun critical)
(has-solana-risk-pattern ai-agent high)

; Solana rug pull indicators
(has-solana-risk-pattern mint-authority-active high)
(has-solana-risk-pattern freeze-authority-active critical)
(has-solana-risk-pattern no-metadata high)
(has-solana-risk-pattern unverified high)

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
; SOLANA-SPECIFIC FRAUD RULES
; ============================================

; Mint authority checks
(solana-fraud-rule
    (if (mint-authority-not-revoked)
        (alert "Mint authority ACTIVE - unlimited supply risk")
        (risk-level high)
        (action "Verify with team or avoid")))

; Freeze authority checks
(solana-fraud-rule
    (if (freeze-authority-active)
        (alert "Freeze authority ACTIVE - tokens can be frozen")
        (risk-level critical)
        (action "DO NOT INVEST - critical centralization risk")))

; Holder concentration on Solana
(solana-concentration-rule
    (if (> top-holder-percent 0.50)
        (alert "Top holder owns >50% - extreme rug pull risk")
        (risk-level critical)))

(solana-concentration-rule
    (if (> top-holder-percent 0.30)
        (alert "Top holder owns >30% - high concentration")
        (risk-level high)))

; Liquidity checks
(solana-liquidity-rule
    (if (< total-liquidity-usd 10000)
        (alert "Very low liquidity - exit difficulty")
        (risk-level high)))

(solana-liquidity-rule
    (if (no-liquidity-pools)
        (alert "No liquidity pools found - cannot trade")
        (risk-level critical)))

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

; Chain diversity for Solana portfolios
(rule (solana-only-portfolio)
    (if (and (= chains-count 1) (= chain solana))
        (recommend "Consider diversifying to other chains")
        (risk-adjustment +0.10)))

; ============================================
; RISK SCORING WEIGHTS
; ============================================

; Multi-factor risk calculation weights
(weight concentration 0.30)
(weight volatility 0.35)
(weight asset-quality 0.20)
(weight chain-diversity 0.15)

; Solana-specific weight adjustments
(solana-weight mint-authority 0.25)
(solana-weight freeze-authority 0.30)
(solana-weight holder-concentration 0.25)
(solana-weight liquidity 0.20)

; ============================================
; CROSS-CHAIN CORRELATION RULES
; ============================================

(correlation-rule
    (if (and (has-asset solana) (has-asset ethereum))
        (note "Cross-chain diversification detected")
        (risk-adjustment -0.05)))

(correlation-rule
    (if (> solana-meme-coins-percentage 0.20)
        (alert "High Solana meme coin exposure")
        (risk-adjustment +0.15)))

; ============================================
; KNOWLEDGE GRAPH METADATA
; ============================================

; Version and attribution
(metadata version "2.0-solana")
(metadata author "DeFiGuard")
(metadata powered-by "SingularityNET MeTTa")
(metadata last-updated "2025-01-27")
(metadata solana-support true)

; Knowledge graph statistics
(metadata total-assets 75)
(metadata total-rules 40)
(metadata risk-factors 15)
(metadata supported-chains 13)
(metadata solana-specific-rules 12)

; End of DeFiGuard Risk Knowledge Graph (Solana Enhanced)
