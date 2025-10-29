from typing import Callable, Optional
import redis
import threading
import queue
import json


class RedisBridge:
    def __init__(
        self,
        host: str,
        port: int,
        db: int,
        events_channel: str,
        responses_channel: str,
        execute_command: Callable[[str, str, str], str | None],
    ):
        self.host = host
        self.port = port
        self.db = db
        self.events_channel = events_channel
        self.responses_channel = responses_channel
        self.execute_command = execute_command

        self.client: Optional[redis.Redis] = None
        self.pubsub = None
        self.listener_thread: Optional[threading.Thread] = None
        self.command_queue: queue.Queue[str] = queue.Queue()
        self.active = False

    def start(self) -> bool:
        if self.active:
            return True
        try:
            self.client = redis.Redis(
                host=self.host, port=self.port, db=self.db, decode_responses=True
            )
            self.client.ping()  # type: ignore
        except redis.RedisError as e:
            print(f"Redis unavailable: {e}")
            self.client = None
            return False
        self.pubsub = self.client.pubsub(ignore_subscribe_messages=True)  # type: ignore
        try:
            self.pubsub.subscribe(self.events_channel)  # type: ignore
        except redis.RedisError as e:
            print(f"Failed to subscribe on Redis channel: {e}")
            self.pubsub = None
            self.client = None
            return False
        self.active = True
        self.listener_thread = threading.Thread(target=self.__listen_loop, daemon=True)
        self.listener_thread.start()
        print("Redis bridge started")
        return True

    def stop(self):
        self.active = False
        if self.pubsub:
            try:
                self.pubsub.close()
            except Exception:
                pass
        self.pubsub = None
        if self.listener_thread and self.listener_thread.is_alive():
            self.listener_thread.join(timeout=1.0)
        self.listener_thread = None
        self.client = None
        self.command_queue = queue.Queue()

    def restart(self) -> bool:
        self.stop()
        return self.start()

    def is_connected(self) -> bool:
        return bool(self.client and self.active)

    def poll(self):
        if not self.client:
            return
        while not self.command_queue.empty():
            command = self.command_queue.get()
            response = self.execute_command(command, "redis", "user")
            payload = json.dumps(
                {"command": command, "message": response}, ensure_ascii=False
            )
            try:
                self.client.publish(self.responses_channel, payload)  # type: ignore
            except redis.RedisError as e:
                print(f"Failed to send response in Redis: {e}")

    def __listen_loop(self):
        if not self.pubsub:
            return
        try:
            for message in self.pubsub.listen():  # type: ignore
                if not self.active:
                    break
                data = message.get("data")  # type: ignore
                if isinstance(data, bytes):
                    data = data.decode("utf-8")
                if isinstance(data, str):
                    self.command_queue.put(data.strip())
        except Exception as e:
            print(f"Error reading from Redis: {e}")
            self.restart()
