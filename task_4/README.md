# Frame Sampling Webhook Payload Structure

## Overview
This repository contains the complete webhook payload structure design for a frame sampling and incident detection system. The design balances accuracy vs. cost while ensuring extensibility and security.

## 🎯 Key Features
- **Cost-Optimized**: Multiple payload profiles to balance accuracy and cost
- **Secure**: HMAC signature validation and replay attack prevention
- **Extensible**: Version-aware schema that supports future enhancements
- **Flexible**: Configurable detail levels and adaptive payload sizing

## 📋 Repository Contents

### Core Schema Files
- [`webhook-payload-schema.json`](webhook-payload-schema.json) - JSON Schema definition
- [`event-types-examples.json`](event-types-examples.json) - Event type definitions and examples

### Documentation
- [`webhook-security-guide.md`](webhook-security-guide.md) - Security implementation guide
- [`extensibility-framework.md`](extensibility-framework.md) - Versioning and extensibility strategy
- [`cost-optimization-strategy.md`](cost-optimization-strategy.md) - Cost optimization techniques

## 🚀 Quick Start

### Basic Webhook Payload Structure
```json
{
  "event": "incident_detected",
  "timestamp": "2025-09-22T10:16:45.789Z",
  "source": {
    "system": "incident-detector",
    "version": "2.1.3",
    "instance_id": "id-prod-02"
  },
  "data": {
    "incident_id": "inc_def456",
    "confidence": 0.94,
    "detection_details": {
      "objects": [
        {
          "type": "person",
          "confidence": 0.94,
          "bounding_box": {"x": 120, "y": 45, "width": 180, "height": 155}
        }
      ]
    }
  },
  "meta": {
    "request_id": "req_67890",
    "priority": "high",
    "schema_version": "1.0.0"
  },
  "signature": "sha256=b2c3d4e5f6g7..."
}
```

### Supported Event Types
- `frame_sampled` - Frame successfully extracted from video
- `incident_detected` - Anomaly or incident detected in frame
- `processing_completed` - Video processing session finished
- `processing_failed` - Processing encountered an error
- `alert_triggered` - Alert condition met
- `system_health_check` - System status update

## 💰 Cost Optimization

### Payload Profiles
Choose the right profile for your use case:

| Profile | Size | Cost Factor | Use Case |
|---------|------|-------------|----------|
| **Minimal** | ~512 bytes | 0.1x | High-volume alerts, cost-sensitive |
| **Standard** | ~2KB | 0.5x | General monitoring, balanced approach |
| **Detailed** | ~8KB | 1.0x | Debugging, full analysis |

### Example: Minimal Profile
```json
{
  "event": "incident_detected",
  "timestamp": "2025-09-22T10:16:45Z",
  "data": {
    "incident_id": "inc_123",
    "confidence": 0.94
  },
  "meta": {
    "request_id": "req_456"
  }
}
```

## 🔒 Security Implementation

### HMAC Signature Validation
```python
import hmac
import hashlib
import json
import base64

def generate_signature(payload, secret_key):
    payload_bytes = json.dumps(payload, separators=(',', ':')).encode('utf-8')
    signature = hmac.new(
        secret_key.encode('utf-8'),
        payload_bytes,
        hashlib.sha256
    ).digest()
    return base64.b64encode(signature).decode('utf-8')
```

### Required Security Headers
```
Content-Type: application/json
X-Webhook-Signature: sha256=<base64_encoded_signature>
X-Request-ID: <unique_request_id>
X-Timestamp: <iso8601_timestamp>
```

## 🔄 Extensibility

### Schema Versioning
- **Semantic Versioning**: MAJOR.MINOR.PATCH
- **Backward Compatibility**: Minor versions are backward compatible
- **Migration Support**: Clear upgrade paths for major versions

### Adding New Fields (Safe)
```json
{
  "data": {
    "frame_id": "frame_123",
    "confidence": 0.95,
    "new_optional_field": {  // Safe to add
      "additional_data": "value"
    }
  }
}
```

## 📊 Integration Examples

### Webhook Receiver Implementation
```python
from flask import Flask, request, jsonify
import hmac
import json

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    # Verify signature
    signature = request.headers.get('X-Webhook-Signature', '').replace('sha256=', '')
    if not verify_signature(request.data, signature, WEBHOOK_SECRET):
        return jsonify({'error': 'Invalid signature'}), 401
    
    # Process payload
    payload = request.json
    event_type = payload.get('event')
    
    if event_type == 'incident_detected':
        handle_incident(payload['data'])
    elif event_type == 'frame_sampled':
        handle_frame_sample(payload['data'])
    
    return jsonify({'status': 'success'}), 200
```

### Configuration Example
```json
{
  "webhook_config": {
    "url": "https://your-app.com/webhook",
    "secret": "your-webhook-secret",
    "profile": "standard",
    "events": ["incident_detected", "processing_completed"],
    "retry_policy": {
      "max_retries": 3,
      "backoff_seconds": [1, 5, 15]
    }
  }
}
```

## 🧪 Testing

### Webhook Testing Tool
```bash
# Test webhook endpoint
curl -X POST https://your-app.com/webhook \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Signature: sha256=signature_here" \
  -H "X-Request-ID: test_req_123" \
  -d @test-payload.json
```

### Validation Checklist
- [ ] Signature verification works
- [ ] Request ID uniqueness enforced
- [ ] Timestamp validation implemented
- [ ] Error handling for malformed payloads
- [ ] Rate limiting configured
- [ ] Logging and monitoring in place

## 📈 Monitoring and Analytics

### Key Metrics to Track
- Webhook delivery success rate
- Average payload size
- Processing latency
- Cost per webhook
- Error rates by event type

### Cost Monitoring
```python
def track_webhook_cost(payload_size_bytes, event_type):
    cost = (payload_size_bytes / 1024) * COST_PER_KB
    metrics.increment(f'webhook.cost.{event_type}', cost)
    metrics.histogram('webhook.payload_size', payload_size_bytes)
```

## 🤝 Contributing

1. Follow the extensibility guidelines for schema changes
2. Update documentation for any new event types
3. Include security considerations in all changes
4. Test cost impact of payload modifications

## 🛠️ Implementation Examples

### Python SDK Example
```python
class FrameSamplingWebhook:
    def __init__(self, secret_key, profile='standard'):
        self.secret_key = secret_key
        self.profile = profile

    def create_payload(self, event_type, data):
        payload = {
            'event': event_type,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'source': {
                'system': 'frame-analyzer',
                'version': '1.0.0'
            },
            'data': self._optimize_data(data),
            'meta': {
                'request_id': self._generate_request_id(),
                'schema_version': '1.0.0'
            }
        }
        payload['signature'] = self._generate_signature(payload)
        return payload
```

### Node.js Integration
```javascript
const crypto = require('crypto');

class WebhookSender {
    constructor(secretKey) {
        this.secretKey = secretKey;
    }

    generateSignature(payload) {
        const payloadString = JSON.stringify(payload);
        return crypto
            .createHmac('sha256', this.secretKey)
            .update(payloadString)
            .digest('base64');
    }

    async sendWebhook(url, payload) {
        payload.signature = `sha256=${this.generateSignature(payload)}`;

        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Webhook-Signature': payload.signature,
                'X-Request-ID': payload.meta.request_id
            },
            body: JSON.stringify(payload)
        });

        return response;
    }
}
```

## 📄 License

This webhook payload structure design is provided as a reference implementation. Adapt according to your specific requirements and security policies.
