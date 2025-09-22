# Webhook Security Implementation Guide

## Overview
This document outlines security best practices and implementation details for the frame sampling webhook system.

## HMAC Signature Validation

### Signature Generation
```python
import hmac
import hashlib
import json
import base64

def generate_signature(payload, secret_key):
    """Generate HMAC-SHA256 signature for webhook payload"""
    payload_bytes = json.dumps(payload, separators=(',', ':')).encode('utf-8')
    signature = hmac.new(
        secret_key.encode('utf-8'),
        payload_bytes,
        hashlib.sha256
    ).digest()
    return base64.b64encode(signature).decode('utf-8')

# Example usage
payload = {
    "event": "incident_detected",
    "timestamp": "2025-09-22T10:16:45.789Z",
    # ... rest of payload
}
secret = "your-webhook-secret-key"
signature = generate_signature(payload, secret)
```

### Signature Verification (Receiver Side)
```python
def verify_signature(payload, received_signature, secret_key):
    """Verify HMAC-SHA256 signature"""
    expected_signature = generate_signature(payload, secret_key)
    return hmac.compare_digest(expected_signature, received_signature)

# Example verification
is_valid = verify_signature(payload, request_signature, secret)
if not is_valid:
    return {"error": "Invalid signature"}, 401
```

## Request ID and Replay Attack Prevention

### Request ID Generation
```python
import uuid
import time

def generate_request_id():
    """Generate unique request ID with timestamp"""
    timestamp = int(time.time() * 1000)  # milliseconds
    unique_id = str(uuid.uuid4())[:8]
    return f"req_{timestamp}_{unique_id}"
```

### Replay Attack Prevention
- Store processed request IDs in cache (Redis/Memcached) with TTL
- Reject requests with duplicate request IDs within time window
- Implement timestamp validation (reject requests older than 5 minutes)

```python
import time
from datetime import datetime, timedelta

def is_request_expired(timestamp_str, max_age_minutes=5):
    """Check if request timestamp is too old"""
    try:
        request_time = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        max_age = timedelta(minutes=max_age_minutes)
        return datetime.now(request_time.tzinfo) - request_time > max_age
    except:
        return True  # Invalid timestamp format
```

## Security Headers and Best Practices

### Required Headers
```
Content-Type: application/json
X-Webhook-Signature: sha256=<base64_encoded_signature>
X-Request-ID: <unique_request_id>
X-Timestamp: <iso8601_timestamp>
User-Agent: FrameSampler-Webhook/1.0
```

### Webhook Endpoint Security
1. **HTTPS Only**: All webhook URLs must use HTTPS
2. **IP Allowlisting**: Restrict webhook sources to known IP ranges
3. **Rate Limiting**: Implement rate limiting per endpoint
4. **Timeout Handling**: Set reasonable timeouts (30 seconds max)

## Secret Management

### Secret Key Requirements
- Minimum 32 characters
- Use cryptographically secure random generation
- Rotate secrets regularly (quarterly recommended)
- Store in secure key management system (AWS KMS, HashiCorp Vault)

### Secret Rotation Process
```python
def rotate_webhook_secret(webhook_id, new_secret):
    """Rotate webhook secret with grace period"""
    # 1. Store new secret alongside old secret
    # 2. Accept both signatures for grace period (24 hours)
    # 3. Remove old secret after grace period
    pass
```

## Error Handling and Logging

### Security Event Logging
```python
import logging

security_logger = logging.getLogger('webhook.security')

def log_security_event(event_type, details):
    """Log security-related events"""
    security_logger.warning(f"Security Event: {event_type}", extra={
        'event_type': event_type,
        'details': details,
        'timestamp': datetime.utcnow().isoformat()
    })

# Examples
log_security_event('invalid_signature', {'request_id': req_id, 'source_ip': ip})
log_security_event('replay_attempt', {'request_id': req_id, 'duplicate_count': 3})
```

### Secure Error Responses
- Never expose internal system details in error messages
- Use generic error messages for security failures
- Log detailed errors internally for debugging

```python
# Good - Generic error response
{"error": "Authentication failed", "code": "AUTH_001"}

# Bad - Exposes internal details  
{"error": "HMAC signature mismatch: expected abc123, got def456"}
```

## Implementation Checklist

- [ ] HMAC-SHA256 signature generation and verification
- [ ] Request ID uniqueness validation
- [ ] Timestamp expiration checking
- [ ] Replay attack prevention with cache
- [ ] HTTPS enforcement
- [ ] Rate limiting implementation
- [ ] Security event logging
- [ ] Secret rotation mechanism
- [ ] IP allowlisting (if applicable)
- [ ] Error handling without information leakage
