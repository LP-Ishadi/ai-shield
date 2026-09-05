import sys
import os

# Allow importing from the parent project folder
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shield.middleware import calculate_variance, is_suspicious_user_agent


def test_even_timing_has_low_variance():
    """Perfectly evenly-spaced timestamps should produce a very low variance."""
    timestamps = [0.0, 0.5, 1.0, 1.5, 2.0]
    variance = calculate_variance(timestamps)
    assert variance < 0.01


def test_irregular_timing_has_high_variance():
    """Randomly spaced timestamps (like a real human) should produce higher variance."""
    timestamps = [0.0, 0.3, 1.2, 1.35, 3.0]
    variance = calculate_variance(timestamps)
    assert variance > 0.01


def test_single_timestamp_returns_none():
    """With fewer than 2 timestamps, there's no gap to measure, so variance should be None."""
    variance = calculate_variance([1.0])
    assert variance is None


def test_python_requests_user_agent_is_suspicious():
    """The default User-Agent sent by the 'requests' library should be flagged."""
    assert is_suspicious_user_agent("python-requests/2.31.0") is True


def test_curl_user_agent_is_suspicious():
    assert is_suspicious_user_agent("curl/8.4.0") is True


def test_empty_user_agent_is_suspicious():
    assert is_suspicious_user_agent("") is True


def test_real_browser_user_agent_is_not_suspicious():
    """A normal browser User-Agent should NOT be flagged."""
    chrome_ua = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    assert is_suspicious_user_agent(chrome_ua) is False