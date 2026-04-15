# 快速解决浏览器问题

## 方案 1：使用 WebKit（最稳定，推荐）

修改 `data/env_config.yaml`：

```yaml
test:
  base_url: "http://localhost:3000"
  timeout: 30000
  headless: false
  browser_type: "webkit"  # 使用 WebKit（Safari 内核）
```

然后运行：
```bash
./run_tests.sh -b webkit
```

## 方案 2：使用 Chrome 但有头模式

保持当前配置，但确保 Chrome 已安装：
```bash
# 检查 Chrome 是否安装
ls -la "/Applications/Google Chrome.app"

# 如果没有，安装 Chrome
brew install --cask google-chrome
```

然后运行：
```bash
./run_tests.sh
```

## 方案 3：使用 Chromium 但添加稳定参数

修改 `data/env_config.yaml`：
```yaml
test:
  base_url: "http://localhost:3000"
  timeout: 30000
  headless: true  # 使用无头模式避免闪烁
  browser_type: "chromium"
  browser_channel: "chrome"
```

## 验证浏览器

运行以下命令查看可用的浏览器：

```bash
cd playwright_test

# 查看 Playwright 安装的浏览器
playwright show-installed-browsers

# 测试 Chrome
pytest --browser-type=chromium --browser-channel=chrome tests/test_login.py::TestLogin::test_login_page_elements -v

# 测试 WebKit
pytest --browser-type=webkit tests/test_login.py::TestLogin::test_login_page_elements -v
```

## 如果仍然有问题

尝试这个最简配置：

```yaml
test:
  base_url: "http://localhost:3000"
  timeout: 60000
  headless: true
  browser_type: "webkit"
```

运行：
```bash
./run_tests.sh -b webkit
```
