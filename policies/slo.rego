# NthLayer SLO Policies
#
# Policies for validating SLO resources within service.yaml files.

package nthlayer.slo

import future.keywords.if
import future.keywords.in

# Get all SLO resources
slo_resources := [r | some r in input.resources; r.kind == "SLO"]

# Deny if SLO is missing objective
deny[msg] if {
    some slo in slo_resources
    not slo.spec.objective
    name := object.get(slo, "name", "unnamed")
    msg := sprintf("SLO '%s' is missing 'objective' in spec", [name])
}

# Deny if SLO objective is out of range
deny[msg] if {
    some slo in slo_resources
    slo.spec.objective
    slo.spec.objective < 0
    name := object.get(slo, "name", "unnamed")
    msg := sprintf("SLO '%s' objective must be >= 0, got %v", [name, slo.spec.objective])
}

deny[msg] if {
    some slo in slo_resources
    slo.spec.objective
    slo.spec.objective > 100
    name := object.get(slo, "name", "unnamed")
    msg := sprintf("SLO '%s' objective must be <= 100, got %v", [name, slo.spec.objective])
}

# Warn if SLO objective is unrealistically high
warn[msg] if {
    some slo in slo_resources
    slo.spec.objective
    slo.spec.objective > 99.99
    name := object.get(slo, "name", "unnamed")
    msg := sprintf("SLO '%s' has very aggressive objective (%v%%) - consider if achievable", [name, slo.spec.objective])
}

# Warn if SLO is missing window
warn[msg] if {
    some slo in slo_resources
    not slo.spec.window
    name := object.get(slo, "name", "unnamed")
    msg := sprintf("SLO '%s' should specify a window (e.g., 30d)", [name])
}

# Warn if SLO is missing indicator
warn[msg] if {
    some slo in slo_resources
    not slo.spec.indicator
    name := object.get(slo, "name", "unnamed")
    msg := sprintf("SLO '%s' should specify an indicator", [name])
}

# Warn if latency SLO is missing threshold
warn[msg] if {
    some slo in slo_resources
    slo.spec.indicator.type == "latency"
    not slo.spec.indicator.threshold_ms
    name := object.get(slo, "name", "unnamed")
    msg := sprintf("Latency SLO '%s' should specify threshold_ms", [name])
}

# Critical tier SLO checks
warn[msg] if {
    input.service.tier == "critical"
    some slo in slo_resources
    slo.spec.indicator.type == "availability"
    slo.spec.objective < 99.9
    name := object.get(slo, "name", "unnamed")
    msg := sprintf("Critical tier availability SLO '%s' has low objective (%v%%), consider >= 99.9%%", [name, slo.spec.objective])
}
