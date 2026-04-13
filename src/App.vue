<template>
  <div class="app">
    <!-- 登录页面 -->
    <div v-if="!isLoggedIn" class="login-container">
      <div class="login-form">
        <h2>用户登录</h2>
        <div class="form-group">
          <label>用户名</label>
          <input v-model="loginForm.username" type="text" placeholder="请输入用户名" />
        </div>
        <div class="form-group">
          <label>密码</label>
          <input v-model="loginForm.password" type="password" placeholder="请输入密码" />
        </div>
        <button @click="login" class="login-btn">登录</button>
        <p v-if="errorMsg" class="error-msg">{{ errorMsg }}</p>
        <p class="demo-info">
          演示账号：<br>
          admin / admin123<br>
          test / test123
        </p>
      </div>
    </div>

    <!-- 主应用 -->
    <div v-else class="main-app">
      <!-- 导航栏 -->
      <nav class="navbar">
        <div class="navbar-brand">用户管理系统</div>
        <div class="navbar-actions">
          <span>欢迎，{{ currentUser?.username }}</span>
          <button @click="logout" class="logout-btn">退出登录</button>
        </div>
      </nav>

      <!-- 内容区域 -->
      <div class="content">
        <!-- 标签页 -->
        <div class="tabs">
          <button 
            v-for="tab in tabs" 
            :key="tab.id" 
            :class="['tab-btn', { active: activeTab === tab.id }]"
            @click="activeTab = tab.id"
          >
            {{ tab.name }}
          </button>
        </div>

        <!-- 内容区域 -->
        <div class="tab-content">
          <!-- 仪表盘 -->
          <div v-if="activeTab === 'dashboard'" class="dashboard">
            <h3>仪表盘</h3>
            <div class="stats">
              <div class="stat-card">
                <div class="stat-title">用户总数</div>
                <div class="stat-value">{{ users.length }}</div>
              </div>
              <div class="stat-card">
                <div class="stat-title">当前用户</div>
                <div class="stat-value">{{ currentUser?.username }}</div>
              </div>
            </div>
          </div>

          <!-- 用户列表 -->
          <div v-else-if="activeTab === 'users'" class="users">
            <div class="users-header">
              <h3>用户管理</h3>
              <button @click="showAddUserForm = true" class="add-user-btn">添加用户</button>
            </div>
            <div class="users-list">
              <table>
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>用户名</th>
                    <th>邮箱</th>
                    <th>操作</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="user in users" :key="user.id">
                    <td>{{ user.id }}</td>
                    <td>{{ user.username }}</td>
                    <td>{{ user.email }}</td>
                    <td>
                      <button @click="editUser(user)" class="edit-btn">编辑</button>
                      <button @click="deleteUser(user.id)" class="delete-btn">删除</button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- 个人信息 -->
          <div v-else-if="activeTab === 'profile'" class="profile">
            <h3>个人信息</h3>
            <div class="profile-info">
              <div class="info-item">
                <label>用户ID：</label>
                <span>{{ currentUser?.id }}</span>
              </div>
              <div class="info-item">
                <label>用户名：</label>
                <span>{{ currentUser?.username }}</span>
              </div>
              <div class="info-item">
                <label>邮箱：</label>
                <span>{{ currentUser?.email }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 添加/编辑用户模态框 -->
    <div v-if="showAddUserForm || showEditUserForm" class="modal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>{{ showEditUserForm ? '编辑用户' : '添加用户' }}</h3>
          <button @click="closeModal" class="close-btn">&times;</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>用户名</label>
            <input v-model="userForm.username" type="text" placeholder="请输入用户名" />
          </div>
          <div class="form-group">
            <label>邮箱</label>
            <input v-model="userForm.email" type="email" placeholder="请输入邮箱" />
          </div>
          <div class="form-group">
            <label>密码</label>
            <input v-model="userForm.password" type="password" placeholder="请输入密码" />
          </div>
        </div>
        <div class="modal-footer">
          <button @click="closeModal" class="cancel-btn">取消</button>
          <button @click="saveUser" class="save-btn">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'

export default {
  name: 'App',
  setup() {
    // 状态
    const isLoggedIn = ref(false)
    const loginForm = ref({ username: '', password: '' })
    const userForm = ref({ username: '', email: '', password: '' })
    const errorMsg = ref('')
    const currentUser = ref(null)
    const users = ref([])
    const activeTab = ref('dashboard')
    const showAddUserForm = ref(false)
    const showEditUserForm = ref(false)
    const editingUserId = ref(null)
    
    // 标签页
    const tabs = [
      { id: 'dashboard', name: '仪表盘' },
      { id: 'users', name: '用户管理' },
      { id: 'profile', name: '个人信息' }
    ]

    // 登录
    const login = async () => {
      try {
        const response = await fetch('/api/auth/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(loginForm.value)
        })
        
        const data = await response.json()
        if (data.code === 200) {
          localStorage.setItem('token', data.data.token)
          isLoggedIn.value = true
          errorMsg.value = ''
          await fetchCurrentUser()
          await fetchUsers()
        } else {
          errorMsg.value = data.msg
        }
      } catch (error) {
        errorMsg.value = '登录失败，请检查网络连接'
      }
    }

    // 退出登录
    const logout = () => {
      localStorage.removeItem('token')
      isLoggedIn.value = false
      currentUser.value = null
      users.value = []
      loginForm.value = { username: '', password: '' }
    }

    // 获取当前用户信息
    const fetchCurrentUser = async () => {
      try {
        const token = localStorage.getItem('token')
        const response = await fetch('/api/api/v1/user', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })
        
        const data = await response.json()
        if (data.code === 200) {
          currentUser.value = data.data
        }
      } catch (error) {
        console.error('获取用户信息失败', error)
      }
    }

    // 获取用户列表
    const fetchUsers = async () => {
      try {
        const token = localStorage.getItem('token')
        const response = await fetch('/api/api/v1/users', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })
        
        const data = await response.json()
        if (data.code === 200) {
          users.value = data.data.list
        }
      } catch (error) {
        console.error('获取用户列表失败', error)
      }
    }

    // 添加用户
    const saveUser = async () => {
      try {
        const token = localStorage.getItem('token')
        const url = showEditUserForm.value 
          ? `/api/api/v1/users/${editingUserId.value}` 
          : '/api/api/v1/users'
        
        const method = showEditUserForm.value ? 'PUT' : 'POST'
        
        const response = await fetch(url, {
          method,
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify(userForm.value)
        })
        
        const data = await response.json()
        if (data.code === 200) {
          await fetchUsers()
          closeModal()
        } else {
          alert(data.msg)
        }
      } catch (error) {
        console.error('保存用户失败', error)
        alert('保存失败，请检查网络连接')
      }
    }

    // 编辑用户
    const editUser = (user) => {
      userForm.value = { ...user }
      editingUserId.value = user.id
      showEditUserForm.value = true
    }

    // 删除用户
    const deleteUser = async (userId) => {
      if (confirm('确定要删除这个用户吗？')) {
        try {
          const token = localStorage.getItem('token')
          const response = await fetch(`/api/api/v1/users/${userId}`, {
            method: 'DELETE',
            headers: {
              'Authorization': `Bearer ${token}`
            }
          })
          
          const data = await response.json()
          if (data.code === 200) {
            await fetchUsers()
          } else {
            alert(data.msg)
          }
        } catch (error) {
          console.error('删除用户失败', error)
          alert('删除失败，请检查网络连接')
        }
      }
    }

    // 关闭模态框
    const closeModal = () => {
      showAddUserForm.value = false
      showEditUserForm.value = false
      userForm.value = { username: '', email: '', password: '' }
      editingUserId.value = null
    }

    // 初始化
    onMounted(() => {
      const token = localStorage.getItem('token')
      if (token) {
        isLoggedIn.value = true
        fetchCurrentUser()
        fetchUsers()
      }
    })

    return {
      isLoggedIn,
      loginForm,
      userForm,
      errorMsg,
      currentUser,
      users,
      activeTab,
      tabs,
      showAddUserForm,
      showEditUserForm,
      login,
      logout,
      saveUser,
      editUser,
      deleteUser,
      closeModal
    }
  }
}
</script>

<style>
/* 全局样式 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: Arial, sans-serif;
  background-color: #f0f2f5;
}

.app {
  min-height: 100vh;
}

/* 登录页面 */
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f0f2f5;
}

.login-form {
  background-color: white;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
}

.login-form h2 {
  text-align: center;
  margin-bottom: 20px;
  color: #333;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
  color: #555;
}

.form-group input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
}

.login-btn {
  width: 100%;
  padding: 10px;
  background-color: #1890ff;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  margin-top: 10px;
}

.login-btn:hover {
  background-color: #40a9ff;
}

.error-msg {
  color: red;
  text-align: center;
  margin-top: 10px;
}

.demo-info {
  margin-top: 20px;
  text-align: center;
  font-size: 14px;
  color: #666;
}

/* 主应用 */
.main-app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* 导航栏 */
.navbar {
  background-color: #1890ff;
  color: white;
  padding: 15px 30px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.navbar-brand {
  font-size: 20px;
  font-weight: bold;
}

.navbar-actions {
  display: flex;
  align-items: center;
  gap: 20px;
}

.logout-btn {
  background-color: transparent;
  color: white;
  border: 1px solid white;
  padding: 5px 15px;
  border-radius: 4px;
  cursor: pointer;
}

.logout-btn:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

/* 内容区域 */
.content {
  flex: 1;
  padding: 30px;
  background-color: #f0f2f5;
}

/* 标签页 */
.tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  background-color: white;
  padding: 10px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.tab-btn {
  padding: 10px 20px;
  border: none;
  background-color: transparent;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  color: #666;
}

.tab-btn.active {
  background-color: #1890ff;
  color: white;
}

/* 标签内容 */
.tab-content {
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  min-height: 400px;
}

/* 仪表盘 */
.dashboard h3 {
  margin-bottom: 20px;
  color: #333;
}

.stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.stat-card {
  background-color: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
  text-align: center;
  border: 1px solid #ddd;
}

.stat-title {
  font-size: 14px;
  color: #666;
  margin-bottom: 10px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #1890ff;
}

/* 用户管理 */
.users-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.users-header h3 {
  color: #333;
}

.add-user-btn {
  padding: 8px 16px;
  background-color: #52c41a;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.add-user-btn:hover {
  background-color: #73d13d;
}

.users-list table {
  width: 100%;
  border-collapse: collapse;
}

.users-list th,
.users-list td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

.users-list th {
  background-color: #f5f5f5;
  font-weight: bold;
  color: #333;
}

.users-list tr:hover {
  background-color: #f9f9f9;
}

.edit-btn {
  padding: 5px 10px;
  background-color: #1890ff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-right: 5px;
}

.edit-btn:hover {
  background-color: #40a9ff;
}

.delete-btn {
  padding: 5px 10px;
  background-color: #ff4d4f;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.delete-btn:hover {
  background-color: #ff7875;
}

/* 个人信息 */
.profile h3 {
  margin-bottom: 20px;
  color: #333;
}

.profile-info {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 10px;
  background-color: #f9f9f9;
  border-radius: 4px;
}

.info-item label {
  font-weight: bold;
  color: #555;
  width: 100px;
}

/* 模态框 */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.modal-header h3 {
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
}

.modal-body {
  margin-bottom: 20px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.cancel-btn {
  padding: 8px 16px;
  background-color: #f5f5f5;
  color: #333;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
}

.save-btn {
  padding: 8px 16px;
  background-color: #1890ff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.save-btn:hover {
  background-color: #40a9ff;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .content {
    padding: 15px;
  }
  
  .navbar {
    padding: 10px 15px;
  }
  
  .tabs {
    flex-wrap: wrap;
  }
  
  .tab-btn {
    flex: 1;
    min-width: 100px;
  }
  
  .users-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .stats {
    grid-template-columns: 1fr;
  }
}
</style>