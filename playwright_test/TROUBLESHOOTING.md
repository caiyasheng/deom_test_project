# Playwright 故障排查指南

## 常见问题及解决方案

### 1. Chromium 崩溃（SIGSEGV 错误）

**错误信息：**
```
[pid=xxxx][err] Received signal 11 SEGV_ACCERR
Browser logs: <launched> pid=xxxx
```

**原因：** macOS 系统版本与 Playwright 的 Chromium 版本兼容性问题

**解决方案：**

#### 方案 A：使用 Chrome 浏览器（推荐）

1. 确保已安装 Google Chrome
2. 配置文件已设置使用 Chrome：
   ```yaml
   test:
     browser_type: "chromium"
     browser_channel: "chrome"
   ```

#### 方案 B：使用 WebKit（Safari）

```bash
./run_tests.sh -b webkit
```

#### 方案 C：自动检测浏览器

```bash
./run_tests.sh -b auto
```

### 2. 浏览器未找到

**错误信息：**
```
Executable doesn't exist at /path/to/chrome
```

**解决方案：**

#### 安装 Chrome（macOS）
```bash
# 使用 Homebrew
brew install --cask google-chrome

# 或手动下载安装
# https://www.google.com/chrome/
```

#### 安装 Chromium
```bash
playwright install chromium
```

#### 安装 WebKit
```bash
playwright install webkit
```

### 3. 依赖缺失（Linux）

**错误信息：**
```
error while loading shared libraries
```

**解决方案：**
```bash
# 安装系统依赖
playwright install-deps
```

### 4. 超时错误

**错误信息：**
```
TimeoutError: Timeout 30000ms exceeded
```

**解决方案：**

1. 检查服务是否启动
2. 增加超时时间：
   ```yaml
   test:
     timeout: 60000  # 增加到 60 秒
   ```

3. 检查元素定位是否正确

### 5. 元素定位失败

**错误信息：**
```
Error: locator.click: Error: Element is not visible
```

**解决方案：**

1. 使用 `get_by_role` 优先策略
2. 添加等待：
   ```python
   page.wait_for_selector("selector", timeout=10000)
   ```

3. 检查元素是否在 iframe 中

### 6. Allure 报告无法生成

**错误信息：**
```
command not found: allure
```

**解决方案：**

#### macOS
```bash
brew install allure
```

#### 其他系统
```bash
# 下载并安装
https://docs.qameta.io/allure/#_get_started
```

### 7. Python 依赖问题

**错误信息：**
```
ModuleNotFoundError: No module named 'playwright'
```

**解决方案：**
```bash
# 安装依赖
pip install -r requirements.txt

# 或使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 调试技巧

### 1. 有头模式运行

确保配置文件中设置：
```yaml
test:
  headless: false
```

### 2. 慢动作调试

在测试代码中添加：
```python
page.wait_for_timeout(1000)  # 等待 1 秒
```

### 3. 截图调试

```python
page.screenshot(path="debug.png")
```

### 4. 查看详细日志

```bash
pytest -v -s
```

### 5. 只运行单个测试

```bash
pytest tests/test_login.py::TestLogin::test_login_success -v -s
```

## 浏览器安装检查

### 检查 Chrome 是否安装

```bash
# macOS
ls -la "/Applications/Google Chrome.app"

# Linux
which google-chrome

# Windows
where chrome
```

### 检查 Playwright 浏览器

```bash
# 查看已安装的浏览器
playwright show-installed-browsers

# 重新安装浏览器
playwright install chromium
playwright install webkit
playwright install firefox
```

## 环境验证

运行以下命令验证环境：

```bash
# 1. 检查 Python 版本
python --version

# 2. 检查 Playwright 版本
playwright --version

# 3. 检查 pytest 版本
pytest --version

# 4. 检查浏览器
playwright show-installed-browsers

# 5. 运行简单测试
pytest tests/test_login.py::TestLogin::test_login_page_elements -v
```

## 性能优化

### 1. 并行执行

```bash
pytest -n auto
```

### 2. 使用 Markers 筛选测试

```bash
# 只运行冒烟测试
pytest -m smoke

# 只运行登录测试
pytest -m login
```

### 3. 失败重跑

安装 pytest-rerunfailures：
```bash
pip install pytest-rerunfailures
```

运行：
```bash
pytest --reruns 3 --reruns-delay 2
```

## 获取帮助

如果问题仍未解决：

1. 查看 Playwright 官方文档：https://playwright.dev/python/
2. 查看 pytest 文档：https://docs.pytest.org/
3. 查看 Allure 文档：https://docs.qameta.io/allure/
4. 提交 Issue 时附上：
   - 操作系统版本
   - Python 版本
   - Playwright 版本
   - 完整的错误日志
