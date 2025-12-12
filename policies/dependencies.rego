# NthLayer Dependencies Policies
#
# Policies for validating Dependencies resources.

package nthlayer.dependencies

import future.keywords.if
import future.keywords.in

# Get all Dependencies resources
dep_resources := [r | some r in input.resources; r.kind == "Dependencies"]

# Warn if critical tier has no dependencies defined
warn[msg] if {
    input.service.tier == "critical"
    count(dep_resources) == 0
    msg := "critical tier services should document dependencies for deploy correlation"
}

# Warn if dependency is missing criticality
warn[msg] if {
    some dep in dep_resources
    some svc in dep.spec.services
    not svc.criticality
    msg := sprintf("service dependency '%s' should specify criticality (high, medium, low)", [svc.name])
}

warn[msg] if {
    some dep in dep_resources
    some db in dep.spec.databases
    not db.criticality
    msg := sprintf("database dependency '%s' should specify criticality (high, medium, low)", [db.name])
}

# Deny if database dependency is missing type
deny[msg] if {
    some dep in dep_resources
    some db in dep.spec.databases
    not db.type
    msg := sprintf("database dependency '%s' must specify type (postgresql, mysql, redis, etc.)", [db.name])
}

# Valid database types
valid_db_types := {
    "postgresql", "postgres", "mysql", "mariadb",
    "redis", "mongodb", "elasticsearch", "cassandra",
    "dynamodb", "rds", "aurora"
}

# Warn if database type is unknown
warn[msg] if {
    some dep in dep_resources
    some db in dep.spec.databases
    db.type
    not db.type in valid_db_types
    msg := sprintf("database dependency '%s' has unknown type '%s'", [db.name, db.type])
}
