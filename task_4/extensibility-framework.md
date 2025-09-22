# Webhook Extensibility Framework

## Overview
This framework ensures webhook payloads can evolve over time without breaking existing integrations.

## Versioning Strategy

### Schema Versioning
- **Semantic Versioning**: Use MAJOR.MINOR.PATCH format
- **MAJOR**: Breaking changes (field removal, type changes)
- **MINOR**: Backward-compatible additions (new fields, new event types)
- **PATCH**: Bug fixes, documentation updates

### Version Header
```json
{
  "meta": {
    "schema_version": "1.2.0"
  }
}
```

### Version Compatibility Matrix
| Schema Version | Compatible Receivers | Breaking Changes |
|----------------|---------------------|------------------|
| 1.0.0          | All                 | Initial release  |
| 1.1.0          | 1.0.0+             | Added cost_metrics |
| 1.2.0          | 1.0.0+             | Added sampling_strategy.parameters |
| 2.0.0          | 2.0.0+             | Removed deprecated fields |

## Backward Compatibility Rules

### Safe Changes (Minor Version)
✅ **Allowed**:
- Adding new optional fields
- Adding new event types
- Adding new enum values
- Expanding field descriptions
- Adding new meta fields

### Breaking Changes (Major Version)
❌ **Requires Major Version Bump**:
- Removing existing fields
- Changing field types
- Making optional fields required
- Removing enum values
- Changing field names

### Example: Adding New Field (Safe)
```json
// Version 1.0.0
{
  "data": {
    "frame_id": "frame_123",
    "confidence": 0.95
  }
}

// Version 1.1.0 - Added processing_metadata (safe)
{
  "data": {
    "frame_id": "frame_123", 
    "confidence": 0.95,
    "processing_metadata": {  // New optional field
      "algorithm": "yolo_v8",
      "model_version": "2.1.0"
    }
  }
}
```

## Extensible Data Structure

### Flexible Event Data
Use nested objects for event-specific data:

```json
{
  "data": {
    // Common fields for all events
    "session_id": "sess_123",
    "video_id": "vid_456",
    
    // Event-specific data in nested objects
    "frame_data": {
      "frame_id": "frame_789",
      "timestamp_in_video": 15.5
    },
    
    "detection_data": {
      "objects": [...],
      "confidence": 0.95
    },
    
    // Future extensions can add new nested objects
    "ml_insights": {
      "model_predictions": [...],
      "feature_vectors": [...]
    }
  }
}
```

### Custom Extensions
Allow custom fields with reserved namespace:

```json
{
  "data": {
    // Standard fields
    "frame_id": "frame_123",
    
    // Custom extensions (prefixed with x_)
    "x_customer_metadata": {
      "department": "security",
      "location": "building_a"
    },
    
    "x_integration_data": {
      "external_system_id": "ext_789",
      "workflow_step": 3
    }
  }
}
```

## Event Type Evolution

### Adding New Event Types
```json
// Current event types
"enum": [
  "frame_sampled",
  "incident_detected", 
  "processing_completed"
]

// Extended event types (v1.1.0)
"enum": [
  "frame_sampled",
  "incident_detected", 
  "processing_completed",
  "quality_check_failed",    // New
  "batch_processing_started", // New
  "system_maintenance"       // New
]
```

### Event Type Deprecation Process
1. **Deprecation Notice**: Mark event type as deprecated in documentation
2. **Grace Period**: Continue supporting for 6 months minimum
3. **Migration Guide**: Provide clear migration path
4. **Removal**: Remove in next major version

## Configuration-Driven Payloads

### Payload Profiles
Allow receivers to configure payload detail levels:

```json
{
  "webhook_config": {
    "profile": "minimal",  // minimal, standard, detailed
    "include_fields": [
      "event",
      "timestamp", 
      "data.frame_id",
      "data.confidence"
    ],
    "exclude_fields": [
      "data.cost_metrics",
      "data.processing_metadata"
    ]
  }
}
```

### Profile Examples
```json
// Minimal Profile (cost-optimized)
{
  "event": "incident_detected",
  "timestamp": "2025-09-22T10:16:45Z",
  "data": {
    "incident_id": "inc_123",
    "confidence": 0.94
  }
}

// Standard Profile (default)
{
  "event": "incident_detected", 
  "timestamp": "2025-09-22T10:16:45Z",
  "source": {...},
  "data": {
    "incident_id": "inc_123",
    "confidence": 0.94,
    "detection_details": {...}
  },
  "meta": {...}
}

// Detailed Profile (full data)
{
  "event": "incident_detected",
  "timestamp": "2025-09-22T10:16:45Z", 
  "source": {...},
  "data": {
    "incident_id": "inc_123",
    "confidence": 0.94,
    "detection_details": {...},
    "cost_metrics": {...},
    "processing_metadata": {...},
    "debug_info": {...}
  },
  "meta": {...}
}
```

## Migration Guidelines

### Version Migration Process
1. **Announce**: Notify all webhook consumers 30 days before release
2. **Test**: Provide test endpoints with new schema
3. **Deploy**: Release with backward compatibility
4. **Monitor**: Track adoption and error rates
5. **Deprecate**: Remove old version after grace period

### Consumer Implementation
```python
def handle_webhook(payload):
    """Handle webhook with version compatibility"""
    schema_version = payload.get('meta', {}).get('schema_version', '1.0.0')
    
    if schema_version.startswith('1.'):
        return handle_v1_payload(payload)
    elif schema_version.startswith('2.'):
        return handle_v2_payload(payload)
    else:
        logger.warning(f"Unsupported schema version: {schema_version}")
        return handle_fallback(payload)
```

## Future-Proofing Checklist

- [ ] Schema version included in all payloads
- [ ] Optional fields used for new additions
- [ ] Nested objects for logical grouping
- [ ] Reserved namespace for custom extensions
- [ ] Configuration-driven payload profiles
- [ ] Clear deprecation process documented
- [ ] Migration guides for breaking changes
- [ ] Version compatibility testing
- [ ] Consumer SDK with version handling
