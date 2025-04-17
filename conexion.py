import redis
r = redis.Redis(
    host='redis-17135.c232.us-east-1-2.ec2.redns.redis-cloud.com',
    port=17135,
    decode_responses=True,
    username="default",
    password="1234",
)