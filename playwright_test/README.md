# Playwright 自动化测试框架

基于 Python + Playwright + POM + 数据驱动的自动化测试框架，支持 Allure 报告。

## 项目结构

```
playwright_test/
├── pages/              # Page Objects
│   ├── base_page.py       # 基础页面类
│   ├── login_page.py      # 登录页面
│   └── main_page.py       # 主页面（仪表盘、用户管理、个人信息）
├── tests/             # 测试用例
│   ├── conftest.py        # Pytest 配置和 fixtures
│   ├── test_login.py      # 登录测试
│   ├── test_user_management.py  # 用户管理测试
│   └── test_navigation.py # 导航测试
├── data/              # 测试数据
│   ├── test_data.yaml     # 测试数据
│   └── env_config.yaml    # 环境配置
├── utils/             # 工具函数
│   └── helpers.py         # 辅助函数
├── fixtures/          # Pytest fixtures
│   └── fixtures.py        # 通用 fixtures
├── config/            # 配置管理
│   └── config.py          # 配置类
├── reports/           # 测试报告（自动生成）
├── allure-results/    # Allure 原始结果（自动生成）
├── pytest.ini         # Pytest 配置
├── requirements.txt   # Python 依赖
└── run_tests.sh      # 运行脚本
```

## 快速开始

### 1. 安装依赖

```bash
cd playwright_test
pip install -r requirements.txt
playwright install
```

### 2. 配置环境

编辑 `data/env_config.yaml` 配置测试环境：

```yaml
test:
  base_url: "http://localhost:3000"
  timeout: 30000
  headless: false
  browser_type: "chromium"
```

### 3. 运行测试

#### 使用运行脚本（推荐）

```bash
# 运行所有测试（默认 test 环境，chromium 浏览器）
./run_tests.sh

# 指定环境
./run_tests.sh -e test

# 指定浏览器
./run_tests.sh -b chromium -c chrome  # Chrome 浏览器
./run_tests.sh -b webkit              # WebKit 浏览器（Safari）

# 运行指定测试
./run_tests.sh -t tests/test_login.py

# 并行执行
./run_tests.sh -p
```

#### 直接使用 pytest

```bash
# 基本运行
pytest

# 指定环境
pytest --env=test

# 指定浏览器
pytest --browser-type=chromium --browser-channel=chrome

# 运行指定测试
pytest tests/test_login.py

# 并行执行
pytest -n auto
```

### 4. 查看 Allure 报告

```bash
# 生成报告
allure generate allure-results -o allure-report --clean


# 打开报告
allure open allure-report
```

## 环境配置

### 环境切换

框架支持多环境配置，通过 `--env` 参数切换：

```bash
# test 环境（本地）
pytest --env=test

# env 环境（生产/预发）
pytest --env=env
```

环境配置在 `data/env_config.yaml` 中定义。

### 浏览器配置

支持多种浏览器：

```bash
# Chromium（默认）
pytest --browser-type=chromium

# Chrome 浏览器
pytest --browser-type=chromium --browser-channel=chrome

# WebKit（Safari）
pytest --browser-type=webkit
```

## 数据驱动

测试数据存储在 `data/test_data.yaml` 中，支持：

- 登录测试数据（有效账号、无效账号）
- 用户管理测试数据（添加、编辑、删除）
- 导航测试数据（标签页切换）

### 添加测试数据

编辑 `test_data.yaml` 添加新的测试数据：

```yaml
login:
  valid_accounts:
    - username: "newuser"
      password: "password123"
      description: "新用户登录"
```

## 测试用例分类

使用 pytest markers 分类测试：

```bash
# 只运行登录测试
pytest -m login

# 只运行用户管理测试
pytest -m user_management

# 只运行冒烟测试
pytest -m smoke
```

## 定位策略

框架优先使用 `get_by_role` 定位策略，符合无障碍最佳实践：

```python
# 推荐：使用 get_by_role
page.get_by_role("button", name="登录")
page.get_by_role("textbox", name="用户名")

# 备选：使用 CSS 选择器
page.locator(".class-name")
```

## 调试技巧

### 1. 有头模式运行

```bash
# 修改 env_config.yaml，设置 headless: false
```

### 2. 慢速执行

在测试中添加延迟：

```python
page.wait_for_timeout(1000)  # 等待 1 秒
```

### 3. 截图

```python
page.screenshot(path="debug.png")
```

### 4. 详细日志

```bash
pytest -v -s
```

## 常见问题

### Q: 测试失败提示找不到元素
A: 检查：
1. 前端服务是否启动
2. 环境配置是否正确
3. 元素定位是否准确
4. 等待时间是否足够

### Q: Allure 报告无法生成
A: 确保已安装 Allure：
```bash
# macOS
brew install allure

# 或其他系统
https://docs.qameta.io/allure/#_get_started
```

### Q: 浏览器无法启动
A: 确保已安装浏览器：
```bash
playwright install
playwright install-deps  # Linux 需要
```

## 扩展框架

### 添加新的 Page Object

1. 在 `pages/` 目录创建新的页面类
2. 继承 `BasePage`
3. 使用 `get_by_role` 定位元素
4. 在 `pages/__init__.py` 中导出

### 添加新的测试用例

1. 在 `tests/` 目录创建测试文件
2. 使用 `@allure.feature` 和 `@allure.story` 标注
3. 使用数据驱动（`@pytest.mark.parametrize`）
4. 使用 fixtures 简化代码

### 添加新的环境

在 `data/env_config.yaml` 添加新环境配置：

```yaml
production:
  base_url: "https://prod.example.com"
  timeout: 30000
  headless: true
  browser_type: "chromium"
```

## 最佳实践

1. **使用 POM**：页面逻辑集中在 pages 目录
2. **数据驱动**：测试数据与测试逻辑分离
3. **优先使用 get_by_role**：符合无障碍标准
4. **添加 Allure 注解**：便于报告分类
5. **使用 fixtures**：复用通用设置
6. **编写清晰的测试描述**：便于理解和维护

## 技术栈

- **Python 3.8+**
- **Playwright**: 浏览器自动化
- **Pytest**: 测试框架
- **Allure**: 测试报告
- **PyYAML**: YAML 文件解析
- **Vue 3**: 被测应用框架
