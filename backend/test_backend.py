import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from backend.app.main import app, UrlPayload
from backend.app import model

class BackendTests(unittest.TestCase):
    def test_url_normalization(self):
        self.assertEqual(UrlPayload(url=' Example.COM/path ').url, 'https://example.com/path')
        self.assertEqual(UrlPayload(url='example.com:8443/a').url, 'https://example.com:8443/a')
        self.assertEqual(UrlPayload(url='HTTPS://EXAMPLE.COM').url, 'https://example.com')

    def test_invalid_urls(self):
        for url in ['', 'javascript:alert(1)', 'ftp://example.com', 'https://', 'http://localhost', 'http://127.0.0.1', 'http://[::1]', 'https://user:password@example.com', 'https://foo bar.com', 'https://bad..com', 'https://example.com:99999']:
            with self.subTest(url=url), self.assertRaises(ValueError):
                UrlPayload(url=url)

    def test_no_trust_bypass_for_user_subdomains(self):
        self.assertFalse(model.is_whitelisted_domain('https://attacker.github.com'))
        self.assertFalse(model.is_whitelisted_domain('https://google.com.evil.example'))
        self.assertTrue(model.is_whitelisted_domain('https://www.google.com'))

    def test_missing_domain_not_declared_malicious(self):
        with patch.object(model, 'check_domain_exists', return_value=False), patch.object(model, 'load_model', side_effect=FileNotFoundError):
            result = model.analyze_url('https://ordinary.example')
        self.assertFalse(result['is_malicious'])
        self.assertEqual(result['risk_level'], 'CAUTION')
        self.assertFalse(result['model_available'])

    def test_trusted_domain_keeps_actual_dns_result(self):
        with patch.object(model, 'check_domain_exists', return_value=None):
            result = model.analyze_url('https://www.google.com')
        self.assertIsNone(result['domain_exists'])
        self.assertEqual(result['risk_level'], 'CAUTION')

    def test_keywords_apply_even_on_recognized_domain(self):
        with patch.object(model, 'check_domain_exists', return_value=True):
            result = model.analyze_url('https://google.com/wallet-connect')
        self.assertTrue(result['is_malicious'])

    def test_common_words_do_not_force_phishing(self):
        self.assertFalse(model.contains_high_risk_heuristic('https://example.com/verify-otp'))
        self.assertFalse(model.contains_high_risk_heuristic('https://example.com/article/phishing'))

    def test_api_validation_and_scan(self):
        with TestClient(app) as client:
            self.assertEqual(client.get('/health').status_code, 200)
            self.assertEqual(client.post('/predict', json={'url': 'javascript:alert(1)'}).status_code, 422)
            with patch.object(model, 'check_domain_exists', return_value=True):
                response = client.post('/predict', json={'url': 'google.com'})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()['url'], 'https://google.com')
            self.assertLess(response.json()['risk_score'], 35)

    def test_api_failure_does_not_leak_details(self):
        with TestClient(app) as client, patch('backend.app.main.analyze_url', side_effect=RuntimeError('private path secret')):
            response = client.post('/predict', json={'url': 'example.com'})
        self.assertEqual(response.status_code, 503)
        self.assertNotIn('private path', response.text)

if __name__ == '__main__':
    unittest.main()
