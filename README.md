# Scam\_LLM

## Project Overview

Taiwan has been named by BBC as the **world’s number one hotspot for scams**. On average, scams cause **NTD 250 million (≈ USD 7.7 million) in losses per day**, including:

* Online shopping fraud: **NTD 6.38 million**
* Fake investment fraud: **NTD 130 million**
* Other phishing-related losses: hundreds of millions more

A large proportion of these financial damages are caused by **phishing websites**.
This project focuses on **detecting scam websites** by analyzing both the **URL structure** and the **HTML content**, rather than just checking source code.

---

## Features

* **URL Analysis**

  * Whitelist and blacklist checks
  * Suspicious TLD detection (`.xyz`, `.top`, `.club`, etc.)
  * Typosquatting detection (domains mimicking popular websites)
  * Suspicious keyword checks (`login`, `secure`, `verify`, etc.)
  * URL length and `@` symbol inspection

* **HTML Content Analysis**

  * Detects presence of password input fields
  * Future extension: SSL certificate checks, scam-related text detection, suspicious external links

* **Risk Scoring (0–100)**

  * **70+** → High risk (likely phishing) ⚠️
  * **40–69** → Medium risk (exercise caution) ⚠️
  * **0–39** → Low risk (relatively safe, but stay alert) ✅

---

## Installation

```bash
pip install requests beautifulsoup4 python-Levenshtein
```

---

## Usage

```bash
python scam_detector.py <URL>
```

**Example:**

```bash
python scam_detector.py https://mvdlstw.net
```

The output will include:

* Scam risk score
* List of detected suspicious features
* Final classification: **Safe / Caution / Warning**

---

## Conclusion

This project demonstrates a basic **website scam detector**. Its core principle is **analyzing URL and HTML patterns**, not just relying on a static blacklist.

Future directions include:

* Validating SSL/TLS certificates
* Detecting scam-related keywords in webpage text
* Checking external links for safety

The goal is to help users quickly identify phishing websites and reduce financial damages caused by online scams.
