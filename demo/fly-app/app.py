"""
Multi-service demo app for NthLayer Gallery
Emits metrics for all 5 demo services with their respective tech stacks
"""

from flask import Flask, Response
from prometheus_client import Counter, Histogram, Gauge, generate_latest, REGISTRY
import random
import time
import os

app = Flask(__name__)

# Basic Auth (same as before)
METRICS_USERNAME = "nthlayer"
METRICS_PASSWORD = os.environ.get("METRICS_PASSWORD", "demo")

def check_auth(username, password):
    return username == METRICS_USERNAME and password == METRICS_PASSWORD

def authenticate():
    return Response(
        'Authentication required', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'}
    )

# =============================================================================
# SERVICE 1: payment-api (PostgreSQL, Redis, Kubernetes)
# =============================================================================

# HTTP metrics
payment_requests = Counter('http_requests_total', 'Total HTTP requests', 
                          ['service', 'method', 'endpoint', 'status'])
payment_duration = Histogram('http_request_duration_seconds', 'Request duration',
                            ['service', 'method', 'endpoint'],
                            buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5])

# PostgreSQL metrics
payment_pg_connections = Gauge('pg_stat_database_numbackends', 'Active connections',
                              ['service', 'datname'])
payment_pg_max_conn = Gauge('pg_settings_max_connections', 'Max connections', ['service'])
payment_pg_blks_hit = Counter('pg_stat_database_blks_hit', 'Buffer cache hits', ['service', 'datname'])
payment_pg_blks_read = Counter('pg_stat_database_blks_read', 'Disk reads', ['service', 'datname'])
payment_pg_query_duration = Histogram('pg_stat_statements_mean_exec_time_seconds', 'Query duration',
                                     ['service'], buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0])

# Redis metrics
payment_cache_hits = Counter('cache_hits_total', 'Cache hits', ['service'])
payment_cache_misses = Counter('cache_misses_total', 'Cache misses', ['service'])

# Kubernetes metrics
payment_pod_status = Gauge('kube_pod_status_phase', 'Pod status', ['service', 'pod', 'phase'])
payment_cpu_usage = Counter('container_cpu_usage_seconds_total', 'CPU usage', ['service', 'pod', 'container'])
payment_memory_usage = Gauge('container_memory_working_set_bytes', 'Memory usage', ['service', 'pod', 'container'])

# =============================================================================
# SERVICE 2: checkout-service (MySQL, RabbitMQ, ECS)
# =============================================================================

checkout_requests = Counter('http_requests_total', 'Total HTTP requests',
                           ['service', 'method', 'endpoint', 'status'])
checkout_duration = Histogram('http_request_duration_seconds', 'Request duration',
                             ['service', 'method', 'endpoint'],
                             buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5])

# MySQL metrics
checkout_mysql_connections = Gauge('mysql_global_status_threads_connected', 'MySQL connections', ['service'])
checkout_mysql_max_conn = Gauge('mysql_global_variables_max_connections', 'Max connections', ['service'])
checkout_mysql_queries = Counter('mysql_global_status_queries_total', 'Total queries', ['service'])

# RabbitMQ metrics
checkout_rabbitmq_messages = Gauge('rabbitmq_queue_messages', 'Messages in queue', ['service', 'queue'])
checkout_rabbitmq_consumers = Gauge('rabbitmq_queue_consumers', 'Active consumers', ['service', 'queue'])
checkout_rabbitmq_published = Counter('rabbitmq_queue_messages_published_total', 'Published messages', ['service', 'queue'])

# ECS metrics
checkout_ecs_tasks = Gauge('ecs_service_running_count', 'Running tasks', ['service', 'cluster'])
checkout_ecs_cpu = Gauge('ecs_task_cpu_utilization', 'CPU utilization %', ['service', 'task'])
checkout_ecs_memory = Gauge('ecs_task_memory_utilization', 'Memory utilization %', ['service', 'task'])

# =============================================================================
# SERVICE 3: notification-worker (Redis, Kafka, Kubernetes - Worker)
# =============================================================================

notif_sent = Counter('notifications_sent_total', 'Notifications sent', ['service', 'status'])
notif_duration = Histogram('notification_processing_duration_seconds', 'Processing duration',
                          ['service'], buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0])
notif_kafka_lag = Gauge('kafka_consumer_lag_seconds', 'Consumer lag', ['service', 'topic'])
notif_kafka_offset = Counter('kafka_consumer_offset_total', 'Consumer offset', ['service', 'topic', 'partition'])

# Redis for notifications
notif_redis_connections = Gauge('redis_connected_clients', 'Connected clients', ['service'])
notif_redis_memory = Gauge('redis_memory_used_bytes', 'Memory used', ['service'])

# Kubernetes metrics for worker
notif_pod_status = Gauge('kube_pod_status_phase', 'Pod status', ['service', 'pod', 'phase'])
notif_cpu_usage = Counter('container_cpu_usage_seconds_total', 'CPU usage', ['service', 'pod', 'container'])
notif_memory_usage = Gauge('container_memory_working_set_bytes', 'Memory usage', ['service', 'pod', 'container'])

# =============================================================================
# SERVICE 4: analytics-stream (MongoDB, Kafka, Kubernetes - Stream Processor)
# =============================================================================

analytics_events = Counter('events_processed_total', 'Events processed', ['service', 'status'])
analytics_duration = Histogram('event_processing_duration_seconds', 'Processing duration',
                              ['service'], buckets=[0.001, 0.01, 0.05, 0.1, 0.5, 1.0])
analytics_throughput = Gauge('stream_throughput_events_per_second', 'Throughput', ['service'])

# MongoDB metrics
analytics_mongo_connections = Gauge('mongodb_connections', 'Active connections', ['service', 'state'])
analytics_mongo_ops = Counter('mongodb_operations_total', 'Operations', ['service', 'type'])
analytics_mongo_query_time = Histogram('mongodb_query_duration_seconds', 'Query duration',
                                       ['service'], buckets=[0.001, 0.01, 0.05, 0.1, 0.5])

# Kafka for analytics
analytics_kafka_lag = Gauge('kafka_consumer_lag_seconds', 'Consumer lag', ['service', 'topic'])
analytics_kafka_throughput = Gauge('kafka_consumer_records_per_second', 'Records/sec', ['service', 'topic'])

# Kubernetes for stream processor
analytics_pod_status = Gauge('kube_pod_status_phase', 'Pod status', ['service', 'pod', 'phase'])
analytics_cpu_usage = Counter('container_cpu_usage_seconds_total', 'CPU usage', ['service', 'pod', 'container'])
analytics_memory_usage = Gauge('container_memory_working_set_bytes', 'Memory usage', ['service', 'pod', 'container'])

# =============================================================================
# SERVICE 5: identity-service (PostgreSQL, Redis, ECS - Auth)
# =============================================================================

identity_requests = Counter('http_requests_total', 'Total HTTP requests',
                           ['service', 'method', 'endpoint', 'status'])
identity_duration = Histogram('http_request_duration_seconds', 'Request duration',
                             ['service', 'method', 'endpoint'],
                             buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0])

# Auth-specific metrics
identity_logins = Counter('login_attempts_total', 'Login attempts', ['service', 'status'])
identity_registrations = Counter('user_registrations_total', 'User registrations', ['service'])
identity_password_resets = Counter('password_reset_total', 'Password resets', ['service'])

# PostgreSQL for identity
identity_pg_connections = Gauge('pg_stat_database_numbackends', 'Active connections',
                               ['service', 'datname'])
identity_pg_max_conn = Gauge('pg_settings_max_connections', 'Max connections', ['service'])

# Redis for sessions
identity_redis_keys = Gauge('redis_db_keys', 'Total keys', ['service', 'db'])
identity_redis_memory = Gauge('redis_memory_used_bytes', 'Memory used', ['service'])

# ECS for identity service
identity_ecs_tasks = Gauge('ecs_service_running_count', 'Running tasks', ['service', 'cluster'])
identity_ecs_cpu = Gauge('ecs_task_cpu_utilization', 'CPU utilization %', ['service', 'task'])

# =============================================================================
# Simulation Functions
# =============================================================================

def simulate_payment_api():
    """Simulate payment-api metrics"""
    # HTTP traffic
    for _ in range(random.randint(5, 15)):
        status = random.choices([200, 201, 400, 500], weights=[85, 10, 3, 2])[0]
        endpoint = random.choice(['/payments', '/checkout', '/refund'])
        duration = random.uniform(0.05, 0.3) if status == 200 else random.uniform(0.5, 2.0)
        
        payment_requests.labels(service='payment-api', method='POST', endpoint=endpoint, status=status).inc()
        payment_duration.labels(service='payment-api', method='POST', endpoint=endpoint).observe(duration)
    
    # PostgreSQL
    payment_pg_connections.labels(service='payment-api', datname='payments').set(random.randint(15, 35))
    payment_pg_max_conn.labels(service='payment-api').set(100)
    payment_pg_blks_hit.labels(service='payment-api', datname='payments').inc(random.randint(1000, 5000))
    payment_pg_blks_read.labels(service='payment-api', datname='payments').inc(random.randint(10, 100))
    payment_pg_query_duration.labels(service='payment-api').observe(random.uniform(0.001, 0.05))
    
    # Redis cache
    payment_cache_hits.labels(service='payment-api').inc(random.randint(80, 120))
    payment_cache_misses.labels(service='payment-api').inc(random.randint(5, 15))
    
    # Kubernetes pods
    for i in range(1, 4):
        pod_name = f'payment-api-{i}'
        payment_pod_status.labels(service='payment-api', pod=pod_name, phase='Running').set(1)
        payment_cpu_usage.labels(service='payment-api', pod=pod_name, container='payment-api').inc(random.uniform(0.01, 0.05))
        payment_memory_usage.labels(service='payment-api', pod=pod_name, container='payment-api').set(random.randint(200_000_000, 400_000_000))

def simulate_checkout_service():
    """Simulate checkout-service metrics"""
    # HTTP traffic
    for _ in range(random.randint(3, 10)):
        status = random.choices([200, 400, 500], weights=[90, 7, 3])[0]
        endpoint = random.choice(['/cart', '/checkout', '/order'])
        duration = random.uniform(0.1, 0.5) if status == 200 else random.uniform(1.0, 3.0)
        
        checkout_requests.labels(service='checkout-service', method='POST', endpoint=endpoint, status=status).inc()
        checkout_duration.labels(service='checkout-service', method='POST', endpoint=endpoint).observe(duration)
    
    # MySQL
    checkout_mysql_connections.labels(service='checkout-service').set(random.randint(10, 25))
    checkout_mysql_max_conn.labels(service='checkout-service').set(150)
    checkout_mysql_queries.labels(service='checkout-service').inc(random.randint(50, 200))
    
    # RabbitMQ
    checkout_rabbitmq_messages.labels(service='checkout-service', queue='order_queue').set(random.randint(0, 50))
    checkout_rabbitmq_consumers.labels(service='checkout-service', queue='order_queue').set(3)
    checkout_rabbitmq_published.labels(service='checkout-service', queue='order_queue').inc(random.randint(5, 20))
    
    # ECS
    checkout_ecs_tasks.labels(service='checkout-service', cluster='production').set(4)
    for i in range(1, 5):
        task_id = f'task-{i}'
        checkout_ecs_cpu.labels(service='checkout-service', task=task_id).set(random.uniform(20, 50))
        checkout_ecs_memory.labels(service='checkout-service', task=task_id).set(random.uniform(30, 60))

def simulate_notification_worker():
    """Simulate notification-worker metrics"""
    # Notifications sent
    for _ in range(random.randint(10, 30)):
        status = random.choices(['delivered', 'failed'], weights=[95, 5])[0]
        notif_sent.labels(service='notification-worker', status=status).inc()
        notif_duration.labels(service='notification-worker').observe(random.uniform(0.5, 3.0))
    
    # Kafka
    notif_kafka_lag.labels(service='notification-worker', topic='notifications').set(random.uniform(0.1, 2.0))
    for partition in range(3):
        notif_kafka_offset.labels(service='notification-worker', topic='notifications', partition=str(partition)).inc(random.randint(10, 50))
    
    # Redis
    notif_redis_connections.labels(service='notification-worker').set(random.randint(5, 15))
    notif_redis_memory.labels(service='notification-worker').set(random.randint(50_000_000, 100_000_000))
    
    # Kubernetes
    for i in range(1, 4):
        pod_name = f'notification-worker-{i}'
        notif_pod_status.labels(service='notification-worker', pod=pod_name, phase='Running').set(1)
        notif_cpu_usage.labels(service='notification-worker', pod=pod_name, container='worker').inc(random.uniform(0.02, 0.08))
        notif_memory_usage.labels(service='notification-worker', pod=pod_name, container='worker').set(random.randint(150_000_000, 300_000_000))

def simulate_analytics_stream():
    """Simulate analytics-stream metrics"""
    # Events processed
    for _ in range(random.randint(20, 50)):
        status = random.choices(['success', 'error'], weights=[98, 2])[0]
        analytics_events.labels(service='analytics-stream', status=status).inc()
        analytics_duration.labels(service='analytics-stream').observe(random.uniform(0.001, 0.05))
    
    analytics_throughput.labels(service='analytics-stream').set(random.uniform(500, 1500))
    
    # MongoDB
    analytics_mongo_connections.labels(service='analytics-stream', state='current').set(random.randint(8, 20))
    analytics_mongo_ops.labels(service='analytics-stream', type='insert').inc(random.randint(50, 200))
    analytics_mongo_query_time.labels(service='analytics-stream').observe(random.uniform(0.005, 0.05))
    
    # Kafka
    analytics_kafka_lag.labels(service='analytics-stream', topic='events').set(random.uniform(0.05, 0.5))
    analytics_kafka_throughput.labels(service='analytics-stream', topic='events').set(random.uniform(800, 1200))
    
    # Kubernetes
    for i in range(1, 5):
        pod_name = f'analytics-stream-{i}'
        analytics_pod_status.labels(service='analytics-stream', pod=pod_name, phase='Running').set(1)
        analytics_cpu_usage.labels(service='analytics-stream', pod=pod_name, container='stream-processor').inc(random.uniform(0.05, 0.15))
        analytics_memory_usage.labels(service='analytics-stream', pod=pod_name, container='stream-processor').set(random.randint(300_000_000, 600_000_000))

def simulate_identity_service():
    """Simulate identity-service metrics"""
    # HTTP traffic
    for _ in range(random.randint(5, 20)):
        status = random.choices([200, 401, 500], weights=[85, 12, 3])[0]
        endpoint = random.choice(['/login', '/register', '/verify'])
        duration = random.uniform(0.05, 0.2) if status == 200 else random.uniform(0.3, 1.0)
        
        identity_requests.labels(service='identity-service', method='POST', endpoint=endpoint, status=status).inc()
        identity_duration.labels(service='identity-service', method='POST', endpoint=endpoint).observe(duration)
    
    # Auth metrics
    identity_logins.labels(service='identity-service', status='success').inc(random.randint(10, 30))
    identity_logins.labels(service='identity-service', status='failed').inc(random.randint(1, 5))
    identity_registrations.labels(service='identity-service').inc(random.randint(0, 3))
    identity_password_resets.labels(service='identity-service').inc(random.randint(0, 2))
    
    # PostgreSQL
    identity_pg_connections.labels(service='identity-service', datname='identity').set(random.randint(10, 20))
    identity_pg_max_conn.labels(service='identity-service').set(100)
    
    # Redis
    identity_redis_keys.labels(service='identity-service', db='0').set(random.randint(1000, 5000))
    identity_redis_memory.labels(service='identity-service').set(random.randint(80_000_000, 150_000_000))
    
    # ECS
    identity_ecs_tasks.labels(service='identity-service', cluster='production').set(3)
    for i in range(1, 4):
        task_id = f'task-{i}'
        identity_ecs_cpu.labels(service='identity-service', task=task_id).set(random.uniform(15, 40))

# =============================================================================
# Flask Routes
# =============================================================================

@app.route('/')
def index():
    return """
    <h1>NthLayer Multi-Service Demo</h1>
    <p>Emitting metrics for 5 services:</p>
    <ul>
        <li><strong>payment-api</strong> - PostgreSQL, Redis, Kubernetes</li>
        <li><strong>checkout-service</strong> - MySQL, RabbitMQ, ECS</li>
        <li><strong>notification-worker</strong> - Redis, Kafka, Kubernetes</li>
        <li><strong>analytics-stream</strong> - MongoDB, Kafka, Kubernetes</li>
        <li><strong>identity-service</strong> - PostgreSQL, Redis, ECS</li>
    </ul>
    <p><a href="/metrics">View Prometheus metrics</a> (requires auth)</p>
    """

@app.route('/health')
def health():
    return {'status': 'healthy', 'services': 5}

@app.route('/metrics')
def metrics():
    from flask import request
    auth = request.authorization
    if not auth or not check_auth(auth.username, auth.password):
        return authenticate()
    
    # Simulate all services
    simulate_payment_api()
    simulate_checkout_service()
    simulate_notification_worker()
    simulate_analytics_stream()
    simulate_identity_service()
    
    return Response(generate_latest(REGISTRY), mimetype='text/plain')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
