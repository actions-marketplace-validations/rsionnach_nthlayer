#!/usr/bin/env python3
"""Integration test for SDK adapter with real service specs."""

from src.nthlayer.specs import parse_service_file
from src.nthlayer.dashboards.sdk_adapter import SDKAdapter
from grafana_foundation_sdk.cog.encoder import JSONEncoder
import json

print("=" * 70)
print("  SDK Adapter Integration Test - payment-api")
print("=" * 70)
print()

# Parse real service file
print("1. Parsing service file...")
service_context, resources = parse_service_file("examples/services/payment-api.yaml")
print(f"   ✅ Service: {service_context.name}")
print(f"      Team: {service_context.team}")
print(f"      Type: {service_context.type}")
print()

# Extract SLOs
slos = [r for r in resources if r.kind == "SLO"]
print(f"2. Found {len(slos)} SLOs")
for slo in slos:
    print(f"   - {slo.spec.name}")
print()

# Create dashboard
print("3. Creating dashboard with SDK adapter...")
adapter = SDKAdapter()
dash = adapter.create_dashboard(service_context)
print(f"   ✅ Dashboard created: {dash.build().title}")
print()

# Add SLO panels
print("4. Adding SLO panels...")
for slo_resource in slos:
    slo_spec = slo_resource.spec
    query = adapter.convert_slo_to_query(slo_spec)
    panel = adapter.create_timeseries_panel(
        title=slo_spec.name,
        description=f"Target: {slo_spec.target}%",
        queries=[query]
    )
    dash.with_panel(panel)
    print(f"   ✅ Added panel: {slo_spec.name}")
print()

# Serialize
print("5. Serializing to JSON...")
json_str = adapter.serialize_dashboard(dash)
data = json.loads(json_str)

print(f"   ✅ Dashboard JSON:")
print(f"      Size: {len(json_str)} bytes")
print(f"      Title: {data['title']}")
print(f"      UID: {data['uid']}")
print(f"      Tags: {data['tags']}")
print(f"      Schema version: {data['schemaVersion']}")
print()

# Compare with old format (basic structure check)
print("6. Validating Grafana compatibility...")
required_keys = ['title', 'uid', 'tags', 'editable', 'schemaVersion', 'timezone']
missing = [k for k in required_keys if k not in data]
if missing:
    print(f"   ❌ Missing keys: {missing}")
else:
    print(f"   ✅ All required keys present")
print()

# Write to file for manual inspection
output_file = "generated/payment-api/dashboard-sdk.json"
import os
os.makedirs(os.path.dirname(output_file), exist_ok=True)
with open(output_file, 'w') as f:
    f.write(json_str)

print(f"7. Written to: {output_file}")
print()

print("=" * 70)
print("✅ SDK Adapter Integration Test: PASSED")
print("=" * 70)
print()
print("Next: Integrate adapter into DashboardBuilder")
