# NthLayer Service Specification Policies
#
# Default policies for validating service.yaml files.
# Uses Open Policy Agent (OPA) Rego language.
# Run with: conftest test services/*.yaml --policy policies/

package nthlayer.service

import future.keywords.if
import future.keywords.in

# Deny if service section is missing
deny[msg] if {
    not input.service
    msg := "service section is required"
}

# Deny if service name is missing
deny[msg] if {
    input.service
    not input.service.name
    msg := "service.name is required"
}

# Deny if service team is missing
deny[msg] if {
    input.service
    not input.service.team
    msg := "service.team is required"
}

# Deny if service tier is missing
deny[msg] if {
    input.service
    not input.service.tier
    msg := "service.tier is required"
}

# Deny if service type is missing
deny[msg] if {
    input.service
    not input.service.type
    msg := "service.type is required"
}

# Warn if tier is not a known value
warn[msg] if {
    input.service.tier
    valid_tiers := {"critical", "standard", "low", "tier-1", "tier-2", "tier-3"}
    not input.service.tier in valid_tiers
    msg := sprintf("service.tier '%s' is not a standard tier (critical, standard, low)", [input.service.tier])
}

# Warn if type is not a known value
warn[msg] if {
    input.service.type
    valid_types := {"api", "worker", "stream", "web", "batch", "ml"}
    not input.service.type in valid_types
    msg := sprintf("service.type '%s' is not a standard type (api, worker, stream, web, batch, ml)", [input.service.type])
}

# Deny if resources section is missing
deny[msg] if {
    not input.resources
    msg := "resources section is required"
}

# Deny if resources is empty
deny[msg] if {
    input.resources
    count(input.resources) == 0
    msg := "at least one resource must be defined"
}

# Deny if any resource is missing kind
deny[msg] if {
    some resource in input.resources
    not resource.kind
    msg := "every resource must have a 'kind' field"
}

# Warn if critical tier service has no SLO
warn[msg] if {
    input.service.tier == "critical"
    slo_resources := [r | some r in input.resources; r.kind == "SLO"]
    count(slo_resources) == 0
    msg := "critical tier services should have at least one SLO defined"
}

# Warn if critical tier service has no PagerDuty
warn[msg] if {
    input.service.tier == "critical"
    pd_resources := [r | some r in input.resources; r.kind == "PagerDuty"]
    count(pd_resources) == 0
    msg := "critical tier services should have PagerDuty integration"
}
