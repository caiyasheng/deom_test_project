# 多浏览器兼容性测试指南

## 概述

本框架支持在多个浏览器上运行自动化测试，确保应用在不同浏览器上的兼容性。

## 支持的浏览器

- **Chrome** - Google Chrome 浏览器（基于 Chromium）
- **WebKit** - Safari 浏览器内核（macOS 原生）
- **Chromium** - 开源 Chromium 浏览器

## 快速开始

### 1. 单浏览器测试（默认）

使用配置文件中指定的浏览器：

```bash
./run_tests.sh
```

### 2. 指定浏览器测试

```bash
# 使用 Chrome
./run_tests.sh -b chromium -c chrome

# 使用 WebKit
./run_tests.sh -b webkit

# 使用 Chromium
./run_tests.sh -b chromium
```

### 3. 多浏览器测试（推荐）

一次性在所有配置的浏览器上运行测试：

```bash
./run_tests.sh -m
```

这会依次在 Chrome、WebKit、Chromium 上运行所有测试。

## 编写多浏览器测试

### 方式 1：使用 @pytest.mark.multi_browser

```python
import pytest
import allure
from playwright.sync_api import Page

@allure.feature("多浏览器测试")
class TestMultiBrowser:
    
    @pytest.mark.multi_browser
    @allure.title("多浏览器 - 登录测试 [{browser_name}]")
    def test_login(self, page: Page, browser_name: str):
        """
        这个测试会在所有配置的浏览器上运行
        
        Args:
            page: Playwright Page 对象
            browser_name: 浏览器名称（自动注入）
        """
        page.goto("/")
        
        # 执行登录
        page.get_by_role("textbox", name="用户名").fill("admin")
        page.get_by_role("textbox", name="密码").fill("admin123")
        page.get_by_role("button", name="登录").click()
        
        # 验证
        assert page.get_by_role("button", name="退出登录").is_visible()
```

### 方式 2：指定特定浏览器

```python
# 只在 Chrome 上运行
@pytest.mark.browser("chrome")
def test_chrome_only(page: Page):
    page.goto("/")
    assert page.title() == "用户管理系统"

# 只在 WebKit 上运行
@pytest.mark.browser("webkit")
def test_webkit_only(page: Page):
    page.goto("/")
    assert page.title() == "用户管理系统"
```

## 配置多浏览器

编辑 `data/env_config.yaml`：

```yaml
# 默认浏览器配置
test:
  base_url: "http://localhost:3000"
  browser_type: "chromium"
  browser_channel: "chrome"

# 多浏览器配置
browsers:
  - name: "chrome"
    browser_type: "chromium"
    browser_channel: "chrome"
  - name: "webkit"
    browser_type: "webkit"
    browser_channel: ""
  - name: "chromium"
    browser_type: "chromium"
    browser_channel: ""
```

## 查看测试结果

### 1. 命令行输出

```bash
./run_tests.sh -m

# 输出示例：
========================================
多浏览器测试模式
========================================

========================================
正在测试：chrome
========================================
test_login.py::TestLogin::test_login[chrome] PASSED

========================================
正在测试：webkit
========================================
test_login.py::TestLogin::test_login[webkit] PASSED

========================================
正在测试：chromium
========================================
test_login.py::TestLogin::test_login[chromium] PASSED
```

### 2. Allure 报告

生成包含所有浏览器测试结果的报告：

```bash
# 生成报告
allure generate allure-results -o allure-report --clean

# 打开报告
allure open allure-report
```

在报告中可以看到每个测试在哪个浏览器上运行。

## 最佳实践

### 1. 标记浏览器特定测试

如果某些测试只在特定浏览器上运行：

```python
@pytest.mark.browser("chrome")
def test_chrome_feature(page: Page):
    """测试 Chrome 特有功能"""
    pass
```

### 2. 使用参数化获取浏览器信息

```python
@pytest.mark.multi_browser
def test_with_browser_info(page: Page, browser_name: str):
    """使用 browser_name 参数"""
    print(f"当前测试运行在：{browser_name}")
```

### 3. 浏览器兼容性检查清单

- [ ] 页面加载正常
- [ ] 表单输入和提交
- [ ] 按钮点击和交互
- [ ] 弹窗和模态框
- [ ] 表格数据显示
- [ ] 导航和路由
- [ ] CSS 样式渲染
- [ ] JavaScript 功能

### 4. 处理浏览器差异

```python
@pytest.mark.multi_browser
def test_handle_differences(page: Page, browser_name: str):
    # 根据不同浏览器调整等待时间
    timeout = 5000 if browser_name == "webkit" else 3000
    
    # 根据不同浏览器调整定位策略
    if browser_name == "webkit":
        # WebKit 特定的定位方式
        pass
    else:
        # 通用定位方式
        pass
```

## 常见问题

### Q: 某个浏览器测试失败怎么办？

A: 可以：
1. 单独在该浏览器上运行测试进行调试
2. 使用 `@pytest.mark.skip` 跳过该浏览器的特定测试
3. 查看浏览器特定的日志和截图

```bash
# 单独在 WebKit 上运行
./run_tests.sh -b webkit -t tests/test_login.py
```

### Q: 如何加速多浏览器测试？

A: 使用并行执行：

```bash
# 多浏览器 + 并行
./run_tests.sh -m -p
```

### Q: 如何只运行标记为多浏览器的测试？

A: 使用 markers 过滤：

```bash
pytest -m multi_browser
```

### Q: 如何添加新的浏览器？

A: 在 `env_config.yaml` 的 `browsers` 列表中添加：

```yaml
browsers:
  - name: "firefox"
    browser_type: "firefox"
    browser_channel: ""
```

然后安装对应浏览器：

```bash
playwright install firefox
```

## 浏览器安装

### 安装所有支持的浏览器

```bash
playwright install chromium
playwright install webkit
playwright install firefox  # 可选
```

### 检查已安装的浏览器

```bash
playwright show-installed-browsers
```

### 使用系统安装的 Chrome

确保 Chrome 已安装：

```bash
# macOS
ls -la "/Applications/Google Chrome.app"

# 如果未安装
brew install --cask google-chrome
```

## 示例命令

```bash
# 1. 快速测试（使用默认浏览器）
./run_tests.sh

# 2. 多浏览器完整测试
./run_tests.sh -m

# 3. 多浏览器 + 并行
./run_tests.sh -m -p

# 4. 只测试登录功能（多浏览器）
./run_tests.sh -m -t tests/test_login.py

# 5. 只在 Chrome 上运行
./run_tests.sh -b chromium -c chrome

# 6. 只在 WebKit 上运行
./run_tests.sh -b webkit

# 7. 生成并查看报告
allure generate allure-results -o allure-report --clean
allure open allure-report
```

## 报告解读

在 Allure 报告中，你可以看到：

- 每个测试在不同浏览器上的执行结果
- 浏览器特定的失败信息
- 截图和日志（如果配置）
- 浏览器兼容性矩阵

## 持续集成

在 CI/CD 中使用多浏览器测试：

```yaml
# .github/workflows/test.yml
jobs:
  multi-browser-test:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r playwright_test/requirements.txt
          playwright install
      - name: Run multi-browser tests
        run: |
          cd playwright_test
          ./run_tests.sh -m
      - name: Upload Allure report
        uses: actions/upload-artifact@v2
        with:
          name: allure-report
          path: allure-report
```

## 总结

多浏览器测试的优势：

✅ 发现浏览器特定问题
✅ 确保跨浏览器兼容性
✅ 提高用户体验
✅ 减少生产环境问题

建议：

- 每次发布前运行多浏览器测试
- 优先保证主流浏览器（Chrome、Safari）的兼容性
- 根据用户群体选择目标浏览器
- 使用自动化持续监控浏览器兼容性
