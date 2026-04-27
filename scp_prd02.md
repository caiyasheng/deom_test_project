# 后台系统功能扩展设计（真实业务复杂度版本）

## 1. 目标

将当前”用户CRUD系统”升级为一个**具备真实业务复杂度的后台系统**，从而：

* 增加操作链路长度
* 引入状态变化与约束
* 构建跨模块交互
* 提升 UI 自动化测试深度

---

## 2. 系统演进方向

从：

👉 用户管理系统

升级为：

👉 **用户 + 订单 + 审批 + 通知 + 日志 的业务后台系统**

---

## 3. 技术栈（保持一致）

| 层次 | 技术 |
|------|------|
| 后端 | Python Flask |
| 前端 | Vue 3 + Vite |
| 存储 | 内存字典 (In-Memory) |
| 认证 | Token (UUID) |
| 构建 | Vite |

---

## 4. 核心模块设计

---

### 4.1 用户模块

#### 4.1.1 用户字段（完整定义）

| 字段名 | 类型 | 枚举值/说明 | 默认值 |
|--------|------|------------|--------|
| id | string | UUID | 自动生成 |
| username | string | 唯一 | 必填 |
| password | string | 明文存储 | 必填 |
| email | string | 邮箱格式 | 可选 |
| status | string | `inactive`(未激活) / `active`(正常) / `frozen`(冻结) | `active` |
| role | string | `Admin`(管理员) / `Operator`(操作员) / `Viewer`(访客) | `Viewer` |
| level | string | `normal`(普通) / `vip`(VIP) | `normal` |
| organization | string | 所属组织名称 | 空字符串 |
| created_at | string | ISO 8601 时间格式 | 自动生成 |

#### 4.1.2 用户状态规则

| 规则 | 触发条件 | 结果 |
|------|----------|------|
| 登录限制 | status = `inactive` | 登录失败，提示”用户未激活” |
| 登录限制 | status = `frozen` | 登录失败，提示”用户已冻结” |
| 订单限制 | status = `frozen` | 创建订单失败，提示”用户已冻结” |

#### 4.1.3 权限矩阵

| 操作 | Admin | Operator | Viewer |
|------|-------|-----------|--------|
| 登录 | ✅ | ✅ | ✅ |
| 查看用户列表 | ✅ | ✅ | ✅ |
| 创建用户 | ✅ | ✅ | ❌ |
| 编辑用户 | ✅ | ✅ (仅自己) | ❌ |
| 删除用户 | ✅ | ❌ | ❌ |
| 创建订单 | ✅ | ✅ | ❌ |
| 提交订单 | ✅ | ✅ | ❌ |
| 审批订单 | ✅ | ❌ | ❌ |
| 查看通知 | ✅ | ✅ | ✅ |
| 查看日志 | ✅ | ✅ | ❌ |

#### 4.1.4 接口变更

**登录接口 `/auth/login`**
- 请求： `{username, password}`
- 响应 data 增加字段：
```json
{
  “token”: “uuid”,
  “userId”: “xxx”,
  “role”: “Admin|Operator|Viewer”,
  “level”: “normal|vip”
}
```

**用户详情 `/api/v1/users/{id}`**
- 响应 data 增加： `status`, `role`, `level`, `organization`, `created_at`

**用户列表 `/api/v1/users`**
- 响应中每条用户记录增加上述字段
- 支持分页参数：`page`, `page_size`

---

### 4.2 订单模块（核心复杂度来源）

#### 4.2.1 订单字段（完整定义）

| 字段名 | 类型 | 说明 | 默认值 |
|--------|------|------|--------|
| id | string | UUID | 自动生成 |
| order_no | string | 订单编号，格式 `ORD-YYYYMMDD-XXXX` | 自动生成 |
| user_id | string | 创建用户ID | 必填 |
| title | string | 订单标题 | 必填 |
| description | string | 订单描述 | 可选 |
| amount | number | 订单金额（元），精确到小数点后2位 | 必填 |
| status | string | 见状态机定义 | `draft`(草稿) |
| created_at | string | ISO 8601 时间 | 自动生成 |
| updated_at | string | ISO 8601 时间 | 自动生成 |
| submitted_at | string | 提交时间 | null |
| approved_at | string | 审批时间 | null |
| completed_at | string | 完成时间 | null |
| approver_id | string | 审批人ID | null |
| approval_comment | string | 审批意见 | null |

#### 4.2.2 订单状态机（重点）

```
                    ┌──────────────────────────┐
                    │                          │
    ┌─────────┐     │    ┌─────────┐     ┌─────────┐     ┌─────────┐
───►│  draft  │─────┼───►│pending  │────►│approved │────►│completed│
    └─────────┘     │    └─────────┘     └─────────┘     └─────────┘
                    │         │               │
                    │         │ reject        │
                    │         ▼               │
                    │    ┌─────────┐           │
                    └───►│ rejected│           │
                         └─────────┘           │
                              │                 │
                              │ cancel          │ cancel
                              ▼                 ▼
                         ┌─────────────────────────┐
                         │       cancelled         │
                         └─────────────────────────┘
```

**状态说明：**

| 状态 | 枚举值 | 说明 | 可执行操作 |
|------|--------|------|------------|
| 草稿 | `draft` | 订单刚创建，未提交 | 提交、取消、编辑 |
| 待审核 | `pending` | 已提交，等待审批 | 审批（Admin）、取消 |
| 已通过 | `approved` | 审批通过 | 完成、取消 |
| 已完成 | `completed` | 订单已完成 | 无（终态） |
| 已拒绝 | `rejected` | 审批被拒绝 | 无（终态） |
| 已取消 | `cancelled` | 订单被取消 | 无（终态） |

**状态转换规则：**

| 当前状态 | 目标状态 | 触发操作 | 权限要求 | 附加规则 |
|----------|----------|----------|----------|----------|
| draft | pending | submit | Operator+, Viewer除外 | 订单金额>0 |
| pending | approved | approve | Admin | 填写审批意见 |
| pending | rejected | reject | Admin | 填写审批意见 |
| approved | completed | complete | Admin, Operator | - |
| draft/pending/approved | cancelled | cancel | Admin, 或订单创建者本人 | - |

#### 4.2.3 订单业务规则

| 规则 | 说明 |
|------|------|
| 订单金额 | 必须 > 0 |
| 订单编号 | 自动生成，格式 `ORD-YYYYMMDD-XXXX`，XXXX为4位序号 |
| 编辑限制 | 只有 `draft` 状态可编辑 |
| 提交限制 | `frozen` 状态用户不能提交订单 |
| 取消限制 | `completed`/`rejected`/`cancelled` 状态不可取消 |

#### 4.2.4 订单接口

| 接口 | 方法 | 说明 | 权限 |
|------|------|------|------|
| `/api/v1/orders` | GET | 获取订单列表 | 登录用户（看自己的） |
| `/api/v1/orders` | POST | 创建订单 | Operator+ |
| `/api/v1/orders/{id}` | GET | 获取订单详情 | 订单所有者或 Admin |
| `/api/v1/orders/{id}` | PUT | 编辑订单 | 订单所有者（仅draft） |
| `/api/v1/orders/{id}/submit` | POST | 提交订单 | Operator+，仅draft |
| `/api/v1/orders/{id}/approve` | POST | 审批通过 | Admin |
| `/api/v1/orders/{id}/reject` | POST | 审批拒绝 | Admin |
| `/api/v1/orders/{id}/complete` | POST | 完成订单 | Admin, Operator |
| `/api/v1/orders/{id}/cancel` | POST | 取消订单 | Admin 或 创建者本人 |
| `/api/v1/admin/orders` | GET | 管理所有订单 | Admin |

**创建订单请求：**
```json
{
  “title”: “采购办公用品”,
  “description”: “键盘鼠标套装”,
  “amount”: 299.99
}
```

**提交订单请求：**
```json
{
  “comment”: “请尽快审批”  // 可选
}
```

**审批请求：**
```json
{
  “comment”: “同意采购”
}
```

---

### 4.3 审批模块

#### 4.3.1 审批接口

与订单模块的 `/orders/{id}/approve` 和 `/orders/{id}/reject` 共用。

#### 4.3.2 审批规则

- 只有 `Admin` 角色可以审批
- 审批时必须填写审批意见 `comment`（不能为空）
- 审批后记录审批人ID和审批时间

---

### 4.4 通知模块

#### 4.4.1 通知字段

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | string | UUID |
| receiver_id | string | 接收者用户ID |
| type | string | `order_created` / `order_submitted` / `order_approved` / `order_rejected` / `order_completed` / `order_cancelled` |
| title | string | 通知标题 |
| content | string | 通知内容（纯文本） |
| related_id | string | 关联对象ID（订单ID等） |
| is_read | boolean | 是否已读 |
| created_at | string | ISO 8601 时间 |

#### 4.4.2 通知触发逻辑

| 事件 | 触发条件 | 通知接收者 | 通知类型 |
|------|----------|------------|----------|
| 创建订单 | 新建订单 | Admin 全部 | `order_created` |
| 提交订单 | 订单状态 → pending | Admin 全部 | `order_submitted` |
| 审批通过 | 订单状态 → approved | 订单创建者 | `order_approved` |
| 审批拒绝 | 订单状态 → rejected | 订单创建者 | `order_rejected` |
| 订单完成 | 订单状态 → completed | 订单创建者 | `order_completed` |
| 订单取消 | 订单状态 → cancelled | Admin 全部 + 创建者 | `order_cancelled` |

#### 4.4.3 通知接口

| 接口 | 方法 | 说明 | 权限 |
|------|------|------|------|
| `/api/v1/notifications` | GET | 获取我的通知列表 | 登录用户 |
| `/api/v1/notifications/{id}/read` | PUT | 标记通知为已读 | 接收者本人 |

**获取通知响应：**
```json
{
  “code”: 200,
  “data”: {
    “list”: [
      {
        “id”: “xxx”,
        “type”: “order_approved”,
        “title”: “订单已通过审批”,
        “content”: “您的订单 ORD-20260424-0001 已通过审批”,
        “related_id”: “order-xxx”,
        “is_read”: false,
        “created_at”: “2026-04-24T10:00:00Z”
      }
    ],
    “total”: 5,
    “unread_count”: 2
  }
}
```

---

### 4.5 操作日志模块

#### 4.5.1 日志字段

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | string | UUID |
| user_id | string | 操作用户ID |
| username | string | 操作用户名（冗余存储） |
| action | string | 操作类型 |
| target_type | string | 目标对象类型（user/order/notification） |
| target_id | string | 目标对象ID |
| detail | object | 操作详情（变更前后） |
| ip_address | string | IP地址（模拟） |
| created_at | string | ISO 8601 时间 |

#### 4.5.2 操作类型枚举

| action | 说明 |
|--------|------|
| `user.login` | 用户登录 |
| `user.logout` | 用户退出 |
| `user.create` | 创建用户 |
| `user.update` | 更新用户 |
| `user.delete` | 删除用户 |
| `order.create` | 创建订单 |
| `order.update` | 更新订单 |
| `order.submit` | 提交订单 |
| `order.approve` | 审批通过 |
| `order.reject` | 审批拒绝 |
| `order.complete` | 完成订单 |
| `order.cancel` | 取消订单 |

#### 4.5.3 日志接口

| 接口 | 方法 | 说明 | 权限 |
|------|------|------|------|
| `/api/v1/logs` | GET | 获取操作日志 | Admin, Operator |
| `/api/v1/logs?user_id=xxx` | GET | 筛选指定用户的日志 | Admin |

**响应格式：**
```json
{
  “code”: 200,
  “data”: {
    “list”: [
      {
        “id”: “log-xxx”,
        “user_id”: “user-1”,
        “username”: “admin”,
        “action”: “order.create”,
        “target_type”: “order”,
        “target_id”: “order-xxx”,
        “detail”: {
          “order_no”: “ORD-20260424-0001”,
          “title”: “采购办公用品”
        },
        “ip_address”: “127.0.0.1”,
        “created_at”: “2026-04-24T10:00:00Z”
      }
    ],
    “total”: 100
  }
}
```

---

### 4.6 权限系统

#### 4.6.1 角色定义

| 角色 | 说明 | 默认用户 |
|------|------|----------|
| Admin | 管理员，拥有全部权限 | admin |
| Operator | 操作员，可创建/处理订单 | test |
| Viewer | 访客，仅可查看 | - |

#### 4.6.2 前端权限控制

1. **路由权限**：根据角色显示/隐藏导航菜单
2. **按钮权限**：根据角色显示/隐藏操作按钮
3. **接口拦截**：后端返回 403 时前端提示”无权限”

#### 4.6.3 UI表现示例

| 场景 | Admin | Operator | Viewer |
|------|-------|-----------|--------|
| 用户列表页面 | 显示”添加用户”按钮 | 隐藏”添加用户”按钮 | 隐藏”添加用户”按钮 |
| 用户行操作 | 显示”编辑”+”删除” | 仅显示”编辑”(自己的行) | 无操作按钮 |
| 订单列表页面 | 显示”审批”按钮 | 显示”提交”+”取消” | 仅查看 |
| 侧边栏菜单 | 显示”用户管理”+”日志” | 显示”我的订单” | 仅显示”通知” |

---

## 5. 关键业务流程（自动化测试重点）

---

### 流程1：正常审批流程（核心）

```
1. Operator 创建订单 (draft)
   → 生成通知: 发送给所有 Admin (order_created)
   → 生成日志: order.create

2. Operator 提交订单 (draft → pending)
   → 生成通知: 发送给所有 Admin (order_submitted)
   → 生成日志: order.submit

3. Admin 审批通过 (pending → approved)
   → 生成通知: 发送给订单创建者 (order_approved)
   → 生成日志: order.approve

4. Operator 完成订单 (approved → completed)
   → 生成通知: 发送给订单创建者 (order_completed)
   → 生成日志: order.complete
```

**自动化验证点：**
- [ ] 订单状态正确流转
- [ ] 每个状态对应正确的按钮组合
- [ ] 每个操作生成对应通知
- [ ] 每个操作记录对应日志

---

### 流程2：审批拒绝流程

```
1. Operator 创建订单 → 提交
2. Admin 审批拒绝 (pending → rejected)
   → 生成通知: 发送给订单创建者 (order_rejected)
   → 审批意见被记录
```

**自动化验证点：**
- [ ] 拒绝后订单终态为 rejected
- [ ] 创建者收到拒绝通知
- [ ] 拒绝后订单不可再操作

---

### 流程3：取消订单流程

```
1. Operator 创建订单
2. Operator 取消订单 (draft → cancelled)
   → 生成通知: 发送给所有 Admin + 创建者 (order_cancelled)

3. 或: Admin 取消待审核订单 (pending → cancelled)
```

**自动化验证点：**
- [ ] 不同角色都可以取消（自己创建的/Admin）
- [ ] 已完成/已拒绝订单不可取消

---

### 流程4：权限验证流程

```
1. Viewer 尝试创建订单
   → 预期: 前端隐藏按钮 或 后端返回 403

2. Operator 尝试审批订单
   → 预期: 前端隐藏按钮 或 后端返回 403

3. Operator 尝试删除用户
   → 预期: 前端隐藏按钮 或 后端返回 403
```

**自动化验证点：**
- [ ] 权限不足时正确拒绝
- [ ] 不同角色看到不同 UI

---

### 流程5：用户状态限制流程

```
1. Admin 冻结用户 (active → frozen)
   → 用户被强制登出（如果在线）
   → 用户无法登录

2. frozen 用户尝试登录
   → 登录失败，提示”用户已冻结”

3. frozen 用户尝试创建订单
   → 创建失败，提示”用户已冻结”
```

**自动化验证点：**
- [ ] frozen 用户无法登录
- [ ] frozen 用户无法创建/提交订单

---

## 6. 实现顺序

### 阶段1：用户模块增强
- T1.1 用户字段扩展（后端）
- T1.2 用户列表页增强（前端）+ 分页

### 阶段2：订单模块基础
- T2.1 订单模型（后端）
- T2.2 订单 CRUD 接口
- T2.3 订单列表页（前端）

### 阶段3：订单状态机（核心）
- T3.1 状态流转逻辑（后端）
- T3.2 状态变更接口
- T3.3 UI状态控制（前端）

### 阶段4：审批 + 权限
- T4.1 审批接口（后端）
- T4.2 审批页面（前端）
- T5.1 登录返回角色
- T5.2 前端权限控制

### 阶段5：通知 + 日志
- T6.1 通知模型（后端）
- T6.2 触发逻辑
- T6.3 通知列表页
- T7.1 日志记录
- T7.2 日志页面

### 阶段6：异常模拟
- T8.1 接口延迟（2-3秒）
- T8.2 错误模拟（随机失败）

### 阶段7：端到端验证
- 流程1-5 全流程验证

---

## 7. 统一响应格式（扩展）

所有接口保持原有格式，新增分页和列表格式：

```json
// 列表响应
{
  “code”: 200,
  “msg”: “success”,
  “data”: {
    “list”: [],
    “total”: 0,
    “page”: 1,
    “page_size”: 10
  }
}

// 分页响应
{
  “code”: 200,
  “msg”: “success”,
  “data”: {
    “list”: [],
    “total”: 100,
    “page”: 1,
    “page_size”: 10
  }
}

// 错误响应
{
  “code”: 400|401|403|404,
  “msg”: “错误描述”,
  “data”: null
}
```

---

## 8. 模拟数据初始化

| 用户名 | 密码 | 角色 | 状态 | 等级 |
|--------|------|------|------|------|
| admin | admin123 | Admin | active | vip |
| test | test123 | Operator | active | normal |
| viewer | viewer123 | Viewer | active | normal |
| frozen | frozen123 | Operator | frozen | normal |
| inactive | inactive123 | Viewer | inactive | normal |

---



## 6. 实现顺序（给ClaudeCode）

### 阶段1

* 用户模块增强
* 基础订单CRUD

### 阶段2

* 订单状态机
* UI状态控制

### 阶段3

* 审批模块
* 角色权限

### 阶段4

* 通知模块
* 操作日志

---

