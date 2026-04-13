"""
简单用户 API 服务：登录、用户 CRUD，数据存于内存。
用于 api-automation 测试演示。
"""

import os
import uuid
from functools import wraps

from flask import Flask, request, jsonify

app = Flask(__name__)
app.config["SECRET_KEY"] = "demo-secret"

# 内存存储
USERS: dict[str, dict] = {}
TOKENS: dict[str, str] = {}  # token -> user_id


def _init_demo_users():
    """初始化演示用户"""
    if not USERS:
        for uid, u in [
            ("1", {"username": "admin", "password": "admin123", "email": "admin@demo.com"}),
            ("2", {"username": "test", "password": "test123", "email": "test@demo.com"}),
        ]:
            USERS[uid] = {
                "id": uid,
                "username": u["username"],
                "password": u["password"],
                "email": u["email"],
            }


def _require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get("Authorization")
        if not auth or not auth.startswith("Bearer "):
            return jsonify({"code": 401, "msg": "未授权", "data": None}), 401
        token = auth[7:]
        user_id = TOKENS.get(token)
        if not user_id or user_id not in USERS:
            return jsonify({"code": 401, "msg": "token 无效", "data": None}), 401
        request.current_user_id = user_id
        return f(*args, **kwargs)
    return decorated


def _resp(code=200, msg="success", data=None):
    return jsonify({"code": code, "msg": msg, "data": data})


# 模块加载时即初始化演示用户，任意启动方式（python app.py / flask run / gunicorn）均可登录
_init_demo_users()


@app.route("/auth/login", methods=["POST"])
def login():
    """用户登录"""
    body = request.get_json() or {}
    username = (body.get("username") or "").strip()
    password = (body.get("password") or "").strip()
    if not username or not password:
        return _resp(400, "用户名和密码必填"), 400
    for uid, u in USERS.items():
        if u["username"] == username and u["password"] == password:
            token = str(uuid.uuid4())
            TOKENS[token] = uid
            return _resp(200, "success", {"token": token, "userId": uid})
    return _resp(401, "用户名或密码错误"), 401


@app.route("/api/v1/user", methods=["GET"])
@_require_auth
def get_current_user():
    """获取当前登录用户信息"""
    u = USERS.get(request.current_user_id)
    if not u:
        return _resp(404, "用户不存在"), 404
    return _resp(200, "success", {"userId": u["id"], "username": u["username"], "email": u["email"]})


@app.route("/api/v1/users", methods=["GET"])
@_require_auth
def list_users():
    """获取用户列表"""
    items = [{"id": u["id"], "username": u["username"], "email": u["email"]} for u in USERS.values()]
    return _resp(200, "success", {"list": items, "total": len(items)})


@app.route("/api/v1/users", methods=["POST"])
@_require_auth
def create_user():
    """创建用户"""
    body = request.get_json() or {}
    username = body.get("username")
    password = body.get("password")
    email = body.get("email", "")
    if not username or not password:
        return _resp(400, "username 和 password 必填"), 400
    for u in USERS.values():
        if u["username"] == username:
            return _resp(400, "用户名已存在"), 400
    uid = str(uuid.uuid4())
    USERS[uid] = {"id": uid, "username": username, "password": password, "email": email}
    return _resp(200, "success", {"id": uid, "username": username, "email": email})


@app.route("/api/v1/users/<user_id>", methods=["GET"])
@_require_auth
def get_user(user_id):
    """获取指定用户"""
    u = USERS.get(user_id)
    if not u:
        return _resp(404, "用户不存在"), 404
    return _resp(200, "success", {"id": u["id"], "username": u["username"], "email": u["email"]})


@app.route("/api/v1/users/<user_id>", methods=["PUT"])
@_require_auth
def update_user(user_id):
    """更新用户"""
    u = USERS.get(user_id)
    if not u:
        return _resp(404, "用户不存在"), 404
    body = request.get_json() or {}
    if "email" in body:
        u["email"] = body["email"]
    if "password" in body:
        u["password"] = body["password"]
    return _resp(200, "success", {"id": u["id"], "username": u["username"], "email": u["email"]})


@app.route("/api/v1/users/<user_id>", methods=["DELETE"])
@_require_auth
def delete_user(user_id):
    """删除用户"""
    if user_id not in USERS:
        return _resp(404, "用户不存在"), 404
    del USERS[user_id]
    for t, uid in list(TOKENS.items()):
        if uid == user_id:
            del TOKENS[t]
            break
    return _resp(200, "success", None)


if __name__ == "__main__":
    _init_demo_users()
    port = int(os.environ.get("DEMO_PORT", "11011"))
    app.run(host="0.0.0.0", port=port, debug=True)
