import redis
from django.conf import settings


redis_client = redis.StrictRedis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    decode_responses=True,
)


class RedisQueue:
    def __init__(self, queue_name: str, ttl: int = None):
        self.queue_name = queue_name
        self.ttl = ttl

    def enqueue(self, value: str) -> int:
        """
        큐에 데이터를 추가하는 메서드. 만약 키가 없으면 자동으로 생성된다.
        """
        total_count = redis_client.lpush(
            self.queue_name,
            value,
            self.ttl,
        )
        if self.ttl:
            redis_client.expire(self.queue_name, self.ttl)
        return total_count

    def dequeue(self) -> str:
        """
        큐에서 데이터를 꺼내는 메서드.
        만약 데이터가 없으면 None을 반환.
        """
        return redis_client.rpop(self.queue_name)

    def size(self) -> int:
        """
        큐의 사이즈를 반환하는 메서드
        """
        return redis_client.llen(self.queue_name)

    def get_all(self) -> list:
        """
        큐의 모든 데이터를 반환하는 메서드
        """
        return redis_client.lrange(self.queue_name, 0, -1)
