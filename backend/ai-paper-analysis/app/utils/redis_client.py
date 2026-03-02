import redis.asyncio as redis
from typing import Optional, Any
import json
from datetime import timedelta

from app.config import settings


class RedisClient:
    """Redis 客户端管理类"""

    _instance: Optional[redis.Redis] = None

    # 任务队列键名
    TASK_QUEUE_KEY = "ai_paper_analysis:task_queue"
    TASK_STATUS_KEY = "ai_paper_analysis:task_status"
    TASK_RESULT_KEY = "ai_paper_analysis:task_result"

    @classmethod
    async def get_instance(cls) -> redis.Redis:
        """获取 Redis 实例（单例模式）"""
        if cls._instance is None:
            cls._instance = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                max_connections=50,
            )
        return cls._instance

    @classmethod
    async def close(cls):
        """关闭 Redis 连接"""
        if cls._instance:
            await cls._instance.close()
            cls._instance = None

    @classmethod
    async def ping(cls) -> bool:
        """测试 Redis 连接"""
        client = await cls.get_instance()
        try:
            await client.ping()
            return True
        except Exception:
            return False


# ============ 任务队列操作 ============

async def enqueue_task(task_id: str, task_data: dict, priority: int = 0) -> bool:
    """
    将任务加入队列

    Args:
        task_id: 任务ID
        task_data: 任务数据
        priority: 优先级（数字越大优先级越高）

    Returns:
        是否成功加入队列
    """
    client = await RedisClient.get_instance()
    task_json = json.dumps({"task_id": task_id, "data": task_data})
    # 使用有序集合实现优先级队列
    await client.zadd(RedisClient.TASK_QUEUE_KEY, {task_json: priority})
    return True


async def dequeue_task() -> Optional[dict]:
    """
    从队列中取出优先级最高的任务

    Returns:
        任务数据或 None
    """
    client = await RedisClient.get_instance()
    # 获取优先级最高的任务（分数最高的）
    result = await client.zpopmax(RedisClient.TASK_QUEUE_KEY)
    if result:
        task_json, _ = result[0]
        return json.loads(task_json)
    return None


async def get_queue_length() -> int:
    """获取队列长度"""
    client = await RedisClient.get_instance()
    return await client.zcard(RedisClient.TASK_QUEUE_KEY)


async def get_task_position(task_id: str) -> int:
    """
    获取任务在队列中的位置

    Args:
        task_id: 任务ID

    Returns:
        位置（从0开始），如果不在队列中返回 -1
    """
    client = await RedisClient.get_instance()
    # 获取队列中所有任务
    tasks = await client.zrange(RedisClient.TASK_QUEUE_KEY, 0, -1, withscores=True)
    for index, (task_json, _) in enumerate(tasks):
        task_data = json.loads(task_json)
        if task_data.get("task_id") == task_id:
            return index
    return -1


# ============ 任务状态操作 ============

async def set_task_status(task_id: str, status: str, ttl: int = 3600) -> bool:
    """
    设置任务状态

    Args:
        task_id: 任务ID
        status: 任务状态
        ttl: 过期时间（秒）

    Returns:
        是否成功
    """
    client = await RedisClient.get_instance()
    key = f"{RedisClient.TASK_STATUS_KEY}:{task_id}"
    await client.set(key, status, ex=ttl)
    return True


async def get_task_status(task_id: str) -> Optional[str]:
    """
    获取任务状态

    Args:
        task_id: 任务ID

    Returns:
        任务状态或 None
    """
    client = await RedisClient.get_instance()
    key = f"{RedisClient.TASK_STATUS_KEY}:{task_id}"
    return await client.get(key)


async def set_task_result(task_id: str, result: dict, ttl: int = 7200) -> bool:
    """
    设置任务结果

    Args:
        task_id: 任务ID
        result: 任务结果
        ttl: 过期时间（秒）

    Returns:
        是否成功
    """
    client = await RedisClient.get_instance()
    key = f"{RedisClient.TASK_RESULT_KEY}:{task_id}"
    await client.set(key, json.dumps(result), ex=ttl)
    return True


async def get_task_result(task_id: str) -> Optional[dict]:
    """
    获取任务结果

    Args:
        task_id: 任务ID

    Returns:
        任务结果或 None
    """
    client = await RedisClient.get_instance()
    key = f"{RedisClient.TASK_RESULT_KEY}:{task_id}"
    result = await client.get(key)
    if result:
        return json.loads(result)
    return None


async def delete_task_cache(task_id: str) -> bool:
    """
    删除任务相关的缓存

    Args:
        task_id: 任务ID

    Returns:
        是否成功
    """
    client = await RedisClient.get_instance()
    keys = [
        f"{RedisClient.TASK_STATUS_KEY}:{task_id}",
        f"{RedisClient.TASK_RESULT_KEY}:{task_id}",
    ]
    await client.delete(*keys)
    return True


# ============ 通用缓存操作 ============

async def set_cache(key: str, value: Any, ttl: int = 3600) -> bool:
    """
    设置缓存

    Args:
        key: 缓存键
        value: 缓存值
        ttl: 过期时间（秒）

    Returns:
        是否成功
    """
    client = await RedisClient.get_instance()
    if isinstance(value, (dict, list)):
        value = json.dumps(value)
    await client.set(key, value, ex=ttl)
    return True


async def get_cache(key: str) -> Optional[Any]:
    """
    获取缓存

    Args:
        key: 缓存键

    Returns:
        缓存值或 None
    """
    client = await RedisClient.get_instance()
    value = await client.get(key)
    if value:
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    return None


async def delete_cache(key: str) -> bool:
    """
    删除缓存

    Args:
        key: 缓存键

    Returns:
        是否成功
    """
    client = await RedisClient.get_instance()
    await client.delete(key)
    return True


async def exists_cache(key: str) -> bool:
    """
    检查缓存是否存在

    Args:
        key: 缓存键

    Returns:
        是否存在
    """
    client = await RedisClient.get_instance()
    return await client.exists(key) > 0


# ============ 便捷方法 ============

async def get_redis() -> redis.Redis:
    """获取 Redis 客户端实例"""
    return await RedisClient.get_instance()


async def init_redis():
    """初始化 Redis 连接"""
    await RedisClient.get_instance()


async def close_redis():
    """关闭 Redis 连接"""
    await RedisClient.close()
