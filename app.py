"""
业务后台系统 API 服务：用户 + 订单 + 审批 + 通知 + 日志
基于 Flask，提供完整的业务后台功能。
"""

import os
import json
import uuid
from datetime import datetime
from functools import wraps

from flask import Flask, request, jsonify

app = Flask(__name__)
app.config["SECRET_KEY"] = "demo-secret"

# ==================== 数据存储 ====================

DATA_FILE = os.path.join(os.path.dirname(__file__), "data.json")
USERS: dict[str, dict] = {}
TOKENS: dict[str, str] = {}  # token -> user_id
ORDERS: dict[str, dict] = {}
NOTIFICATIONS: dict[str, dict] = {}
LOGS: list[dict] = []
ORDER_COUNTER: int = 0  # 订单序号计数器

# ==================== 初始化演示数据 ====================

def _init_demo_users():
    """初始化演示用户"""
    if not USERS:
        demo_users = [
            {
                "id": "1",
                "username": "admin",
                "password": "admin123",
                "email": "admin@demo.com",
                "status": "active",
                "role": "Admin",
                "level": "vip",
                "organization": "管理层",
            },
            {
                "id": "2",
                "username": "test",
                "password": "test123",
                "email": "test@demo.com",
                "status": "active",
                "role": "Operator",
                "level": "normal",
                "organization": "运营部",
            },
            {
                "id": "3",
                "username": "viewer",
                "password": "viewer123",
                "email": "viewer@demo.com",
                "status": "active",
                "role": "Viewer",
                "level": "normal",
                "organization": "观察部",
            },
            {
                "id": "4",
                "username": "frozen",
                "password": "frozen123",
                "email": "frozen@demo.com",
                "status": "frozen",
                "role": "Operator",
                "level": "normal",
                "organization": "运营部",
            },
            {
                "id": "5",
                "username": "inactive",
                "password": "inactive123",
                "email": "inactive@demo.com",
                "status": "inactive",
                "role": "Viewer",
                "level": "normal",
                "organization": "待激活",
            },
        ]
        for u in demo_users:
            USERS[u["id"]] = u


def _generate_order_no():
    """生成订单编号"""
    global ORDER_COUNTER
    ORDER_COUNTER += 1
    date_str = datetime.now().strftime("%Y%m%d")
    return f"ORD-{date_str}-{ORDER_COUNTER:04d}"


def _save_data():
    """保存数据到 JSON 文件"""
    data = {
        "users": USERS,
        "orders": ORDERS,
        "notifications": NOTIFICATIONS,
        "logs": LOGS,
        "order_counter": ORDER_COUNTER,
    }
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _load_data():
    """从 JSON 文件加载数据"""
    global ORDER_COUNTER
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            USERS.update(data.get("users", {}))
            ORDERS.update(data.get("orders", {}))
            NOTIFICATIONS.update(data.get("notifications", {}))
            LOGS.extend(data.get("logs", []))
            ORDER_COUNTER = data.get("order_counter", 0)
            print(f"✓ 已加载数据：{len(USERS)} 用户，{len(ORDERS)} 订单，{len(NOTIFICATIONS)} 通知，{len(LOGS)} 日志")
        except Exception as e:
            print(f"✗ 加载数据失败：{e}")


# ==================== 工具函数 ====================

def _resp(code=200, msg="success", data=None):
    return jsonify({"code": code, "msg": msg, "data": data})


def _require_auth(f):
    """通用认证装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get("Authorization")
        if not auth or not auth.startswith("Bearer "):
            return _resp(401, "未授权", None), 401
        token = auth[7:]
        user_id = TOKENS.get(token)
        if not user_id or user_id not in USERS:
            return _resp(401, "token 无效", None), 401
        request.current_user_id = user_id
        request.current_user = USERS[user_id]
        return f(*args, **kwargs)
    return decorated


def _require_role(*roles):
    """角色权限装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            user = getattr(request, 'current_user', None)
            if not user or user.get("role") not in roles:
                return _resp(403, "无权限", None), 403
            return f(*args, **kwargs)
        return decorated
    return decorator


def _log_action(action: str, target_type: str, target_id: str, detail: dict = None, user_id: str = None, username: str = None):
    """记录操作日志"""
    log_entry = {
        "id": str(uuid.uuid4()),
        "user_id": user_id or getattr(request, 'current_user_id', None),
        "username": username or (getattr(request, 'current_user', None) or {}).get("username", ""),
        "action": action,
        "target_type": target_type,
        "target_id": target_id,
        "detail": detail or {},
        "ip_address": request.remote_addr or "127.0.0.1",
        "created_at": datetime.now().isoformat() + "Z",
    }
    LOGS.insert(0, log_entry)
    _save_data()


def _create_notification(receiver_ids: list, notify_type: str, title: str, content: str, related_id: str = None):
    """创建通知"""
    for rid in receiver_ids:
        notif = {
            "id": str(uuid.uuid4()),
            "receiver_id": rid,
            "type": notify_type,
            "title": title,
            "content": content,
            "related_id": related_id,
            "is_read": False,
            "created_at": datetime.now().isoformat() + "Z",
        }
        NOTIFICATIONS[notif["id"]] = notif
    _save_data()


def _notify_admins(notify_type: str, title: str, content: str, related_id: str = None):
    """通知所有管理员"""
    admin_ids = [uid for uid, u in USERS.items() if u.get("role") == "Admin"]
    _create_notification(admin_ids, notify_type, title, content, related_id)


def _get_user_notifications(user_id: str) -> list:
    """获取用户的所有通知"""
    return [n for n in NOTIFICATIONS.values() if n["receiver_id"] == user_id]


# ==================== 认证接口 ====================

@app.route("/api/auth/login", methods=["POST"])
def login():
    """用户登录"""
    body = request.get_json() or {}
    username = (body.get("username") or "").strip()
    password = (body.get("password") or "").strip()

    if not username or not password:
        return _resp(400, "用户名和密码必填", None), 400

    for uid, u in USERS.items():
        if u["username"] == username and u["password"] == password:
            # 检查用户状态
            if u["status"] == "inactive":
                return _resp(401, "用户未激活", None), 401
            if u["status"] == "frozen":
                return _resp(401, "用户已冻结", None), 401

            token = str(uuid.uuid4())
            TOKENS[token] = uid

            _log_action("user.login", "user", uid, {"username": username}, user_id=uid, username=username)

            return _resp(200, "success", {
                "token": token,
                "userId": uid,
                "role": u["role"],
                "level": u["level"],
            })

    return _resp(401, "用户名或密码错误", None), 401


@app.route("/api/auth/logout", methods=["POST"])
@_require_auth
def logout():
    """用户退出登录"""
    token = request.headers.get("Authorization", "")[7:]
    user_id = TOKENS.pop(token, None)
    if user_id:
        _log_action("user.logout", "user", user_id, {})
    return _resp(200, "success", None)


# ==================== 用户接口 ====================

@app.route("/api/v1/user", methods=["GET"])
@_require_auth
def get_current_user():
    """获取当前登录用户信息"""
    u = USERS.get(request.current_user_id)
    if not u:
        return _resp(404, "用户不存在", None), 404

    return _resp(200, "success", {
        "id": u["id"],
        "userId": u["id"],
        "username": u["username"],
        "email": u["email"],
        "status": u["status"],
        "role": u["role"],
        "level": u["level"],
        "organization": u.get("organization", ""),
        "created_at": u.get("created_at", ""),
    })


@app.route("/api/v1/users", methods=["GET"])
@_require_auth
def list_users():
    """获取用户列表"""
    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("page_size", 10))

    all_users = list(USERS.values())
    total = len(all_users)

    # 分页
    start = (page - 1) * page_size
    end = start + page_size
    items = [
        {
            "id": u["id"],
            "username": u["username"],
            "email": u["email"],
            "status": u["status"],
            "role": u["role"],
            "level": u["level"],
            "organization": u.get("organization", ""),
            "created_at": u.get("created_at", ""),
        }
        for u in all_users[start:end]
    ]

    return _resp(200, "success", {
        "list": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    })


@app.route("/api/v1/users", methods=["POST"])
@_require_auth
@_require_role("Admin", "Operator")
def create_user():
    """创建用户"""
    body = request.get_json() or {}
    username = body.get("username")
    password = body.get("password")
    email = body.get("email", "")
    role = body.get("role", "Viewer")
    level = body.get("level", "normal")
    organization = body.get("organization", "")
    status = body.get("status", "active")

    if not username or not password:
        return _resp(400, "用户名和密码必填", None), 400

    for u in USERS.values():
        if u["username"] == username:
            return _resp(400, "用户名已存在", None), 400

    uid = str(uuid.uuid4())
    now = datetime.now().isoformat() + "Z"
    USERS[uid] = {
        "id": uid,
        "username": username,
        "password": password,
        "email": email,
        "status": status,
        "role": role,
        "level": level,
        "organization": organization,
        "created_at": now,
    }
    _save_data()

    _log_action("user.create", "user", uid, {"username": username, "role": role})

    return _resp(200, "success", {
        "id": uid,
        "username": username,
        "email": email,
        "status": status,
        "role": role,
        "level": level,
        "organization": organization,
        "created_at": USERS[uid]["created_at"],
    })


@app.route("/api/v1/users/<user_id>", methods=["GET"])
@_require_auth
def get_user(user_id):
    """获取指定用户"""
    u = USERS.get(user_id)
    if not u:
        return _resp(404, "用户不存在", None), 404

    return _resp(200, "success", {
        "id": u["id"],
        "username": u["username"],
        "email": u["email"],
        "status": u["status"],
        "role": u["role"],
        "level": u["level"],
        "organization": u.get("organization", ""),
        "created_at": u.get("created_at", ""),
    })


@app.route("/api/v1/users/<user_id>", methods=["PUT"])
@_require_auth
def update_user(user_id):
    """更新用户"""
    u = USERS.get(user_id)
    if not u:
        return _resp(404, "用户不存在", None), 404

    current_user = request.current_user
    # 非 Admin 只能修改自己的信息
    if current_user["role"] != "Admin" and current_user["id"] != user_id:
        return _resp(403, "无权限修改此用户", None), 403

    body = request.get_json() or {}

    # Admin 可以修改所有字段，其他角色只能修改部分
    if current_user["role"] == "Admin":
        if "email" in body:
            u["email"] = body["email"]
        if "password" in body:
            u["password"] = body["password"]
        if "status" in body:
            u["status"] = body["status"]
        if "role" in body:
            u["role"] = body["role"]
        if "level" in body:
            u["level"] = body["level"]
        if "organization" in body:
            u["organization"] = body["organization"]
    else:
        # Operator 只能修改自己的 email 和 password
        if "email" in body:
            u["email"] = body["email"]
        if "password" in body:
            u["password"] = body["password"]

    _save_data()
    _log_action("user.update", "user", user_id, {"updated_fields": list(body.keys())})

    return _resp(200, "success", {
        "id": u["id"],
        "username": u["username"],
        "email": u["email"],
        "status": u["status"],
        "role": u["role"],
        "level": u["level"],
        "organization": u.get("organization", ""),
        "created_at": u.get("created_at", ""),
    })


@app.route("/api/v1/users/<user_id>", methods=["DELETE"])
@_require_auth
@_require_role("Admin")
def delete_user(user_id):
    """删除用户"""
    if user_id not in USERS:
        return _resp(404, "用户不存在", None), 404

    username = USERS[user_id]["username"]
    del USERS[user_id]
    _save_data()

    # 清理该用户的 token
    tokens_to_remove = [t for t, uid in list(TOKENS.items()) if uid == user_id]
    for t in tokens_to_remove:
        del TOKENS[t]

    _log_action("user.delete", "user", user_id, {"username": username})

    return _resp(200, "success", None)


# ==================== 订单接口 ====================

@app.route("/api/v1/orders", methods=["GET"])
@_require_auth
def list_orders():
    """获取订单列表（当前用户创建的订单）"""
    current_user = request.current_user

    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("page_size", 10))
    status_filter = request.args.get("status", None)

    # Admin 可以看所有订单，其他用户只能看自己的
    if current_user["role"] == "Admin":
        all_orders = list(ORDERS.values())
    else:
        all_orders = [o for o in ORDERS.values() if o["user_id"] == current_user["id"]]

    # 状态筛选
    if status_filter:
        all_orders = [o for o in all_orders if o["status"] == status_filter]

    # 按创建时间倒序
    all_orders.sort(key=lambda x: x.get("created_at", ""), reverse=True)

    total = len(all_orders)
    start = (page - 1) * page_size
    end = start + page_size
    items = all_orders[start:end]

    return _resp(200, "success", {
        "list": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    })


@app.route("/api/v1/admin/orders", methods=["GET"])
@_require_auth
@_require_role("Admin")
def list_all_orders():
    """管理所有订单（Admin 专用）"""
    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("page_size", 10))
    status_filter = request.args.get("status", None)

    all_orders = list(ORDERS.values())

    if status_filter:
        all_orders = [o for o in all_orders if o["status"] == status_filter]

    all_orders.sort(key=lambda x: x.get("created_at", ""), reverse=True)

    total = len(all_orders)
    start = (page - 1) * page_size
    end = start + page_size
    items = all_orders[start:end]

    return _resp(200, "success", {
        "list": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    })


@app.route("/api/v1/orders", methods=["POST"])
@_require_auth
@_require_role("Admin", "Operator")
def create_order():
    """创建订单"""
    current_user = request.current_user

    # frozen 用户不能创建订单
    if current_user["status"] == "frozen":
        return _resp(400, "用户已冻结，无法创建订单", None), 400

    body = request.get_json() or {}
    title = body.get("title", "").strip()
    description = body.get("description", "").strip()
    amount = body.get("amount")

    if not title:
        return _resp(400, "订单标题必填", None), 400
    if amount is None or float(amount) <= 0:
        return _resp(400, "订单金额必须大于0", None), 400

    now = datetime.now().isoformat() + "Z"
    order_id = str(uuid.uuid4())
    order = {
        "id": order_id,
        "order_no": _generate_order_no(),
        "user_id": current_user["id"],
        "creator_name": current_user["username"],
        "title": title,
        "description": description,
        "amount": float(amount),
        "status": "draft",
        "created_at": now,
        "updated_at": now,
        "submitted_at": None,
        "approved_at": None,
        "completed_at": None,
        "cancelled_at": None,
        "approver_id": None,
        "approver_name": None,
        "approval_comment": None,
        "cancel_reason": None,
    }
    ORDERS[order_id] = order
    _save_data()

    _log_action("order.create", "order", order_id, {
        "order_no": order["order_no"],
        "title": title,
        "amount": float(amount),
    })

    # 通知管理员
    _notify_admins(
        "order_created",
        f"新订单: {order['order_no']}",
        f"用户 {current_user['username']} 创建了新订单 '{title}'，金额 {amount} 元",
        order_id
    )

    return _resp(200, "success", order)


@app.route("/api/v1/orders/<order_id>", methods=["GET"])
@_require_auth
def get_order(order_id):
    """获取订单详情"""
    current_user = request.current_user
    order = ORDERS.get(order_id)

    if not order:
        return _resp(404, "订单不存在", None), 404

    # 非 Admin 只能查看自己的订单
    if current_user["role"] != "Admin" and order["user_id"] != current_user["id"]:
        return _resp(403, "无权限查看此订单", None), 403

    return _resp(200, "success", order)


@app.route("/api/v1/orders/<order_id>", methods=["PUT"])
@_require_auth
def update_order(order_id):
    """更新订单（仅 draft 状态可编辑）"""
    current_user = request.current_user
    order = ORDERS.get(order_id)

    if not order:
        return _resp(404, "订单不存在", None), 404

    # 非 Admin 只能编辑自己的订单
    if current_user["role"] != "Admin" and order["user_id"] != current_user["id"]:
        return _resp(403, "无权限修改此订单", None), 403

    # 只有 draft 状态可以编辑
    if order["status"] != "draft":
        return _resp(400, "只有草稿状态的订单可以编辑", None), 400

    body = request.get_json() or {}

    if "title" in body:
        order["title"] = body["title"].strip()
    if "description" in body:
        order["description"] = body["description"].strip()
    if "amount" in body:
        amount = float(body["amount"])
        if amount <= 0:
            return _resp(400, "订单金额必须大于0", None), 400
        order["amount"] = amount

    order["updated_at"] = datetime.now().isoformat() + "Z"
    _save_data()

    _log_action("order.update", "order", order_id, {"updated_fields": list(body.keys())})

    return _resp(200, "success", order)


@app.route("/api/v1/orders/<order_id>/submit", methods=["POST"])
@_require_auth
@_require_role("Admin", "Operator")
def submit_order(order_id):
    """提交订单 (draft -> pending)"""
    current_user = request.current_user
    order = ORDERS.get(order_id)

    if not order:
        return _resp(404, "订单不存在", None), 404

    # 只能提交自己的订单
    if current_user["role"] != "Admin" and order["user_id"] != current_user["id"]:
        return _resp(403, "无权限操作此订单", None), 403

    # frozen 用户不能提交订单
    if current_user["status"] == "frozen":
        return _resp(400, "用户已冻结，无法提交订单", None), 400

    if order["status"] != "draft":
        return _resp(400, "只有草稿状态的订单可以提交", None), 400

    order["status"] = "pending"
    order["submitted_at"] = datetime.now().isoformat() + "Z"
    order["updated_at"] = order["submitted_at"]
    _save_data()

    _log_action("order.submit", "order", order_id, {"order_no": order["order_no"]})

    # 通知管理员
    _notify_admins(
        "order_submitted",
        f"订单待审批: {order['order_no']}",
        f"用户 {current_user['username']} 提交了订单 '{order['title']}'，金额 {order['amount']} 元",
        order_id
    )

    return _resp(200, "success", order)


@app.route("/api/v1/orders/<order_id>/approve", methods=["POST"])
@_require_auth
@_require_role("Admin")
def approve_order(order_id):
    """审批通过 (pending -> approved)"""
    current_user = request.current_user
    order = ORDERS.get(order_id)

    if not order:
        return _resp(404, "订单不存在", None), 404

    if order["status"] != "pending":
        return _resp(400, "只有待审核状态的订单可以审批", None), 400

    body = request.get_json() or {}
    comment = body.get("comment", "").strip()

    if not comment:
        return _resp(400, "审批意见必填", None), 400

    now = datetime.now().isoformat() + "Z"
    order["status"] = "approved"
    order["approved_at"] = now
    order["updated_at"] = now
    order["approver_id"] = current_user["id"]
    order["approver_name"] = current_user["username"]
    order["approval_comment"] = comment
    _save_data()

    _log_action("order.approve", "order", order_id, {
        "order_no": order["order_no"],
        "comment": comment,
    })

    # 通知订单创建者
    _create_notification(
        [order["user_id"]],
        "order_approved",
        f"订单已通过审批: {order['order_no']}",
        f"您的订单 '{order['title']}' 已通过审批，审批意见: {comment}",
        order_id
    )

    return _resp(200, "success", order)


@app.route("/api/v1/orders/<order_id>/reject", methods=["POST"])
@_require_auth
@_require_role("Admin")
def reject_order(order_id):
    """审批拒绝 (pending -> rejected)"""
    current_user = request.current_user
    order = ORDERS.get(order_id)

    if not order:
        return _resp(404, "订单不存在", None), 404

    if order["status"] != "pending":
        return _resp(400, "只有待审核状态的订单可以审批", None), 400

    body = request.get_json() or {}
    comment = body.get("comment", "").strip()

    if not comment:
        return _resp(400, "审批意见必填", None), 400

    now = datetime.now().isoformat() + "Z"
    order["status"] = "rejected"
    order["updated_at"] = now
    order["approver_id"] = current_user["id"]
    order["approver_name"] = current_user["username"]
    order["approval_comment"] = comment
    _save_data()

    _log_action("order.reject", "order", order_id, {
        "order_no": order["order_no"],
        "comment": comment,
    })

    # 通知订单创建者
    _create_notification(
        [order["user_id"]],
        "order_rejected",
        f"订单已拒绝: {order['order_no']}",
        f"您的订单 '{order['title']}' 被拒绝，审批意见: {comment}",
        order_id
    )

    return _resp(200, "success", order)


@app.route("/api/v1/orders/<order_id>/complete", methods=["POST"])
@_require_auth
@_require_role("Admin", "Operator")
def complete_order(order_id):
    """完成订单 (approved -> completed)"""
    current_user = request.current_user
    order = ORDERS.get(order_id)

    if not order:
        return _resp(404, "订单不存在", None), 404

    if order["status"] != "approved":
        return _resp(400, "只有已通过审批的订单可以完成", None), 400

    now = datetime.now().isoformat() + "Z"
    order["status"] = "completed"
    order["completed_at"] = now
    order["updated_at"] = now
    _save_data()

    _log_action("order.complete", "order", order_id, {"order_no": order["order_no"]})

    # 通知订单创建者
    _create_notification(
        [order["user_id"]],
        "order_completed",
        f"订单已完成: {order['order_no']}",
        f"您的订单 '{order['title']}' 已完成",
        order_id
    )

    return _resp(200, "success", order)


@app.route("/api/v1/orders/<order_id>/cancel", methods=["POST"])
@_require_auth
def cancel_order(order_id):
    """取消订单"""
    current_user = request.current_user
    order = ORDERS.get(order_id)

    if not order:
        return _resp(404, "订单不存在", None), 404

    # 检查权限：Admin 或 订单创建者可以取消
    if current_user["role"] != "Admin" and order["user_id"] != current_user["id"]:
        return _resp(403, "无权限取消此订单", None), 403

    # 终态不可取消
    if order["status"] in ("completed", "rejected", "cancelled"):
        return _resp(400, f"{order['status']} 状态的订单不可取消", None), 400

    body = request.get_json() or {}
    reason = body.get("reason", "").strip()

    now = datetime.now().isoformat() + "Z"
    order["status"] = "cancelled"
    order["cancelled_at"] = now
    order["updated_at"] = now
    order["cancel_reason"] = reason or "用户取消"
    _save_data()

    _log_action("order.cancel", "order", order_id, {
        "order_no": order["order_no"],
        "reason": reason or "用户取消",
    })

    # 通知管理员和创建者
    admin_ids = [uid for uid, u in USERS.items() if u.get("role") == "Admin"]
    notify_ids = list(set(admin_ids + [order["user_id"]]))
    _create_notification(
        notify_ids,
        "order_cancelled",
        f"订单已取消: {order['order_no']}",
        f"订单 '{order['title']}' 已被取消，取消原因: {reason or '用户取消'}",
        order_id
    )

    return _resp(200, "success", order)


# ==================== 通知接口 ====================

@app.route("/api/v1/notifications", methods=["GET"])
@_require_auth
def list_notifications():
    """获取当前用户的通知列表"""
    current_user = request.current_user

    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("page_size", 10))

    all_notifs = _get_user_notifications(current_user["id"])
    all_notifs.sort(key=lambda x: x.get("created_at", ""), reverse=True)

    unread_count = len([n for n in all_notifs if not n["is_read"]])
    total = len(all_notifs)

    start = (page - 1) * page_size
    end = start + page_size
    items = all_notifs[start:end]

    return _resp(200, "success", {
        "list": items,
        "total": total,
        "unread_count": unread_count,
        "page": page,
        "page_size": page_size,
    })


@app.route("/api/v1/notifications/<notif_id>/read", methods=["PUT"])
@_require_auth
def mark_notification_read(notif_id):
    """标记通知为已读"""
    current_user = request.current_user
    notif = NOTIFICATIONS.get(notif_id)

    if not notif:
        return _resp(404, "通知不存在", None), 404

    if notif["receiver_id"] != current_user["id"]:
        return _resp(403, "无权限操作此通知", None), 403

    notif["is_read"] = True

    return _resp(200, "success", notif)


@app.route("/api/v1/notifications/read-all", methods=["PUT"])
@_require_auth
def mark_all_notifications_read():
    """标记所有通知为已读"""
    current_user = request.current_user
    count = 0
    for notif in NOTIFICATIONS.values():
        if notif["receiver_id"] == current_user["id"] and not notif["is_read"]:
            notif["is_read"] = True
            count += 1

    return _resp(200, "success", {"count": count})


# ==================== 日志接口 ====================

@app.route("/api/v1/logs", methods=["GET"])
@_require_auth
@_require_role("Admin", "Operator")
def list_logs():
    """获取操作日志"""
    current_user = request.current_user

    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("page_size", 10))
    user_filter = request.args.get("user_id", None)
    action_filter = request.args.get("action", None)

    all_logs = list(LOGS)

    # Viewer 不能看日志
    if current_user["role"] != "Admin":
        # Operator 只能看自己的日志
        all_logs = [l for l in all_logs if l["user_id"] == current_user["id"]]

    if user_filter:
        all_logs = [l for l in all_logs if l["user_id"] == user_filter]

    if action_filter:
        all_logs = [l for l in all_logs if l["action"] == action_filter]

    all_logs.sort(key=lambda x: x.get("created_at", ""), reverse=True)

    total = len(all_logs)
    start = (page - 1) * page_size
    end = start + page_size
    items = all_logs[start:end]

    return _resp(200, "success", {
        "list": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    })


# ==================== 初始化 ====================

_init_demo_users()
_load_data()

if __name__ == "__main__":
    port = int(os.environ.get("DEMO_PORT", "11011"))
    app.run(host="0.0.0.0", port=port, debug=True)
