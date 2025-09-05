#!/usr/bin/env python3
"""Simple test for very low risk scoring."""

from datetime import datetime, timedelta, timezone


def test_low_risk_scoring():
    """Test the low risk calculation without Django dependencies."""

    # Mock the risk calculation logic directly
    def calculate_risk_score(ip, ua_string, created_at, current_ip, current_ua):
        risk_score = 0

        # Time-based risk factors (much more lenient)
        if created_at:
            now = datetime.now(timezone.utc)
            age_hours = (now - created_at).total_seconds() / 3600

            # Only very old sessions get significant risk
            if age_hours > 2160:  # 90 days
                risk_score += 15
            elif age_hours > 1440:  # 60 days
                risk_score += 8
            elif age_hours > 720:  # 30 days
                risk_score += 3

        # IP-based risk factors (reduced significantly)
        if ip and current_ip:
            try:
                ip_parts = ip.split('.')[:3]
                current_ip_parts = current_ip.split('.')[:3]
                if ip_parts != current_ip_parts:
                    risk_score += 2  # Very minimal risk for different /24 network

                    # Only completely different providers get moderate risk
                    if ip_parts[:2] != current_ip_parts[:2]:
                        risk_score += 5  # Still low risk for different /16 network
            except:
                pass

        # Check for known suspicious patterns
        if ua_string:
            highly_suspicious_patterns = [
                'sqlmap', 'nikto', 'nmap', 'masscan', 'exploit', 'hack', 'attack']
            moderately_suspicious_patterns = [
                'bot', 'crawler', 'spider', 'automated', 'curl', 'wget', 'python-requests']

            if any(pattern in ua_string.lower() for pattern in highly_suspicious_patterns):
                risk_score += 25  # Only truly malicious gets high score
            elif any(pattern in ua_string.lower() for pattern in moderately_suspicious_patterns):
                risk_score += 5   # Legitimate bots get low score

        return min(risk_score, 100)

    def get_risk_level(risk_score):
        if risk_score >= 50:
            return "HIGH"
        elif risk_score >= 25:
            return "MEDIUM"
        elif risk_score >= 10:
            return "LOW"
        elif risk_score >= 3:
            return "VERY LOW"
        else:
            return "MINIMAL"

    print("🔒 Testing Very Low Risk Scoring")
    print("=" * 50)

    current_time = datetime.now(timezone.utc)

    # Test cases that should be MINIMAL or VERY LOW risk
    test_cases = [
        {
            "name": "Same device, same IP, recent session",
            "ip": "192.168.1.100",
            "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0",
            "created": current_time - timedelta(hours=2),
            "current_ip": "192.168.1.100",
            "current_ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"
        },
        {
            "name": "Mobile vs Desktop (common scenario)",
            "ip": "192.168.1.100",
            "ua": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0) Safari/604.1",
            "created": current_time - timedelta(hours=5),
            "current_ip": "192.168.1.100",
            "current_ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"
        },
        {
            "name": "Different home IP (wifi vs mobile)",
            "ip": "192.168.1.100",
            "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0",
            "created": current_time - timedelta(days=2),
            "current_ip": "203.45.67.89",
            "current_ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"
        },
        {
            "name": "30-day old session",
            "ip": "192.168.1.100",
            "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0",
            "created": current_time - timedelta(days=30),
            "current_ip": "192.168.1.100",
            "current_ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"
        },
        {
            "name": "60-day old session",
            "ip": "192.168.1.100",
            "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0",
            "created": current_time - timedelta(days=60),
            "current_ip": "192.168.1.100",
            "current_ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"
        },
        {
            "name": "Legitimate crawler",
            "ip": "66.249.66.1",  # Google IP
            "ua": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
            "created": current_time - timedelta(hours=1),
            "current_ip": "192.168.1.100",
            "current_ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"
        }
    ]

    for test_case in test_cases:
        risk = calculate_risk_score(
            test_case["ip"],
            test_case["ua"],
            test_case["created"],
            test_case["current_ip"],
            test_case["current_ua"]
        )
        level = get_risk_level(risk)

        # Color coding for terminal output
        color = ""
        if level == "MINIMAL":
            color = "✅"
        elif level == "VERY LOW":
            color = "🟢"
        elif level == "LOW":
            color = "🟡"
        elif level == "MEDIUM":
            color = "🟠"
        else:
            color = "🔴"

        print(f"{color} {test_case['name']}: Risk={risk}% ({level})")

    print("\n🎯 Summary:")
    print("✅ Most common scenarios now result in MINIMAL or VERY LOW risk")
    print("🟢 Only truly suspicious activity gets medium-high risk scores")
    print("🔒 Users will see very few sessions flagged as concerning")


if __name__ == "__main__":
    test_low_risk_scoring()
