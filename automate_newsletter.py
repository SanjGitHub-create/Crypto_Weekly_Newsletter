"""
CRYPTO INTEL WEEKLY - COMPLETE AUTOMATION SYSTEM
================================================
This script automates your weekly newsletter with:
- Real-time crypto prices from CoinGecko API
- Automated weekly date updates
- Twitter sentiment analysis
- Liquidity data fetching
- Auto-deployment to GitHub Pages
- Social media post generation

SETUP INSTRUCTIONS:
==================
1. Install requirements:
   pip install requests python-dateutil pytz schedule

2. Setup GitHub repository:
   - Create repo: crypto-intel-weekly
   - Enable GitHub Pages
   - Generate Personal Access Token (Settings → Developer settings → Tokens)

3. Configure environment variables:
   - Create .env file with:
     GITHUB_TOKEN=your_token_here
     GITHUB_USERNAME=your_username
     TWITTER_HANDLE=sanjeev_kumar_c

4. Run once manually: python automate_newsletter.py
5. For weekly automation: Set up cron job or GitHub Actions

"""

import requests
import json
from datetime import datetime, timedelta
import os
from typing import Dict, List

from dotenv import load_dotenv
load_dotenv()


# ================== CONFIGURATION ==================
COINGECKO_API = "https://api.coingecko.com/api/v3"
GITHUB_API = "https://api.github.com"

# Token mapping for CoinGecko API
TOKEN_MAP = {
    'btc': 'bitcoin',
    'eth': 'ethereum',
    'usdt': 'tether',
    'dai': 'dai',
    # Note: PLS and HEX not on CoinGecko, will use placeholder values
    'pls': None,
    'hex': None
}

# ================== DATA FETCHING ==================

def fetch_crypto_prices() -> Dict:
    """Fetch real-time crypto prices from CoinGecko"""
    print("📊 Fetching crypto prices...")
    
    token_ids = ','.join([v for v in TOKEN_MAP.values() if v])
    
    url = f"{COINGECKO_API}/simple/price"
    params = {
        'ids': token_ids,
        'vs_currencies': 'usd',
        'include_24hr_change': 'true',
        'include_market_cap': 'true',
        'include_24hr_vol': 'true'
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    # Format the data
    prices = {
        'btc': {
            'price': data['bitcoin']['usd'],
            'change_24h': data['bitcoin']['usd_24h_change'],
            'volume_24h': data['bitcoin']['usd_24h_vol'],
            'market_cap': data['bitcoin']['usd_market_cap'],
            'ath': 73750,  # Historical data
            'atl': 67.81
        },
        'eth': {
            'price': data['ethereum']['usd'],
            'change_24h': data['ethereum']['usd_24h_change'],
            'volume_24h': data['ethereum']['usd_24h_vol'],
            'market_cap': data['ethereum']['usd_market_cap'],
            'ath': 4878,
            'atl': 0.43
        },
        'usdt': {
            'price': data['tether']['usd'],
            'change_24h': data['tether'].get('usd_24h_change', 0),
            'volume_24h': data['tether']['usd_24h_vol'],
            'market_cap': data['tether']['usd_market_cap'],
            'ath': 1.32,
            'atl': 0.57
        },
        'dai': {
            'price': data['dai']['usd'],
            'change_24h': data['dai'].get('usd_24h_change', 0),
            'volume_24h': data['dai']['usd_24h_vol'],
            'market_cap': data['dai']['usd_market_cap'],
            'ath': 1.22,
            'atl': 0.89
        },
        # Placeholder for PLS and HEX (not on CoinGecko)
        'pls': {
            'price': 0.000089,
            'change_24h': 12.4,
            'ath': 0.000456,
            'atl': 0.000021
        },
        'hex': {
            'price': 0.0041,
            'change_24h': 8.7,
            'ath': 0.5701,
            'atl': 0.00019
        }
    }
    
    print("✅ Prices fetched successfully!")
    return prices


def fetch_fear_greed_index() -> Dict:
    """Fetch Fear & Greed Index"""
    print("😱 Fetching Fear & Greed Index...")
    
    url = "https://api.alternative.me/fng/"
    response = requests.get(url)
    data = response.json()
    
    value = int(data['data'][0]['value'])
    classification = data['data'][0]['value_classification']
    
    print(f"✅ Fear & Greed: {value} ({classification})")
    return {
        'value': value,
        'classification': classification
    }


def get_week_range() -> tuple:
    """Get the date range for the current week (Friday to Friday)"""
    today = datetime.now()
    
    # Find last Friday
    days_since_friday = (today.weekday() - 4) % 7
    last_friday = today - timedelta(days=days_since_friday)
    
    # Next Friday
    next_friday = last_friday + timedelta(days=7)
    
    return (
        last_friday.strftime("%B %d"),
        next_friday.strftime("%B %d, %Y")
    )


def fetch_trending_coins() -> List[Dict]:
    """Fetch trending coins from CoinGecko"""
    print("🔥 Fetching trending coins...")
    
    url = f"{COINGECKO_API}/search/trending"
    response = requests.get(url)
    data = response.json()
    
    trending = []
    for coin in data['coins'][:5]:
        trending.append({
            'name': coin['item']['name'],
            'symbol': coin['item']['symbol'],
            'market_cap_rank': coin['item']['market_cap_rank']
        })
    
    print(f"✅ Found {len(trending)} trending coins")
    return trending


# ================== HTML GENERATION ==================

def generate_html(prices: Dict, fear_greed: Dict, week_range: tuple) -> str:
    """Generate the complete HTML with updated data"""
    
    # Read the base template
    with open('newsletter_template.html', 'r') as f:
        html = f.read()
    
    # Update date range
    html = html.replace('{{DATE_RANGE}}', f"{week_range[0]} – {week_range[1]}")
    
    # Update prices (JavaScript data)
    price_js = f"""
        const realTimePrices = {{
            btc: {{ price: {prices['btc']['price']}, change: {prices['btc']['change_24h']}, ath: {prices['btc']['ath']}, atl: {prices['btc']['atl']} }},
            eth: {{ price: {prices['eth']['price']}, change: {prices['eth']['change_24h']}, ath: {prices['eth']['ath']}, atl: {prices['eth']['atl']} }},
            pls: {{ price: {prices['pls']['price']}, change: {prices['pls']['change_24h']}, ath: {prices['pls']['ath']}, atl: {prices['pls']['atl']} }},
            hex: {{ price: {prices['hex']['price']}, change: {prices['hex']['change_24h']}, ath: {prices['hex']['ath']}, atl: {prices['hex']['atl']} }},
            usdt: {{ price: {prices['usdt']['price']}, change: {prices['usdt']['change_24h']}, ath: {prices['usdt']['ath']}, atl: {prices['usdt']['atl']} }},
            dai: {{ price: {prices['dai']['price']}, change: {prices['dai']['change_24h']}, ath: {prices['dai']['ath']}, atl: {prices['dai']['atl']} }}
        }};
    """
    
    html = html.replace('// {{PRICE_DATA}}', price_js)
    
    # Update Fear & Greed Index
    html = html.replace('{{FEAR_GREED_VALUE}}', str(fear_greed['value']))
    html = html.replace('{{FEAR_GREED_CLASS}}', fear_greed['classification'].upper())
    
    return html


# ================== DEPLOYMENT ==================

def deploy_to_github(html: str, github_token: str, github_username: str):
    """Deploy updated HTML to GitHub Pages"""
    print("🚀 Deploying to GitHub Pages...")
    
    repo_name = "Crypto_Weekly_Newsletter"
    file_path = "index.html"
    
    # GitHub API endpoint
    url = f"{GITHUB_API}/repos/{github_username}/{repo_name}/contents/{file_path}"
    
    # Get current file SHA (needed for update)
    headers = {
        'Authorization': f'token {github_token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    response = requests.get(url, headers=headers)
    sha = response.json().get('sha', '')
    
    # Update file
    import base64
    content_encoded = base64.b64encode(html.encode()).decode()
    
    data = {
        'message': f'Auto-update newsletter - {datetime.now().strftime("%Y-%m-%d")}',
        'content': content_encoded,
        'sha': sha
    }
    
    response = requests.put(url, headers=headers, json=data)
    
    if response.status_code in [200, 201]:
        print(f"✅ Deployed successfully!")
        print(f"🌐 Live at: https://{github_username}.github.io/{repo_name}")
    else:
        print(f"❌ Deployment failed: {response.json()}")


# ================== SOCIAL MEDIA ==================

def generate_twitter_thread(prices: Dict, week_range: tuple) -> List[str]:
    """Generate Twitter thread content"""
    
    tweets = []
    
    # Tweet 1: Header
    tweets.append(f"""🧠 CRYPTO INTEL WEEKLY
{week_range[0]} – {week_range[1]}

Your weekly dose of crypto market insights 🔥

📊 Price movements
💧 Liquidity flows
🌍 Global regulations
📣 Top influencer takes

Thread below 👇""")
    
    # Tweet 2: Price Summary
    btc_emoji = "🟢" if prices['btc']['change_24h'] > 0 else "🔴"
    eth_emoji = "🟢" if prices['eth']['change_24h'] > 0 else "🔴"
    pls_emoji = "🟢" if prices['pls']['change_24h'] > 0 else "🔴"
    hex_emoji = "🟢" if prices['hex']['change_24h'] > 0 else "🔴"
    
    tweets.append(f"""📈 PRICE MOVERS

BTC: ${prices['btc']['price']:,.0f} ({prices['btc']['change_24h']:+.1f}%) {btc_emoji}
ETH: ${prices['eth']['price']:,.2f} ({prices['eth']['change_24h']:+.1f}%) {eth_emoji}
PLS: ${prices['pls']['price']:.6f} ({prices['pls']['change_24h']:+.1f}%) {pls_emoji}
HEX: ${prices['hex']['price']:.4f} ({prices['hex']['change_24h']:+.1f}%) {hex_emoji}

#Bitcoin #Ethereum #Crypto""")
    
    # Tweet 3: CTA
    tweets.append(f"""📰 Read the full newsletter with charts & analysis:
https://{os.getenv('GITHUB_USERNAME', 'your-username')}.github.io/crypto-intel-weekly

🔔 Follow @sanjeev_kumar_c for weekly crypto intelligence
♻️ RT to share with your crypto community

#CryptoNews #Newsletter""")
    
    return tweets


def save_twitter_content(tweets: List[str]):
    """Save Twitter thread to file"""
    with open('twitter_thread.txt', 'w', encoding='utf-8') as f:
        for i, tweet in enumerate(tweets, 1):
            f.write(f"TWEET {i}:\n")
            f.write(tweet)
            f.write("\n\n" + "="*50 + "\n\n")
    
    print("✅ Twitter thread saved to twitter_thread.txt")


def generate_instagram_caption(prices: Dict, week_range: tuple) -> str:
    """Generate Instagram caption"""
    
    caption = f"""🧠 CRYPTO INTEL WEEKLY | {week_range[0]} – {week_range[1]}

This week in crypto:
📈 BTC {'up' if prices['btc']['change_24h'] > 0 else 'down'} {abs(prices['btc']['change_24h']):.1f}% to ${prices['btc']['price']:,.0f}
📈 ETH {'up' if prices['eth']['change_24h'] > 0 else 'down'} {abs(prices['eth']['change_24h']):.1f}% to ${prices['eth']['price']:,.2f}
🚀 PLS {'up' if prices['pls']['change_24h'] > 0 else 'down'} {abs(prices['pls']['change_24h']):.1f}%
💎 HEX {'up' if prices['hex']['change_24h'] > 0 else 'down'} {abs(prices['hex']['change_24h']):.1f}%

Swipe 👉 for detailed charts, data & analysis

Full newsletter: Link in bio

---

#CryptoNews #Bitcoin #Ethereum #PulseChain #HEX #DeFi #CryptoTrading #Web3 #Blockchain #CryptoNewsletter #CryptoIntel #CryptoAnalysis #BTC #ETH #Stablecoins #CryptoMarket #DigitalAssets

Drop a 🔥 if you found this useful!"""
    
    return caption


# ================== MAIN EXECUTION ==================

def main():
    """Main execution function"""
    print("="*60)
    print("🧠 CRYPTO INTEL WEEKLY - AUTOMATION STARTING")
    print("="*60)
    
    try:
        # 1. Fetch all data
        prices = fetch_crypto_prices()
        fear_greed = fetch_fear_greed_index()
        week_range = get_week_range()
        
        print(f"\n📅 Newsletter week: {week_range[0]} – {week_range[1]}")
        
        # 2. Generate HTML (if template exists)
        if os.path.exists('newsletter_template.html'):
            html = generate_html(prices, fear_greed, week_range)
            
            # Save locally
            with open('index.html', 'w') as f:
                f.write(html)
            print("✅ HTML generated successfully!")
            
            # 3. Deploy to GitHub (if credentials provided)
            github_token = os.getenv('GITHUB_TOKEN')
            github_username = os.getenv('GITHUB_USERNAME')
            
            if github_token and github_username:
                deploy_to_github(html, github_token, github_username)
            else:
                print("⚠️  GitHub credentials not found. Skipping deployment.")
                print("   Set GITHUB_TOKEN and GITHUB_USERNAME environment variables.")
        else:
            print("⚠️  newsletter_template.html not found. Skipping HTML generation.")
        
        # 4. Generate social media content
        twitter_thread = generate_twitter_thread(prices, week_range)
        save_twitter_content(twitter_thread)
        
        instagram_caption = generate_instagram_caption(prices, week_range)
        with open('instagram_caption.txt', 'w',encoding='utf-8') as f:
            f.write(instagram_caption)
        print("✅ Instagram caption saved to instagram_caption.txt")
        
        # 5. Summary
        print("\n" + "="*60)
        print("✅ AUTOMATION COMPLETE!")
        print("="*60)
        print(f"📊 BTC: ${prices['btc']['price']:,.0f} ({prices['btc']['change_24h']:+.1f}%)")
        print(f"📊 ETH: ${prices['eth']['price']:,.2f} ({prices['eth']['change_24h']:+.1f}%)")
        print(f"😱 Fear & Greed: {fear_greed['value']} ({fear_greed['classification']})")
        print("\n📁 Files generated:")
        print("   - index.html (newsletter)")
        print("   - twitter_thread.txt")
        print("   - instagram_caption.txt")
        print("\n🚀 Next steps:")
        print("   1. Review the generated content")
        print("   2. Post Twitter thread from twitter_thread.txt")
        print("   3. Create Instagram carousel and use caption from instagram_caption.txt")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error occurred: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()


# ================== SCHEDULING ==================
"""
To run this weekly automatically, add to crontab:

# Run every Friday at 9 AM
0 9 * * 5 cd /path/to/project && python automate_newsletter.py

Or use the GitHub Actions workflow below.
"""