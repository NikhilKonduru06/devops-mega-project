from flask import Flask, render_template, request, redirect, url_for
import os
import redis

app = Flask(__name__)

# Redis client - shared storage so all replicas see the same task list
redis_host = os.environ.get("REDIS_HOST", "localhost")
redis_port = int(os.environ.get("REDIS_PORT", 6379))
r = redis.Redis(host=redis_host, port=redis_port, decode_responses=True, socket_connect_timeout=3)

TASKS_KEY = "todo:tasks"


@app.route("/")
def index():
    tasks = r.lrange(TASKS_KEY, 0, -1)
    return render_template("index.html", tasks=tasks)


@app.route("/add", methods=["POST"])
def add_task():
    task = request.form.get("task")
    if task:
        r.rpush(TASKS_KEY, task)
    return redirect(url_for("index"))


@app.route("/delete/<int:task_id>")
def delete_task(task_id):
    tasks = r.lrange(TASKS_KEY, 0, -1)
    if 0 <= task_id < len(tasks):
        # Remove the specific item by value at that index
        r.lset(TASKS_KEY, task_id, "__DELETE__")
        r.lrem(TASKS_KEY, 1, "__DELETE__")
    return redirect(url_for("index"))


@app.route("/health")
def health():
    # Used by Kubernetes liveness/readiness probes
    try:
        r.ping()
        return {"status": "healthy"}, 200
    except Exception:
        return {"status": "unhealthy"}, 503


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
