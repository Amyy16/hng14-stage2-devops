import redis
import time
import os
import signal


running = True


def handle_shutdown(signum, frame):
    global running
    running = False


signal.signal(signal.SIGTERM, handle_shutdown)
signal.signal(signal.SIGINT, handle_shutdown)

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

try:
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    r.ping()
except redis.exceptions.ConnectionError as error:
    raise RuntimeError(f"Could not connect to Redis {error}")


def process_job(job_id):
    print(f"Processing job {job_id}")
    time.sleep(2)  # simulate work
    r.hset(f"job:{job_id}", "status", "completed")
    print(f"Done: {job_id}")


while running:
    try:
        job = r.brpop("job", timeout=5)
        if job:
            _, job_id = job
            process_job(job_id)
    except redis.exceptions.ConnectionError as e:
        print(f"Redis connection lost: {e}. Retrying in 5s...")
        time.sleep(5)  # wait and try again
