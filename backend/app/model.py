import ipaddress
import logging
import os
import re
from functools import lru_cache
from urllib.parse import unquote, urlparse

import dns.resolver
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import FeatureUnion, Pipeline

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'rf_model.joblib')
logger = logging.getLogger(__name__)
TRUSTED_DOMAINS = {'wikipedia.org', 'google.com', 'github.com', 'youtube.com', 'microsoft.com', 'apple.com', 'amazon.com', 'stackoverflow.com', 'linkedin.com', 'reddit.com', 'python.org', 'mozilla.org', 'cloudflare.com', 'bbc.com', 'reuters.com'}
HIGH_RISK_KEYWORDS = ['secure-login', 'bank-login', 'account-update', 'paypal-security', 'wallet-connect', 'claim-bonus', 'free-robux', 'bypass-otp', 'login-verify', 'recover-account', 'hack-otp']


def check_domain_exists(hostname):
    """True for DNS records, False for NXDOMAIN, None for inconclusive lookups."""
    try:
        ipaddress.ip_address(hostname)
        return True
    except ValueError:
        pass
    resolver = dns.resolver.Resolver()
    resolver.timeout = 1.5
    resolver.lifetime = 2.5
    try:
        resolver.resolve(hostname, 'A')
        return True
    except dns.resolver.NXDOMAIN:
        return False
    except dns.resolver.NoAnswer:
        try:
            resolver.resolve(hostname, 'AAAA')
            return True
        except dns.resolver.NXDOMAIN:
            return False
        except (dns.exception.DNSException, OSError):
            return None
    except (dns.exception.DNSException, OSError):
        return None


def is_whitelisted_domain(url):
    host = (urlparse(url).hostname or '').lower().rstrip('.')
    # User-hosted subdomains are not automatically trusted.
    return host in TRUSTED_DOMAINS or (host.startswith('www.') and host[4:] in TRUSTED_DOMAINS)


def contains_high_risk_heuristic(url):
    decoded = unquote(url).lower()
    return any(keyword in decoded for keyword in HIGH_RISK_KEYWORDS)


def generate_benign_urls():
    return ['https://' + domain + path for domain in sorted(TRUSTED_DOMAINS) for path in ['', '/', '/about', '/login', '/docs', '/privacy', '/search', '/contact']]


def generate_synthetic_phishing_urls():
    return ['https://hack-otp-verify.net', 'http://verify-bank-otp.com', 'https://paypal-security.example/login', 'https://wallet-connect-airdrop.xyz', 'http://bypass-otp-auth.com']


def train_model(csv_path):
    frame = pd.read_csv(csv_path)
    malicious = frame['url'].dropna().astype(str).tolist() + generate_synthetic_phishing_urls()
    benign = generate_benign_urls()
    pipeline = Pipeline([
        ('features', FeatureUnion([
            ('char_tfidf', TfidfVectorizer(analyzer='char', ngram_range=(3, 5), sublinear_tf=True)),
            ('word_tfidf', TfidfVectorizer(token_pattern=r'(?u)\b\w+\b', ngram_range=(1, 2), sublinear_tf=True)),
        ])),
        ('rf', RandomForestClassifier(n_estimators=300, max_depth=25, random_state=42, n_jobs=-1)),
    ])
    pipeline.fit(malicious + benign, [1] * len(malicious) + [0] * len(benign))
    joblib.dump(pipeline, MODEL_PATH)
    load_model.cache_clear()


@lru_cache(maxsize=1)
def load_model():
    return joblib.load(MODEL_PATH)


def analyze_url(url):
    exists = check_domain_exists(urlparse(url).hostname)
    trusted = is_whitelisted_domain(url)
    heuristic = contains_high_risk_heuristic(url)
    reasons = []
    score = 10
    available = True
    try:
        model = load_model()
        classes = list(model.classes_)
        probability = float(model.predict_proba([url])[0][classes.index(1)])
        score = round(probability * 100)
    except Exception:
        available = False
        probability = None
        reasons.append('AI model is unavailable; this result uses URL and DNS checks only.')
    if trusted and not heuristic:
        score = min(score, 15)
        reasons.append('The hostname matches a recognized domain; this does not verify the page content.')
    elif probability is not None and probability >= 0.65:
        reasons.append('The model detected URL patterns associated with phishing.')
    if heuristic:
        score = max(score, 85)
        reasons.append('The URL contains a combination of terms often used in phishing links.')
    if exists is False:
        score = max(score, 50)
        reasons.append('The domain was not found in DNS. A missing domain alone does not prove fraud.')
    elif exists is None:
        score = max(score, 40)
        reasons.append('DNS could not be verified. Check your connection or try again later.')
    if not available:
        score = max(score, 40)
    malicious = score >= 65
    level = 'HIGH RISK' if malicious else ('CAUTION' if score >= 35 else 'LOW RISK')
    if not reasons:
        reasons.append('No strong warning signals were found in the URL and DNS checks.')
    return {'is_malicious': malicious, 'domain_exists': exists, 'risk_score': score, 'risk_level': level, 'reason': ' | '.join(reasons), 'model_available': available}
