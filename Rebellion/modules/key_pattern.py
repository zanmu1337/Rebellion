import re

FIREBASE_FIELDS = {
    "apiKey": (
        r'["\']?apiKey["\']?\s*:\s*["\']'
        r'(AIza[0-9A-Za-z_-]{35})["\']'
    ),
    "authDomain": (
        r'["\']?authDomain["\']?\s*:\s*["\']([^"\']+)["\']'
    ),
    "projectId": (
        r'["\']?projectId["\']?\s*:\s*["\']([^"\']+)["\']'
    ),
    "storageBucket": (
        r'["\']?storageBucket["\']?\s*:\s*["\']([^"\']+)["\']'
    ),
    "databaseURL": (
        r'["\']?databaseURL["\']?\s*:\s*["\']([^"\']+)["\']'
    ),
    "messagingSenderId": (
        r'["\']?messagingSenderId["\']?\s*:\s*["\']([^"\']+)["\']'
    ),
    "appId": (
        r'["\']?appId["\']?\s*:\s*["\']([^"\']+)["\']'
    ),
}

PATTERNS = {
    "AWS Key":            r'AKIA[0-9A-Z]{16}',
    "AWS Secret":         r'(?i)aws[_\-\s]{0,20}secret[_\-\s]{0,20}["\']?[=:\s]+["\']?([A-Za-z0-9/+=]{40})',
    "Google API":         r'AIza[0-9A-Za-z\-_]{35}',
    "Stripe Secret":      r'sk_live_[0-9a-zA-Z]{24,}',
    "Stripe Test Secret": r'sk_test_[0-9a-zA-Z]{24,}',
    "Twilio":             r'SK[0-9a-fA-F]{32}',
    "SendGrid":           r'SG\.[a-zA-Z0-9_-]{22,}\.[a-zA-Z0-9_-]{43,}',
    "GitHub Token":       r'ghp_[a-zA-Z0-9]{36}',
    "GitHub OAuth":       r'gho_[a-zA-Z0-9]{36}',
    "GitHub App":         r'(?:ghu|ghs|ghr)_[a-zA-Z0-9]{36}',
    "Slack Token":        r'xox[baprs]-[0-9]{10,}-[0-9]{10,}-[a-zA-Z0-9]{24,}',
    "Slack Webhook":      r'https://hooks\.slack\.com/services/T[A-Z0-9]+/B[A-Z0-9]+/[a-zA-Z0-9]+',
    "Supabase URL":       r'(https?://[a-zA-Z0-9_-]{3,}\.supabase\.co)',
    "Supabase JWT":       r'eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{40,}',
    "Private Key":        r'-----BEGIN (?:RSA |EC |DSA )?PRIVATE KEY-----',
    "Basic Auth URL":     r'https?://[a-zA-Z0-9_-]{3,}:[a-zA-Z0-9_!@#$%^&*]{8,}@[a-zA-Z0-9]',
    "Notion Token":       r'secret_[a-zA-Z0-9]{43,}',
    "Mapbox":             r'pk\.eyJ1[a-zA-Z0-9_\-\.]+\.[a-zA-Z0-9_\-]+',
    "Cloudinary":         r'cloudinary://[0-9]{10,}:[a-zA-Z0-9_\-]{20,}@',
    "Algolia":            r'(?i)algolia[_\-\s]{0,10}([a-zA-Z0-9]{32})',
    "Databricks":         r'dapi[a-zA-Z0-9]{32}',
    "HuggingFace":        r'hf_[a-zA-Z0-9]{37,}',
    "Anthropic":          r'sk-ant-[a-zA-Z0-9_\-]{40,}',
    "OpenAI":             r'sk-[a-zA-Z0-9]{20}T3BlbkFJ[a-zA-Z0-9]{20}',
    "Mailgun":            r'key-[0-9a-zA-Z]{32}',
    "Mailchimp":          r'[0-9a-f]{32}-us[0-9]{1,2}',
    "Shopify":            r'shpss_[a-fA-F0-9]{32}',
    "Shopify Token":      r'shpat_[a-fA-F0-9]{32}',
    "Square":             r'sq0[a-z]{3}-[0-9A-Za-z\-_]{22,43}',
    "Heroku":             r'(?i)heroku[a-z0-9_\-]{0,20}([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})',
    "NPM Token":          r'npm_[a-zA-Z0-9]{36}',
    "GCP Service Acc":    r'"type"\s*:\s*"service_account"',
    "DB Password":        r'(?i)(?:db_pass|db_password|database_password|mysql_pass|postgres_pass|mongo_pass)\s*[=:]\s*["\']?([a-zA-Z0-9_!@#$%^&*\-]{8,})["\']?',
    "Generic Secret":     r'(?i)(?:api_key|api_secret|app_secret|auth_token|client_secret|access_token|secret_key)\s*[=:]\s*["\']([a-zA-Z0-9_\-\.]{20,})["\']',
    "Generic Password":   r'(?i)\bpassword\s*=\s*["\']([a-zA-Z0-9_!@#$%^&*\-]{8,})["\']',
    "Bearer Token":       r'(?i)bearer\s+([a-zA-Z0-9_\-\.]{32,})',
    "HTML to PDF Key":    r'sk_[a-f0-9]{40}',
    "App Password":       r'(?i)app_password\s*[=:]\s*["\']([a-zA-Z0-9 ]{16,})["\']',
    "S3 Bucket":          r'(?:https?:\/\/)?([a-z0-9.\-]{3,63})\.s3(?:[.-][a-z0-9\-]+)?\.amazonaws\.com|(?:https?:\/\/)?s3(?:[.-][a-z0-9\-]+)?\.amazonaws\.com/([a-z0-9.\-]{3,63})|(?:s3://)([a-z0-9.\-]{3,63})',
}

DOMAIN_BLACKLIST = {
    "google.com", "gstatic.com", "googleapis.com", "googletagmanager.com",
    "googleusercontent.com", "googlesyndication.com",
    "cloudflare.com", "cdnjs.cloudflare.com",
    "bing.com", "brave.com", "duckduckgo.com",
    "jquery.com", "bootstrapcdn.com",
    "facebook.com", "fbcdn.net", "instagram.com",
    "twitter.com", "twimg.com",
    "microsoft.com", "msecnd.net", "live.com",
    "amazon.com", "amazonaws.com",
    "apple.com", "icloud.com",
    "youtube.com", "ytimg.com",
    "akamaihd.net", "akamai.net",
    "cloudfront.net",
    "newrelic.com", "nr-data.net",
    "hotjar.com", "segment.com", "mixpanel.com",
    "intercom.io", "intercomcdn.com",
    "sentry.io", "bugsnag.com", "jwt.io",
    "jsdelivr.net", "unpkg.com",
    "fontawesome.com", "typekit.net",
    "recaptcha.net", "grecaptcha.com",
    "stripe.com", "chatgpt.com"
}

FP_BLACKLIST = {
    "password", "passwd", "pwd", "forgot_password", "resetpassword",
    "okta_password", "your_password", "enter_password", "new_password",
    "old_password", "confirm_password", "change_password", "set_password",
    "placeholder", "label", "field", "type", "name", "key", "id",
    "undefined", "null", "true", "false", "none", "empty", "example",
    "test", "demo", "sample", "dummy", "fake", "mock", "default",
    "process.env", "env", "config", "settings", "options", "document",
    "window", "this", "self", "event", "target", "value", "element",
    "node", "object", "function", "class", "module", "exports",
    "your-bucket-name", "bucket-name", "my-bucket", "test-bucket"
}

BRUTEFORCE_TABLES = [
    "users", "user", "admin", "administrators", "accounts", "profiles",
    "user_profiles", "members", "staff", "employees", "config", "settings",
    "api_keys", "tokens", "secrets", "customers", "orders", "transactions",
    "subscriptions", "payments", "clients", "managers", "superusers"
]

def is_fp(val):
    v = val.strip().strip('"\'')
    if not v or len(v) < 6:
        return True
    if v.lower() in FP_BLACKLIST:
        return True
    if re.match(r'^[A-Z_]{3,}$', v):
        return True
    if re.match(r'^[a-z_]+[A-Z][a-z_]+$', v) and len(v) < 20:
        return True
    if v.startswith('%') or v.startswith('{') or v.startswith('<'):
        return True
    if re.search(r'[(){}\[\];,<>!&|]', v):
        return True
    ratio = len(re.findall(r'[a-zA-Z0-9]', v)) / max(len(v), 1)
    if ratio < 0.75:
        return True
    if re.match(r'^process\.env\b', v):
        return True
    return False

def extract_firebase_config(content):
    config = {}
    for field, pattern in FIREBASE_FIELDS.items():
        match = re.search(pattern, content, re.I)
        if match:
            config[field] = match.group(1)
    if "apiKey" not in config or "projectId" not in config:
        return None
    return config