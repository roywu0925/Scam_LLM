#!/usr/bin/env python
# -*- coding: utf-8 -*- 
"""
詐騙網址檢測器 (Scam URL Detector)

用法:
  python scam_detector.py <要檢測的網址>

依賴套件安裝:
  pip install requests beautifulsoup4 python-Levenshtein
"""

import sys
import re
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from Levenshtein import distance as levenshtein_distance

# --- 資料庫與權重設定 ---

# 已知的安全網域 (白名單)
KNOWN_SAFE_DOMAINS = [
    "google.com",
    "facebook.com",
    "instagram.com",
    "apple.com",
    "microsoft.com",
    "amazon.com",
    "gov.tw", # 台灣政府機關
    "edu.tw", # 台灣教育機構
    "com.tw", # 台灣商業機構
    "org.tw", # 台灣組織機構
    "net.tw", # 台灣網路機構
    "mvdis.gov.tw", # 監理服務網
    "moi.gov.tw", # 內政部
    "mof.gov.tw", # 財政部
    "moe.gov.tw"  # 教育部
]

# 已知的詐騙網域 (黑名單)
KNOWN_PHISHING_DOMAINS = [
    "mvdlstw.net" # 我們發現的詐騙網站
]

# 可疑的頂級域名 (TLD)
SUSPICIOUS_TLDS = {
    ".xyz", ".top", ".club", ".site", ".online", ".buzz", ".info", ".cn", ".ru"
}

# 可疑的URL關鍵字
SUSPICIOUS_KEYWORDS = [
    "login", "secure", "account", "update", "verify", "password", "signin", "banking", "confirm"
]

# 分數權重
SCORE_WEIGHTS = {
    "KNOWN_PHISHING": 100,
    "IP_AS_DOMAIN": 30,
    "NO_HTTPS": 25,
    "SUSPICIOUS_TLD": 20,
    "TYPOSQUATTING": 40, # 模仿知名網域
    "KEYWORD": 5, # 每個關鍵字加5分
    "LONG_URL": 10, # URL過長
    "AT_SYMBOL": 20, # URL中包含@
    "PASSWORD_FIELD": 30 # 頁面中有密碼輸入框
}

def analyze_url(url):
    '''分析URL本身的特徵'''
    score = 0
    reasons = []
    
    try:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()
        path = parsed_url.path.lower()

        # 移除 www. 以便比對
        if domain.startswith("www."):
            domain = domain[4:]

        # 1. 黑白名單檢查
        if domain in KNOWN_PHISHING_DOMAINS:
            score = SCORE_WEIGHTS["KNOWN_PHISHING"]
            reasons.append(f"此網域在已知的詐騙黑名單中 ({domain})")
            return score, reasons
        
        for safe_domain in KNOWN_SAFE_DOMAINS:
            if domain.endswith(safe_domain):
                # 在白名單中，直接視為安全
                return 0, ["此網域在已知的安全名單中"]

        # 2. 檢查是否使用IP地址而非域名
        if re.match(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", domain):
            score += SCORE_WEIGHTS["IP_AS_DOMAIN"]
            reasons.append("使用IP位址而非網域名稱")

        # 3. 檢查是否使用HTTPS
        if parsed_url.scheme != 'https':
            score += SCORE_WEIGHTS["NO_HTTPS"]
            reasons.append("未使用安全的HTTPS加密連線")

        # 4. 檢查可疑的頂級域名 (TLD)
        tld = "." + domain.split('.')[-1]
        if tld in SUSPICIOUS_TLDS:
            score += SCORE_WEIGHTS["SUSPICIOUS_TLD"]
            reasons.append(f"使用可疑的頂級域名 ({tld})")

        # 5. 檢查網域模仿 (Typosquatting)
        for safe_domain in KNOWN_SAFE_DOMAINS:
            # 只比對主要域名部分，避免誤判 (例如 a.b.com.tw vs c.com.tw)
            main_domain_part = ".".join(domain.split('.')[-2:])
            if levenshtein_distance(main_domain_part, safe_domain) in [1, 2]:
                score += SCORE_WEIGHTS["TYPOSQUATTING"]
                reasons.append(f"網域可能在模仿一個已知的安全網站: {safe_domain}")
                break

        # 6. 檢查URL中的可疑關鍵字
        for keyword in SUSPICIOUS_KEYWORDS:
            if keyword in url.lower():
                score += SCORE_WEIGHTS["KEYWORD"]
                reasons.append(f"URL中包含可疑關鍵字: {keyword}")

        # 7. 檢查URL長度
        if len(url) > 75:
            score += SCORE_WEIGHTS["LONG_URL"]
            reasons.append("URL長度過長")

        # 8. 檢查URL中是否包含 '@' 符號 (常見的混淆技巧)
        if '@' in parsed_url.path:
            score += SCORE_WEIGHTS["AT_SYMBOL"]
            reasons.append("URL路徑中包含 '@' 符號")

    except Exception as e:
        reasons.append(f"URL分析時發生錯誤: {e}")

    return score, reasons

def analyze_content(url):
    '''分析網頁內容的特徵'''
    score = 0
    reasons = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        # 讓使用者知道程式正在連線
        print("\n正在嘗試連線並分析網頁內容...")
        response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        response.raise_for_status() # 如果請求失敗，會拋出異常

        soup = BeautifulSoup(response.text, 'html.parser')

        # 1. 檢查密碼輸入框
        if soup.find('input', {'type': 'password'}):
            score += SCORE_WEIGHTS["PASSWORD_FIELD"]
            reasons.append("網頁內容包含密碼輸入欄位")

        # 未來可以增加更多內容分析，例如：
        # - 檢查外部連結是否都指向同一個網域
        # - 檢查網站是否有有效的SSL證書 (需要更複雜的庫)
        # - 分析文字內容，尋找詐騙常用語句

    except requests.exceptions.RequestException as e:
        reasons.append(f"無法擷取網頁內容: {e}")
    except Exception as e:
        reasons.append(f"網頁內容分析時發生錯誤: {e}")

    return score, reasons

def main():
    '''主函數'''
    if len(sys.argv) < 2:
        print("用法: python scam_detector.py <要檢測的網址>")
        sys.exit(1)

    url = sys.argv[1]
    print(f"正在分析網址: {url}")

    # 分析URL
    url_score, url_reasons = analyze_url(url)

    # 分析內容
    content_score, content_reasons = analyze_content(url)

    # 計算總分
    total_score = url_score + content_score
    all_reasons = url_reasons + content_reasons

    # 將分數限制在 0-100 之間
    final_score = min(total_score, 100)

    print("\n--- 分析結果 ---")
    print(f"詐騙係數: {final_score} / 100")

    if not all_reasons:
        print("分析完成，未發現明顯可疑特徵。")
    else:
        print("\n發現以下可疑特徵:")
        for reason in all_reasons:
            print(f"- {reason}")

    if final_score >= 70:
        print("\n[警告] 此網站為高度可疑詐騙網站，請勿瀏覽或輸入任何資訊！")
    elif final_score >= 40:
        print("\n[注意] 此網站具有中度風險，請小心謹慎！")
    else:
        print("\n[安全] 此網站風險較低，但仍請保持警覺。")

if __name__ == "__main__":
    main()