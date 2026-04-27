<template>
  <div class="app">
    <!-- 登录页面 -->
    <div v-if="!isLoggedIn" class="login-container">
      <div class="login-form">
        <h2>业务后台系统</h2>
        <div class="form-group">
          <label>用户名</label>
          <input v-model="loginForm.username" type="text" placeholder="请输入用户名" @keyup.enter="login" />
        </div>
        <div class="form-group">
          <label>密码</label>
          <input v-model="loginForm.password" type="password" placeholder="请输入密码" @keyup.enter="login" />
        </div>
        <button @click="login" class="login-btn" :disabled="loading">
          {{ loading ? '登录中...' : '登录' }}
        </button>
        <p v-if="errorMsg" class="error-msg">{{ errorMsg }}</p>
        <div class="demo-info">
          <p>演示账号：</p>
          <div class="demo-accounts">
            <div><strong>Admin</strong>: admin / admin123</div>
            <div><strong>Operator</strong>: test / test123</div>
            <div><strong>Viewer</strong>: viewer / viewer123</div>
            <div><strong>Frozen</strong>: frozen / frozen123 (已冻结)</div>
            <div><strong>Inactive</strong>: inactive / inactive123 (未激活)</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 主应用 -->
    <div v-else class="main-app">
      <!-- 导航栏 -->
      <nav class="navbar">
        <div class="navbar-brand">业务后台系统</div>
        <div class="navbar-user">
          <span class="user-info">
            {{ currentUser?.username }}
            <span class="role-badge" :class="currentUser?.role?.toLowerCase()">{{ currentUser?.role }}</span>
            <span class="level-badge" :class="currentUser?.level">{{ currentUser?.level === 'vip' ? 'VIP' : '普通' }}</span>
          </span>
          <button @click="logout" class="logout-btn">退出登录</button>
        </div>
      </nav>

      <!-- 侧边栏 + 内容 -->
      <div class="main-content">
        <!-- 侧边栏 -->
        <aside class="sidebar">
          <ul class="nav-menu">
            <li v-for="menu in visibleMenus" :key="menu.id">
              <a :class="['nav-item', { active: activeMenu === menu.id }]" @click="activeMenu = menu.id">
                <span class="nav-icon">{{ menu.icon }}</span>
                <span class="nav-text">{{ menu.name }}</span>
              </a>
            </li>
          </ul>
        </aside>

        <!-- 内容区域 -->
        <main class="content-area">
          <!-- 仪表盘 -->
          <div v-if="activeMenu === 'dashboard'" class="dashboard">
            <h2>仪表盘</h2>
            <div class="stats-grid">
              <div class="stat-card">
                <div class="stat-label">用户总数</div>
                <div class="stat-value">{{ stats.totalUsers }}</div>
              </div>
              <div class="stat-card">
                <div class="stat-label">订单总数</div>
                <div class="stat-value">{{ stats.totalOrders }}</div>
              </div>
              <div class="stat-card">
                <div class="stat-label">待审核订单</div>
                <div class="stat-value warning">{{ stats.pendingOrders }}</div>
              </div>
              <div class="stat-card">
                <div class="stat-label">未读通知</div>
                <div class="stat-value info">{{ stats.unreadNotifications }}</div>
              </div>
            </div>
          </div>

          <!-- 用户管理 -->
          <div v-if="activeMenu === 'users'" class="user-management">
            <div class="page-header">
              <h2>用户管理</h2>
              <button v-if="isAdmin || isOperator" @click="showUserModal = true; editingUser = null; userForm = { username: '', password: '', email: '', role: 'Viewer', level: 'normal', organization: '' }" class="btn-primary">
                添加用户
              </button>
            </div>

            <div class="filter-bar">
              <select v-model="userFilters.status" class="filter-select">
                <option value="">全部状态</option>
                <option value="active">正常</option>
                <option value="inactive">未激活</option>
                <option value="frozen">冻结</option>
              </select>
              <select v-model="userFilters.role" class="filter-select">
                <option value="">全部角色</option>
                <option value="Admin">管理员</option>
                <option value="Operator">操作员</option>
                <option value="Viewer">访客</option>
              </select>
            </div>

            <div class="loading" v-if="loadingUsers">加载中...</div>
            <table v-else class="data-table">
              <thead>
                <tr>
                  <th>用户名</th>
                  <th>邮箱</th>
                  <th>角色</th>
                  <th>等级</th>
                  <th>状态</th>
                  <th>组织</th>
                  <th>创建时间</th>
                  <th v-if="isAdmin">操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="user in filteredUsers" :key="user.id">
                  <td>{{ user.username }}</td>
                  <td>{{ user.email || '-' }}</td>
                  <td><span class="role-badge" :class="user.role?.toLowerCase()">{{ user.role }}</span></td>
                  <td><span class="level-badge" :class="user.level">{{ user.level === 'vip' ? 'VIP' : '普通' }}</span></td>
                  <td><span class="status-badge" :class="user.status">{{ statusText[user.status] || user.status }}</span></td>
                  <td>{{ user.organization || '-' }}</td>
                  <td>{{ formatDate(user.created_at) }}</td>
                  <td v-if="isAdmin">
                    <button @click="editUser(user)" class="btn-edit">编辑</button>
                    <button v-if="user.id !== currentUser?.id" @click="deleteUser(user.id)" class="btn-danger">删除</button>
                  </td>
                </tr>
              </tbody>
            </table>

            <div class="pagination">
              <button @click="usersPage--" :disabled="usersPage <= 1">上一页</button>
              <span>{{ usersPage }} / {{ Math.ceil(usersTotal / usersPageSize) }}</span>
              <button @click="usersPage++" :disabled="usersPage >= Math.ceil(usersTotal / usersPageSize)">下一页</button>
            </div>
          </div>

          <!-- 订单管理 -->
          <div v-if="activeMenu === 'orders'" class="order-management">
            <div class="page-header">
              <h2>{{ isAdmin ? '订单管理' : '我的订单' }}</h2>
              <div class="header-actions">
                <button @click="createOrder" class="btn-primary">新建订单</button>
                <button v-if="isAdmin" @click="fetchAllOrders" class="btn-secondary">查看全部订单</button>
              </div>
            </div>

            <div class="filter-bar">
              <select v-model="orderFilters.status" class="filter-select">
                <option value="">全部状态</option>
                <option value="draft">草稿</option>
                <option value="pending">待审核</option>
                <option value="approved">已通过</option>
                <option value="rejected">已拒绝</option>
                <option value="completed">已完成</option>
                <option value="cancelled">已取消</option>
              </select>
            </div>

            <div class="loading" v-if="loadingOrders">加载中...</div>
            <div v-else class="order-list">
              <div v-for="order in filteredOrders" :key="order.id" class="order-card">
                <div class="order-header">
                  <span class="order-no">{{ order.order_no }}</span>
                  <span class="status-badge" :class="order.status">{{ statusText[order.status] || order.status }}</span>
                </div>
                <div class="order-body">
                  <h3>{{ order.title }}</h3>
                  <p v-if="order.description">{{ order.description }}</p>
                  <div class="order-meta">
                    <span>创建人: {{ order.creator_name }}</span>
                    <span>金额: ¥{{ order.amount?.toFixed(2) }}</span>
                    <span>{{ formatDate(order.created_at) }}</span>
                  </div>
                </div>
                <div class="order-actions">
                  <!-- draft: 可以提交、编辑、取消 -->
                  <button v-if="order.status === 'draft' && canOperateOrder(order)" @click="submitOrder(order.id)" class="btn-primary">提交</button>
                  <button v-if="order.status === 'draft' && canOperateOrder(order)" @click="editOrder(order)" class="btn-secondary">编辑</button>
                  <button v-if="order.status === 'draft' && canOperateOrder(order)" @click="cancelOrder(order.id)" class="btn-warning">取消</button>

                  <!-- pending: Admin 可以审批 -->
                  <button v-if="order.status === 'pending' && isAdmin" @click="showApprovalModal(order)" class="btn-primary">审批</button>
                  <button v-if="order.status === 'pending' && canOperateOrder(order)" @click="cancelOrder(order.id)" class="btn-warning">取消</button>

                  <!-- approved: 可以完成 -->
                  <button v-if="order.status === 'approved' && canOperateOrder(order)" @click="completeOrder(order.id)" class="btn-success">完成</button>
                  <button v-if="order.status === 'approved' && canOperateOrder(order)" @click="cancelOrder(order.id)" class="btn-warning">取消</button>
                </div>
                <div v-if="order.approval_comment" class="order-approval">
                  <strong>审批意见:</strong> {{ order.approval_comment }}
                  <span v-if="order.approver_name"> ({{ order.approver_name }})</span>
                </div>
              </div>
              <div v-if="filteredOrders.length === 0" class="empty-state">暂无订单</div>
            </div>
          </div>

          <!-- 通知中心 -->
          <div v-if="activeMenu === 'notifications'" class="notification-center">
            <div class="page-header">
              <h2>通知中心</h2>
              <button v-if="stats.unreadNotifications > 0" @click="markAllRead" class="btn-secondary">全部已读</button>
            </div>

            <div class="loading" v-if="loadingNotifications">加载中...</div>
            <div v-else class="notification-list">
              <div v-for="notif in notifications" :key="notif.id" :class="['notification-item', { unread: !notif.is_read }]">
                <div class="notif-header">
                  <span class="notif-type">{{ notifTypeText[notif.type] || notif.type }}</span>
                  <span class="notif-time">{{ formatDate(notif.created_at) }}</span>
                </div>
                <div class="notif-title">{{ notif.title }}</div>
                <div class="notif-content">{{ notif.content }}</div>
                <button v-if="!notif.is_read" @click="markRead(notif.id)" class="btn-small">标记已读</button>
              </div>
              <div v-if="notifications.length === 0" class="empty-state">暂无通知</div>
            </div>
          </div>

          <!-- 操作日志 -->
          <div v-if="activeMenu === 'logs'" class="log-management">
            <div class="page-header">
              <h2>操作日志</h2>
            </div>

            <div class="filter-bar">
              <select v-model="logFilters.action" class="filter-select">
                <option value="">全部操作</option>
                <option value="user.login">用户登录</option>
                <option value="user.create">创建用户</option>
                <option value="user.update">更新用户</option>
                <option value="user.delete">删除用户</option>
                <option value="order.create">创建订单</option>
                <option value="order.submit">提交订单</option>
                <option value="order.approve">审批通过</option>
                <option value="order.reject">审批拒绝</option>
                <option value="order.complete">完成订单</option>
                <option value="order.cancel">取消订单</option>
              </select>
            </div>

            <div class="loading" v-if="loadingLogs">加载中...</div>
            <table v-else class="data-table">
              <thead>
                <tr>
                  <th>时间</th>
                  <th>用户</th>
                  <th>操作</th>
                  <th>目标</th>
                  <th>详情</th>
                  <th>IP</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="log in filteredLogs" :key="log.id">
                  <td>{{ formatDate(log.created_at) }}</td>
                  <td>{{ log.username }}</td>
                  <td><span class="action-badge">{{ actionText[log.action] || log.action }}</span></td>
                  <td>{{ log.target_type }}: {{ log.target_id?.substring(0, 8) }}...</td>
                  <td>{{ formatDetail(log.detail) }}</td>
                  <td>{{ log.ip_address }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </main>
      </div>
    </div>

    <!-- 用户模态框 -->
    <div v-if="showUserModal" class="modal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>{{ editingUser ? '编辑用户' : '添加用户' }}</h3>
          <button @click="showUserModal = false" class="close-btn">&times;</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>用户名</label>
            <input v-model="userForm.username" type="text" placeholder="用户名" :disabled="!!editingUser" />
          </div>
          <div class="form-group">
            <label>密码 {{ editingUser ? '(不修改请留空)' : '' }}</label>
            <input v-model="userForm.password" type="password" :placeholder="editingUser ? '不修改请留空' : '密码'" />
          </div>
          <div class="form-group">
            <label>邮箱</label>
            <input v-model="userForm.email" type="email" placeholder="邮箱" />
          </div>
          <div class="form-group" v-if="isAdmin">
            <label>角色</label>
            <select v-model="userForm.role" class="filter-select">
              <option value="Viewer">访客</option>
              <option value="Operator">操作员</option>
              <option value="Admin">管理员</option>
            </select>
          </div>
          <div class="form-group" v-if="isAdmin">
            <label>等级</label>
            <select v-model="userForm.level" class="filter-select">
              <option value="normal">普通</option>
              <option value="vip">VIP</option>
            </select>
          </div>
          <div class="form-group" v-if="isAdmin">
            <label>组织</label>
            <input v-model="userForm.organization" type="text" placeholder="所属组织" />
          </div>
          <div class="form-group" v-if="isAdmin && editingUser">
            <label>状态</label>
            <select v-model="userForm.status" class="filter-select">
              <option value="active">正常</option>
              <option value="inactive">未激活</option>
              <option value="frozen">冻结</option>
            </select>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="showUserModal = false" class="btn-secondary">取消</button>
          <button @click="saveUser" class="btn-primary">{{ editingUser ? '保存' : '创建' }}</button>
        </div>
      </div>
    </div>

    <!-- 订单模态框 -->
    <div v-if="showOrderModal" class="modal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>{{ editingOrder ? '编辑订单' : '新建订单' }}</h3>
          <button @click="showOrderModal = false" class="close-btn">&times;</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>订单标题</label>
            <input v-model="orderForm.title" type="text" placeholder="订单标题" />
          </div>
          <div class="form-group">
            <label>订单描述</label>
            <textarea v-model="orderForm.description" placeholder="订单描述" rows="3"></textarea>
          </div>
          <div class="form-group">
            <label>金额 (元)</label>
            <input v-model.number="orderForm.amount" type="number" step="0.01" min="0" placeholder="金额" />
          </div>
        </div>
        <div class="modal-footer">
          <button @click="showOrderModal = false" class="btn-secondary">取消</button>
          <button @click="saveOrder" class="btn-primary">保存</button>
        </div>
      </div>
    </div>

    <!-- 审批模态框 -->
    <div v-if="showApprovalModalFlag" class="modal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>审批订单</h3>
          <button @click="showApprovalModalFlag = false" class="close-btn">&times;</button>
        </div>
        <div class="modal-body">
          <div class="order-summary">
            <p><strong>订单号:</strong> {{ approvalOrder?.order_no }}</p>
            <p><strong>标题:</strong> {{ approvalOrder?.title }}</p>
            <p><strong>金额:</strong> ¥{{ approvalOrder?.amount?.toFixed(2) }}</p>
            <p><strong>申请人:</strong> {{ approvalOrder?.creator_name }}</p>
          </div>
          <div class="form-group">
            <label>审批意见 (必填)</label>
            <textarea v-model="approvalComment" placeholder="请输入审批意见" rows="3"></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="showApprovalModalFlag = false" class="btn-secondary">取消</button>
          <button @click="rejectOrder(approvalOrder.id)" class="btn-danger">拒绝</button>
          <button @click="approveOrder(approvalOrder.id)" class="btn-success">通过</button>
        </div>
      </div>
    </div>

    <!-- 取消订单模态框 -->
    <div v-if="showCancelModal" class="modal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>取消订单</h3>
          <button @click="showCancelModal = false" class="close-btn">&times;</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>取消原因 (可选)</label>
            <textarea v-model="cancelReason" placeholder="请输入取消原因" rows="3"></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="showCancelModal = false" class="btn-secondary">返回</button>
          <button @click="confirmCancelOrder" class="btn-warning">确认取消</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'

export default {
  name: 'App',
  setup() {
    // 状态
    const isLoggedIn = ref(false)
    const loading = ref(false)
    const loginForm = ref({ username: '', password: '' })
    const errorMsg = ref('')
    const currentUser = ref(null)
    const token = ref('')

    // 菜单
    const activeMenu = ref('dashboard')

    // 用户相关
    const users = ref([])
    const loadingUsers = ref(false)
    const usersPage = ref(1)
    const usersPageSize = ref(10)
    const usersTotal = ref(0)
    const userFilters = ref({ status: '', role: '' })
    const showUserModal = ref(false)
    const editingUser = ref(null)
    const userForm = ref({ username: '', password: '', email: '', role: 'Viewer', level: 'normal', organization: '', status: 'active' })

    // 订单相关
    const orders = ref([])
    const loadingOrders = ref(false)
    const orderFilters = ref({ status: '' })
    const showOrderModal = ref(false)
    const editingOrder = ref(null)
    const orderForm = ref({ title: '', description: '', amount: 0 })
    const showApprovalModalFlag = ref(false)
    const approvalOrder = ref(null)
    const approvalComment = ref('')
    const showCancelModal = ref(false)
    const cancellingOrderId = ref(null)
    const cancelReason = ref('')

    // 通知相关
    const notifications = ref([])
    const loadingNotifications = ref(false)

    // 日志相关
    const logs = ref([])
    const loadingLogs = ref(false)
    const logFilters = ref({ action: '' })

    // 统计数据
    const stats = computed(() => {
      const pendingOrders = orders.value.filter(o => o.status === 'pending').length
      const totalOrders = orders.value.length
      const unreadNotifications = notifications.value.filter(n => !n.is_read).length
      return {
        totalUsers: usersTotal.value,
        totalOrders,
        pendingOrders,
        unreadNotifications,
      }
    })

    // 权限判断
    const isAdmin = computed(() => currentUser.value?.role === 'Admin')
    const isOperator = computed(() => currentUser.value?.role === 'Operator')
    const isViewer = computed(() => currentUser.value?.role === 'Viewer')

    // 可见菜单
    const visibleMenus = computed(() => {
      const menus = [
        { id: 'dashboard', name: '仪表盘', icon: '📊' },
        { id: 'orders', name: '订单管理', icon: '📋' },
        { id: 'notifications', name: '通知中心', icon: '🔔' },
      ]
      if (isAdmin.value || isOperator.value) {
        menus.push({ id: 'users', name: '用户管理', icon: '👥' })
      }
      if (isAdmin.value || isOperator.value) {
        menus.push({ id: 'logs', name: '操作日志', icon: '📝' })
      }
      return menus
    })

    // 过滤后的用户
    const filteredUsers = computed(() => {
      return users.value.filter(u => {
        if (userFilters.value.status && u.status !== userFilters.value.status) return false
        if (userFilters.value.role && u.role !== userFilters.value.role) return false
        return true
      })
    })

    // 过滤后的订单
    const filteredOrders = computed(() => {
      if (orderFilters.value.status) {
        return orders.value.filter(o => o.status === orderFilters.value.status)
      }
      return orders.value
    })

    // 过滤后的日志
    const filteredLogs = computed(() => {
      if (logFilters.value.action) {
        return logs.value.filter(l => l.action === logFilters.value.action)
      }
      return logs.value
    })

    // 状态文本映射
    const statusText = {
      draft: '草稿',
      pending: '待审核',
      approved: '已通过',
      rejected: '已拒绝',
      completed: '已完成',
      cancelled: '已取消',
      active: '正常',
      inactive: '未激活',
      frozen: '冻结',
    }

    const notifTypeText = {
      order_created: '订单创建',
      order_submitted: '订单提交',
      order_approved: '审批通过',
      order_rejected: '审批拒绝',
      order_completed: '订单完成',
      order_cancelled: '订单取消',
    }

    const actionText = {
      'user.login': '登录',
      'user.logout': '退出',
      'user.create': '创建用户',
      'user.update': '更新用户',
      'user.delete': '删除用户',
      'order.create': '创建订单',
      'order.update': '更新订单',
      'order.submit': '提交订单',
      'order.approve': '审批通过',
      'order.reject': '审批拒绝',
      'order.complete': '完成订单',
      'order.cancel': '取消订单',
    }

    // API 请求
    const api = (url, options = {}) => {
      return fetch(url, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token.value}`,
          ...options.headers,
        },
      }).then(res => res.json())
    }

    // 登录
    const login = async () => {
      if (!loginForm.value.username || !loginForm.value.password) {
        errorMsg.value = '请输入用户名和密码'
        return
      }
      loading.value = true
      errorMsg.value = ''
      try {
        const res = await fetch('/api/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(loginForm.value),
        })
        const data = await res.json()
        if (data.code === 200) {
          token.value = data.data.token
          localStorage.setItem('token', token.value)
          currentUser.value = data.data
          isLoggedIn.value = true
          await fetchUserInfo()
          await fetchOrders()
          await fetchNotifications()
        } else {
          errorMsg.value = data.msg || '登录失败'
        }
      } catch (e) {
        errorMsg.value = '网络错误，请检查连接'
      } finally {
        loading.value = false
      }
    }

    // 退出登录
    const logout = async () => {
      try {
        await api('/api/auth/logout', { method: 'POST' })
      } catch (e) {}
      localStorage.removeItem('token')
      token.value = ''
      currentUser.value = null
      isLoggedIn.value = false
      loginForm.value = { username: '', password: '' }
      users.value = []
      orders.value = []
      notifications.value = []
      logs.value = []
    }

    // 获取当前用户信息
    const fetchUserInfo = async () => {
      try {
        const data = await api('/api/v1/user')
        if (data.code === 200) {
          currentUser.value = { ...currentUser.value, ...data.data }
        }
      } catch (e) {
        console.error('获取用户信息失败', e)
      }
    }

    // 获取用户列表
    const fetchUsers = async () => {
      loadingUsers.value = true
      try {
        const data = await api(`/api/v1/users?page=${usersPage.value}&page_size=${usersPageSize.value}`)
        if (data.code === 200) {
          users.value = data.data.list
          usersTotal.value = data.data.total
        }
      } catch (e) {
        console.error('获取用户列表失败', e)
      } finally {
        loadingUsers.value = false
      }
    }

    // 编辑用户
    const editUser = (user) => {
      editingUser.value = user
      userForm.value = {
        username: user.username,
        password: '',
        email: user.email || '',
        role: user.role,
        level: user.level,
        organization: user.organization || '',
        status: user.status,
      }
      showUserModal.value = true
    }

    // 保存用户
    const saveUser = async () => {
      try {
        let data
        if (editingUser.value) {
          const updateData = { ...userForm.value }
          if (!updateData.password) delete updateData.password
          data = await api(`/api/v1/users/${editingUser.value.id}`, {
            method: 'PUT',
            body: JSON.stringify(updateData),
          })
        } else {
          if (!userForm.value.username || !userForm.value.password) {
            alert('用户名和密码必填')
            return
          }
          data = await api('/api/v1/users', {
            method: 'POST',
            body: JSON.stringify(userForm.value),
          })
        }
        if (data.code === 200) {
          showUserModal.value = false
          await fetchUsers()
        } else {
          alert(data.msg)
        }
      } catch (e) {
        alert('操作失败')
      }
    }

    // 删除用户
    const deleteUser = async (userId) => {
      if (!confirm('确定要删除此用户吗？')) return
      try {
        const data = await api(`/api/v1/users/${userId}`, { method: 'DELETE' })
        if (data.code === 200) {
          await fetchUsers()
        } else {
          alert(data.msg)
        }
      } catch (e) {
        alert('删除失败')
      }
    }

    // 获取订单列表
    const fetchOrders = async () => {
      loadingOrders.value = true
      try {
        const url = isAdmin.value ? `/api/v1/admin/orders?page=1&page_size=100` : `/api/v1/orders?page=1&page_size=100`
        const data = await api(url)
        if (data.code === 200) {
          orders.value = data.data.list
        }
      } catch (e) {
        console.error('获取订单失败', e)
      } finally {
        loadingOrders.value = false
      }
    }

    // 获取所有订单 (Admin)
    const fetchAllOrders = async () => {
      loadingOrders.value = true
      try {
        const data = await api('/api/v1/admin/orders?page=1&page_size=100')
        if (data.code === 200) {
          orders.value = data.data.list
        }
      } catch (e) {
        console.error('获取订单失败', e)
      } finally {
        loadingOrders.value = false
      }
    }

    // 能否操作订单
    const canOperateOrder = (order) => {
      if (isAdmin.value) return true
      return order.user_id === currentUser.value?.id
    }

    // 创建订单
    const createOrder = async () => {
      orderForm.value = { title: '', description: '', amount: 0 }
      editingOrder.value = null
      showOrderModal.value = true
    }

    // 编辑订单
    const editOrder = (order) => {
      editingOrder.value = order
      orderForm.value = {
        title: order.title,
        description: order.description || '',
        amount: order.amount,
      }
      showOrderModal.value = true
    }

    // 保存订单
    const saveOrder = async () => {
      if (!orderForm.value.title) {
        alert('订单标题必填')
        return
      }
      if (!orderForm.value.amount || orderForm.value.amount <= 0) {
        alert('订单金额必须大于0')
        return
      }
      try {
        let data
        if (editingOrder.value) {
          data = await api(`/api/v1/orders/${editingOrder.value.id}`, {
            method: 'PUT',
            body: JSON.stringify(orderForm.value),
          })
        } else {
          data = await api('/api/v1/orders', {
            method: 'POST',
            body: JSON.stringify(orderForm.value),
          })
        }
        if (data.code === 200) {
          showOrderModal.value = false
          await fetchOrders()
          await fetchNotifications()
        } else {
          alert(data.msg)
        }
      } catch (e) {
        alert('操作失败')
      }
    }

    // 提交订单
    const submitOrder = async (orderId) => {
      try {
        const data = await api(`/api/v1/orders/${orderId}/submit`, { method: 'POST' })
        if (data.code === 200) {
          await fetchOrders()
          await fetchNotifications()
        } else {
          alert(data.msg)
        }
      } catch (e) {
        alert('提交失败')
      }
    }

    // 审批模态框
    const showApprovalModal = (order) => {
      approvalOrder.value = order
      approvalComment.value = ''
      showApprovalModalFlag.value = true
    }

    // 审批通过
    const approveOrder = async (orderId) => {
      if (!approvalComment.value.trim()) {
        alert('审批意见必填')
        return
      }
      try {
        const data = await api(`/api/v1/orders/${orderId}/approve`, {
          method: 'POST',
          body: JSON.stringify({ comment: approvalComment.value }),
        })
        if (data.code === 200) {
          showApprovalModalFlag.value = false
          await fetchOrders()
          await fetchNotifications()
          await fetchLogs()
        } else {
          alert(data.msg)
        }
      } catch (e) {
        alert('审批失败')
      }
    }

    // 审批拒绝
    const rejectOrder = async (orderId) => {
      if (!approvalComment.value.trim()) {
        alert('审批意见必填')
        return
      }
      try {
        const data = await api(`/api/v1/orders/${orderId}/reject`, {
          method: 'POST',
          body: JSON.stringify({ comment: approvalComment.value }),
        })
        if (data.code === 200) {
          showApprovalModalFlag.value = false
          await fetchOrders()
          await fetchNotifications()
          await fetchLogs()
        } else {
          alert(data.msg)
        }
      } catch (e) {
        alert('审批失败')
      }
    }

    // 完成订单
    const completeOrder = async (orderId) => {
      try {
        const data = await api(`/api/v1/orders/${orderId}/complete`, { method: 'POST' })
        if (data.code === 200) {
          await fetchOrders()
          await fetchNotifications()
        } else {
          alert(data.msg)
        }
      } catch (e) {
        alert('操作失败')
      }
    }

    // 取消订单
    const cancelOrder = (orderId) => {
      cancellingOrderId.value = orderId
      cancelReason.value = ''
      showCancelModal.value = true
    }

    // 确认取消订单
    const confirmCancelOrder = async () => {
      try {
        const data = await api(`/api/v1/orders/${cancellingOrderId.value}/cancel`, {
          method: 'POST',
          body: JSON.stringify({ reason: cancelReason.value }),
        })
        if (data.code === 200) {
          showCancelModal.value = false
          await fetchOrders()
          await fetchNotifications()
        } else {
          alert(data.msg)
        }
      } catch (e) {
        alert('取消失败')
      }
    }

    // 获取通知列表
    const fetchNotifications = async () => {
      loadingNotifications.value = true
      try {
        const data = await api('/api/v1/notifications?page=1&page_size=50')
        if (data.code === 200) {
          notifications.value = data.data.list
        }
      } catch (e) {
        console.error('获取通知失败', e)
      } finally {
        loadingNotifications.value = false
      }
    }

    // 标记通知已读
    const markRead = async (notifId) => {
      try {
        await api(`/api/v1/notifications/${notifId}/read`, { method: 'PUT' })
        await fetchNotifications()
      } catch (e) {
        console.error('标记已读失败', e)
      }
    }

    // 全部标记已读
    const markAllRead = async () => {
      try {
        await api('/api/v1/notifications/read-all', { method: 'PUT' })
        await fetchNotifications()
      } catch (e) {
        console.error('标记已读失败', e)
      }
    }

    // 获取日志列表
    const fetchLogs = async () => {
      loadingLogs.value = true
      try {
        const data = await api('/api/v1/logs?page=1&page_size=50')
        if (data.code === 200) {
          logs.value = data.data.list
        }
      } catch (e) {
        console.error('获取日志失败', e)
      } finally {
        loadingLogs.value = false
      }
    }

    // 格式化日期
    const formatDate = (dateStr) => {
      if (!dateStr) return '-'
      const d = new Date(dateStr)
      return d.toLocaleString('zh-CN', { hour12: false })
    }

    // 格式化详情
    const formatDetail = (detail) => {
      if (!detail) return '-'
      if (detail.order_no) return `订单号: ${detail.order_no}`
      if (detail.username) return `用户: ${detail.username}`
      if (detail.updated_fields) return `更新: ${detail.updated_fields.join(', ')}`
      return JSON.stringify(detail).substring(0, 50)
    }

    // 菜单和 URL 的映射关系
    const menuToPath = {
      'dashboard': '/dashboard',
      'users': '/users',
      'orders': '/orders',
      'notifications': '/notifications',
      'logs': '/logs',
    }

    const pathToMenu = {
      '/dashboard': 'dashboard',
      '/users': 'users',
      '/orders': 'orders',
      '/notifications': 'notifications',
      '/logs': 'logs',
    }

    // 根据 URL 设置菜单
    const setMenuFromURL = () => {
      const path = window.location.pathname
      const menu = pathToMenu[path]
      if (menu && visibleMenus.value.find(m => m.id === menu)) {
        activeMenu.value = menu
      }
    }

    // 根据菜单更新 URL
    const updateURLFromMenu = (menu) => {
      const path = menuToPath[menu]
      if (path) {
        window.history.pushState({ menu }, '', path)
      }
    }

    // 监听浏览器前进/后退
    window.addEventListener('popstate', (event) => {
      if (event.state?.menu) {
        activeMenu.value = event.state.menu
      } else {
        setMenuFromURL()
      }
    })

    // 监听菜单变化
    watch(activeMenu, async (menu) => {
      updateURLFromMenu(menu)
      if (menu === 'users' && (isAdmin.value || isOperator.value)) {
        await fetchUsers()
      } else if (menu === 'logs' && (isAdmin.value || isOperator.value)) {
        await fetchLogs()
      }
    })

    // 监听用户分页
    watch(usersPage, () => fetchUsers())

    // 初始化
    onMounted(() => {
      const savedToken = localStorage.getItem('token')
      if (savedToken) {
        token.value = savedToken
        isLoggedIn.value = true
        fetchUserInfo().then(() => {
          fetchOrders()
          fetchNotifications()
          // 登录后根据 URL 设置菜单
          setMenuFromURL()
        })
      } else {
        // 未登录时根据 URL 设置菜单（虽然显示的是登录页）
        setMenuFromURL()
      }
    })

    return {
      isLoggedIn,
      loading,
      loginForm,
      errorMsg,
      currentUser,
      activeMenu,
      visibleMenus,
      isAdmin,
      isOperator,
      isViewer,
      users,
      loadingUsers,
      usersPage,
      usersTotal,
      usersPageSize,
      userFilters,
      filteredUsers,
      showUserModal,
      editingUser,
      userForm,
      orders,
      loadingOrders,
      orderFilters,
      filteredOrders,
      showOrderModal,
      editingOrder,
      orderForm,
      showApprovalModalFlag,
      approvalOrder,
      approvalComment,
      showCancelModal,
      cancelReason,
      notifications,
      loadingNotifications,
      logs,
      loadingLogs,
      logFilters,
      filteredLogs,
      stats,
      statusText,
      notifTypeText,
      actionText,
      login,
      logout,
      editUser,
      saveUser,
      deleteUser,
      fetchAllOrders,
      canOperateOrder,
      createOrder,
      editOrder,
      saveOrder,
      submitOrder,
      showApprovalModal,
      approveOrder,
      rejectOrder,
      completeOrder,
      cancelOrder,
      confirmCancelOrder,
      markRead,
      markAllRead,
      formatDate,
      formatDetail,
    }
  }
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background-color: #f5f6f8;
  color: #333;
}

.app {
  min-height: 100vh;
}

/* 登录页 */
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-form {
  background: white;
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0,0,0,0.2);
  width: 100%;
  max-width: 400px;
}

.login-form h2 {
  text-align: center;
  margin-bottom: 30px;
  color: #333;
}

.demo-info {
  margin-top: 20px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
  font-size: 13px;
}

.demo-accounts {
  margin-top: 10px;
  line-height: 1.8;
}

.demo-accounts div {
  color: #666;
}

/* 表单 */
.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
  color: #555;
}

.form-group input,
.form-group textarea,
.form-group select {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.form-group input:focus,
.form-group textarea:focus,
.form-group select:focus {
  outline: none;
  border-color: #667eea;
}

.login-btn {
  width: 100%;
  padding: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: opacity 0.2s;
}

.login-btn:hover {
  opacity: 0.9;
}

.login-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error-msg {
  color: #e74c3c;
  text-align: center;
  margin-top: 15px;
  font-size: 14px;
}

/* 主应用 */
.main-app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* 导航栏 */
.navbar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 0 30px;
  height: 60px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.navbar-brand {
  font-size: 20px;
  font-weight: 600;
}

.navbar-user {
  display: flex;
  align-items: center;
  gap: 20px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.role-badge {
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.role-badge.admin {
  background: #e74c3c;
  color: white;
}

.role-badge.operator {
  background: #3498db;
  color: white;
}

.role-badge.viewer {
  background: #95a5a6;
  color: white;
}

.level-badge {
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.level-badge.vip {
  background: #f1c40f;
  color: #333;
}

.level-badge.normal {
  background: #ecf0f1;
  color: #666;
}

.logout-btn {
  background: rgba(255,255,255,0.2);
  color: white;
  border: 1px solid rgba(255,255,255,0.3);
  padding: 6px 16px;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.2s;
}

.logout-btn:hover {
  background: rgba(255,255,255,0.3);
}

/* 主内容 */
.main-content {
  display: flex;
  flex: 1;
}

/* 侧边栏 */
.sidebar {
  width: 200px;
  background: white;
  border-right: 1px solid #e8e8e8;
  padding: 20px 0;
}

.nav-menu {
  list-style: none;
}

.nav-item {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  cursor: pointer;
  color: #666;
  transition: all 0.2s;
  border-left: 3px solid transparent;
}

.nav-item:hover {
  background: #f5f6f8;
  color: #333;
}

.nav-item.active {
  background: #f0edff;
  color: #667eea;
  border-left-color: #667eea;
}

.nav-icon {
  margin-right: 10px;
  font-size: 18px;
}

/* 内容区域 */
.content-area {
  flex: 1;
  padding: 30px;
  overflow-y: auto;
  max-height: calc(100vh - 60px);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  font-size: 24px;
  color: #333;
}

/* 仪表盘 */
.dashboard h2 {
  margin-bottom: 20px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.stat-card {
  background: white;
  padding: 24px;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.stat-label {
  font-size: 14px;
  color: #888;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 32px;
  font-weight: 600;
  color: #333;
}

.stat-value.warning {
  color: #f39c12;
}

.stat-value.info {
  color: #3498db;
}

/* 表格 */
.data-table {
  width: 100%;
  background: white;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.data-table th,
.data-table td {
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.data-table th {
  background: #f8f9fa;
  font-weight: 600;
  color: #555;
}

.data-table tr:hover {
  background: #fafafa;
}

/* 筛选栏 */
.filter-bar {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
}

.filter-select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  background: white;
  cursor: pointer;
}

/* 按钮 */
.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: opacity 0.2s;
}

.btn-primary:hover {
  opacity: 0.9;
}

.btn-secondary {
  background: #ecf0f1;
  color: #333;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

.btn-secondary:hover {
  background: #dfe6e9;
}

.btn-success {
  background: #27ae60;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

.btn-danger {
  background: #e74c3c;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

.btn-warning {
  background: #f39c12;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

.btn-edit {
  background: #3498db;
  color: white;
  border: none;
  padding: 5px 10px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  margin-right: 5px;
}

.btn-small {
  background: #ecf0f1;
  color: #333;
  border: none;
  padding: 4px 10px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  margin-top: 10px;
}

/* 状态徽章 */
.status-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.active {
  background: #d4edda;
  color: #155724;
}

.status-badge.inactive {
  background: #fff3cd;
  color: #856404;
}

.status-badge.frozen {
  background: #f8d7da;
  color: #721c24;
}

.status-badge.draft {
  background: #e2e3e5;
  color: #383d41;
}

.status-badge.pending {
  background: #fff3cd;
  color: #856404;
}

.status-badge.approved {
  background: #d4edda;
  color: #155724;
}

.status-badge.rejected {
  background: #f8d7da;
  color: #721c24;
}

.status-badge.completed {
  background: #c3e6cb;
  color: #155724;
}

.status-badge.cancelled {
  background: #e2e3e5;
  color: #383d41;
}

/* 操作徽章 */
.action-badge {
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 12px;
  background: #e9ecef;
  color: #495057;
}

/* 分页 */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 15px;
  margin-top: 20px;
}

.pagination button {
  padding: 8px 16px;
  border: 1px solid #ddd;
  background: white;
  border-radius: 6px;
  cursor: pointer;
}

.pagination button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 订单卡片 */
.order-list {
  display: grid;
  gap: 15px;
}

.order-card {
  background: white;
  border-radius: 10px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.order-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.order-no {
  font-weight: 600;
  color: #333;
  font-family: monospace;
}

.order-body h3 {
  margin-bottom: 8px;
  color: #333;
}

.order-body p {
  color: #666;
  margin-bottom: 10px;
}

.order-meta {
  display: flex;
  gap: 20px;
  font-size: 13px;
  color: #888;
}

.order-actions {
  display: flex;
  gap: 10px;
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #eee;
}

.order-approval {
  margin-top: 15px;
  padding: 10px;
  background: #f8f9fa;
  border-radius: 6px;
  font-size: 13px;
  color: #666;
}

.order-summary {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 15px;
}

.order-summary p {
  margin-bottom: 8px;
}

/* 通知 */
.notification-list {
  display: grid;
  gap: 10px;
}

.notification-item {
  background: white;
  padding: 15px 20px;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.05);
  border-left: 4px solid #ddd;
}

.notification-item.unread {
  border-left-color: #667eea;
  background: #f8f9ff;
}

.notif-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.notif-type {
  font-size: 12px;
  color: #667eea;
  font-weight: 500;
}

.notif-time {
  font-size: 12px;
  color: #888;
}

.notif-title {
  font-weight: 500;
  margin-bottom: 5px;
}

.notif-content {
  color: #666;
  font-size: 14px;
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 40px;
  color: #999;
  background: white;
  border-radius: 10px;
}

.loading {
  text-align: center;
  padding: 40px;
  color: #999;
}

/* 模态框 */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 25px;
  border-radius: 12px;
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.modal-header h3 {
  font-size: 18px;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #999;
}

.close-btn:hover {
  color: #333;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

/* 响应式 */
@media (max-width: 768px) {
  .sidebar {
    width: 60px;
  }

  .nav-text {
    display: none;
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .content-area {
    padding: 15px;
  }
}
</style>
