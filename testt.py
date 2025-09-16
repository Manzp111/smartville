import redis

r = redis.Redis(
    host="redis-15260.c279.us-central1-1.gce.redns.redis-cloud.com",
    port=15260,
    username="default",
    password="dKBe9IKNGupqrZVs8jsXe3cx0UuWLMak",
    ssl=True,
    ssl_cert_reqs=None  # disables certificate verification for testing
)

# Test set/get
r.set("hello", "world")
print(r.get("hello"))  # should print b'world'
