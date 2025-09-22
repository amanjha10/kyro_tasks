#!/usr/bin/env python3
"""
Frame Sampling Webhook Implementation Examples
Demonstrates webhook payload creation, validation, and cost optimization
"""

import json
import hmac
import hashlib
import base64
import time
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List


class WebhookPayloadBuilder:
    """Build webhook payloads with cost optimization and security"""
    
    def __init__(self, secret_key: str, system_name: str = "frame-analyzer", version: str = "1.0.0"):
        self.secret_key = secret_key
        self.system_name = system_name
        self.version = version
    
    def create_payload(self, event_type: str, data: Dict[str, Any], 
                      profile: str = "standard", priority: str = "medium") -> Dict[str, Any]:
        """Create a webhook payload with specified profile and priority"""
        
        base_payload = {
            "event": event_type,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "source": {
                "system": self.system_name,
                "version": self.version,
                "instance_id": f"{self.system_name}-{uuid.uuid4().hex[:8]}"
            },
            "data": self._optimize_data_for_profile(data, profile),
            "meta": {
                "request_id": self._generate_request_id(),
                "priority": priority,
                "schema_version": "1.0.0"
            }
        }
        
        # Add signature for security
        base_payload["signature"] = self._generate_signature(base_payload)
        return base_payload
    
    def _optimize_data_for_profile(self, data: Dict[str, Any], profile: str) -> Dict[str, Any]:
        """Optimize data based on cost profile"""
        
        if profile == "minimal":
            # Keep only essential fields
            essential_fields = ["incident_id", "frame_id", "confidence", "session_id"]
            return {k: v for k, v in data.items() if k in essential_fields}
        
        elif profile == "standard":
            # Remove debug and detailed metadata
            excluded_fields = ["debug_info", "raw_frame_data", "processing_metadata"]
            optimized = {k: v for k, v in data.items() if k not in excluded_fields}
            
            # Compress detection details
            if "detection_details" in optimized:
                optimized["detection_details"] = self._compress_detection_details(
                    optimized["detection_details"]
                )
            return optimized
        
        else:  # detailed profile
            return data
    
    def _compress_detection_details(self, details: Dict[str, Any]) -> Dict[str, Any]:
        """Compress detection details to reduce payload size"""
        compressed = {}
        
        if "objects" in details:
            compressed["objects"] = []
            for obj in details["objects"]:
                # Only include high-confidence detections
                if obj.get("confidence", 0) >= 0.7:
                    compressed_obj = {
                        "type": obj["type"],
                        "conf": round(obj["confidence"], 2),
                    }
                    
                    # Compress bounding box to integers
                    if "bounding_box" in obj:
                        bbox = obj["bounding_box"]
                        if isinstance(bbox, dict):
                            compressed_obj["bbox"] = [
                                int(bbox.get("x", 0)), int(bbox.get("y", 0)),
                                int(bbox.get("width", 0)), int(bbox.get("height", 0))
                            ]
                        elif isinstance(bbox, list):
                            compressed_obj["bbox"] = [int(x) for x in bbox]
                    
                    compressed["objects"].append(compressed_obj)
        
        return compressed
    
    def _generate_request_id(self) -> str:
        """Generate unique request ID with timestamp"""
        timestamp = int(time.time() * 1000)
        unique_id = str(uuid.uuid4())[:8]
        return f"req_{timestamp}_{unique_id}"
    
    def _generate_signature(self, payload: Dict[str, Any]) -> str:
        """Generate HMAC-SHA256 signature for payload"""
        # Remove signature field if it exists
        payload_copy = payload.copy()
        payload_copy.pop("signature", None)
        
        payload_bytes = json.dumps(payload_copy, separators=(',', ':')).encode('utf-8')
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            payload_bytes,
            hashlib.sha256
        ).digest()
        return f"sha256={base64.b64encode(signature).decode('utf-8')}"


class WebhookValidator:
    """Validate incoming webhook payloads"""
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.processed_requests = set()  # In production, use Redis/cache
    
    def validate_payload(self, payload: Dict[str, Any], received_signature: str) -> Dict[str, Any]:
        """Validate webhook payload and signature"""
        validation_result = {
            "valid": False,
            "errors": []
        }
        
        # Check required fields
        required_fields = ["event", "timestamp", "source", "data", "meta"]
        for field in required_fields:
            if field not in payload:
                validation_result["errors"].append(f"Missing required field: {field}")
        
        # Validate timestamp (not older than 5 minutes)
        if "timestamp" in payload:
            try:
                timestamp = datetime.fromisoformat(payload["timestamp"].replace('Z', '+00:00'))
                age_seconds = (datetime.now(timestamp.tzinfo) - timestamp).total_seconds()
                if age_seconds > 300:  # 5 minutes
                    validation_result["errors"].append("Timestamp too old")
            except ValueError:
                validation_result["errors"].append("Invalid timestamp format")
        
        # Check for replay attacks
        request_id = payload.get("meta", {}).get("request_id")
        if request_id:
            if request_id in self.processed_requests:
                validation_result["errors"].append("Duplicate request ID (replay attack)")
            else:
                self.processed_requests.add(request_id)
        
        # Verify signature
        if not self._verify_signature(payload, received_signature):
            validation_result["errors"].append("Invalid signature")
        
        validation_result["valid"] = len(validation_result["errors"]) == 0
        return validation_result
    
    def _verify_signature(self, payload: Dict[str, Any], received_signature: str) -> bool:
        """Verify HMAC signature"""
        # Remove signature from payload for verification
        payload_copy = payload.copy()
        payload_copy.pop("signature", None)
        
        expected_signature = self._generate_signature(payload_copy)
        received_sig = received_signature.replace("sha256=", "")
        expected_sig = expected_signature.replace("sha256=", "")
        
        return hmac.compare_digest(expected_sig, received_sig)
    
    def _generate_signature(self, payload: Dict[str, Any]) -> str:
        """Generate signature for comparison"""
        payload_bytes = json.dumps(payload, separators=(',', ':')).encode('utf-8')
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            payload_bytes,
            hashlib.sha256
        ).digest()
        return f"sha256={base64.b64encode(signature).decode('utf-8')}"


# Example usage and testing
if __name__ == "__main__":
    # Initialize webhook builder
    secret_key = "your-webhook-secret-key-here"
    builder = WebhookPayloadBuilder(secret_key)
    
    # Example: Create incident detection payload
    incident_data = {
        "incident_id": "inc_123",
        "frame_id": "frame_456", 
        "confidence": 0.94,
        "detection_details": {
            "objects": [
                {
                    "type": "person",
                    "confidence": 0.94,
                    "bounding_box": {"x": 120.5, "y": 45.2, "width": 180.7, "height": 155.9},
                    "attributes": {"age_estimate": "adult", "clothing_color": "blue"}
                }
            ]
        },
        "debug_info": {"processing_time": 156, "model_version": "v2.1"}
    }
    
    # Create payloads with different profiles
    minimal_payload = builder.create_payload("incident_detected", incident_data, "minimal")
    standard_payload = builder.create_payload("incident_detected", incident_data, "standard") 
    detailed_payload = builder.create_payload("incident_detected", incident_data, "detailed")
    
    print("=== Payload Size Comparison ===")
    print(f"Minimal:  {len(json.dumps(minimal_payload))} bytes")
    print(f"Standard: {len(json.dumps(standard_payload))} bytes") 
    print(f"Detailed: {len(json.dumps(detailed_payload))} bytes")
    
    print("\n=== Standard Payload Example ===")
    print(json.dumps(standard_payload, indent=2))
    
    # Validate payload
    validator = WebhookValidator(secret_key)
    validation_result = validator.validate_payload(
        standard_payload, 
        standard_payload["signature"]
    )
    
    print(f"\n=== Validation Result ===")
    print(f"Valid: {validation_result['valid']}")
    if validation_result['errors']:
        print(f"Errors: {validation_result['errors']}")
