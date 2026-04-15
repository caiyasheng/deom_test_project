#!/bin/bash

# Playwright 自动化测试运行脚本
# 支持多环境、多浏览器切换

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 默认配置
ENV="test"
BROWSER_TYPE=""
BROWSER_CHANNEL=""
TEST_PATTERN=""
PARALLEL=false
MULTI_BROWSER=false

# 显示帮助信息
show_help() {
    echo "用法：$0 [选项]"
    echo ""
    echo "选项:"
    echo "  -e, --env <环境>        测试环境 (test, env)，默认：test"
    echo "  -b, --browser <浏览器>  浏览器类型 (chromium, webkit, auto)，默认：auto"
    echo "  -c, --channel <通道>    浏览器通道 (chrome, chromium)，默认：从配置文件读取"
    echo "  -t, --test <测试文件>   运行指定测试文件"
    echo "  -p, --parallel          并行执行测试"
    echo "  -m, --multi-browser     多浏览器测试（在所有配置的浏览器上运行）"
    echo "  -h, --help              显示帮助信息"
    echo ""
    echo "示例:"
    echo "  $0                              # 使用默认配置运行所有测试"
    echo "  $0 -e test                      # 在 test 环境运行"
    echo "  $0 -e env -b chromium -c chrome # 在 env 环境使用 Chrome 浏览器"
    echo "  $0 -t tests/test_login.py       # 只运行登录测试"
    echo "  $0 -p                           # 并行执行测试"
    echo "  $0 -b auto                      # 自动检测可用浏览器"
    echo "  $0 -m                           # 多浏览器测试（Chrome + WebKit + Chromium）"
    echo ""
    echo "Allure 报告:"
    echo "  生成报告：allure generate allure-results -o allure-report --clean"
    echo "  查看报告：allure open allure-report"
}

# 检测可用浏览器
detect_browser() {
    echo -e "${BLUE}检测可用浏览器...${NC}"
    
    # 检测 Chrome
    if command -v google-chrome &> /dev/null || [ -d "/Applications/Google Chrome.app" ]; then
        echo -e "${GREEN}找到 Google Chrome${NC}"
        BROWSER_TYPE="chromium"
        BROWSER_CHANNEL="chrome"
        return 0
    fi
    
    # 检测 Chromium
    if command -v chromium &> /dev/null; then
        echo -e "${GREEN}找到 Chromium${NC}"
        BROWSER_TYPE="chromium"
        BROWSER_CHANNEL="chromium"
        return 0
    fi
    
    # 检测 WebKit
    if command -v webkitgtk &> /dev/null || [[ "$OSTYPE" == "darwin"* ]]; then
        echo -e "${GREEN}找到 WebKit${NC}"
        BROWSER_TYPE="webkit"
        BROWSER_CHANNEL=""
        return 0
    fi
    
    echo -e "${RED}未找到可用的浏览器，尝试使用默认 Chromium${NC}"
    BROWSER_TYPE="chromium"
    BROWSER_CHANNEL=""
    return 0
}

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--env)
            ENV="$2"
            shift 2
            ;;
        -b|--browser)
            BROWSER_TYPE="$2"
            shift 2
            ;;
        -c|--channel)
            BROWSER_CHANNEL="$2"
            shift 2
            ;;
        -t|--test)
            TEST_PATTERN="$2"
            shift 2
            ;;
        -p|--parallel)
            PARALLEL=true
            shift
            ;;
        -m|--multi-browser)
            MULTI_BROWSER=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo -e "${RED}未知选项：$1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# 进入脚本所在目录
cd "$(dirname "$0")"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Playwright 自动化测试${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "${YELLOW}环境：${ENV}${NC}"

# 如果浏览器类型为 auto 或未指定，自动检测
if [ "$BROWSER_TYPE" == "auto" ] || [ -z "$BROWSER_TYPE" ]; then
    detect_browser
fi

# 如果没有指定 channel，尝试从配置文件读取
if [ -z "$BROWSER_CHANNEL" ]; then
    if grep -q "browser_channel:" data/env_config.yaml; then
        BROWSER_CHANNEL=$(grep "browser_channel:" data/env_config.yaml | head -1 | awk -F': ' '{print $2}' | tr -d ' "')
        if [ -n "$BROWSER_CHANNEL" ]; then
            echo -e "${BLUE}从配置文件读取浏览器通道：${BROWSER_CHANNEL}${NC}"
        fi
    fi
fi

echo -e "${YELLOW}浏览器：${BROWSER_TYPE}${NC}"
if [ -n "$BROWSER_CHANNEL" ]; then
    echo -e "${YELLOW}浏览器通道：${BROWSER_CHANNEL}${NC}"
fi
echo ""

# 构建 pytest 命令
PYTEST_CMD="pytest"

# 添加环境参数
PYTEST_CMD="$PYTEST_CMD --env=$ENV"

# 添加浏览器类型
if [ -n "$BROWSER_TYPE" ]; then
    PYTEST_CMD="$PYTEST_CMD --browser-type=$BROWSER_TYPE"
fi

# 添加浏览器通道（如果指定）
if [ -n "$BROWSER_CHANNEL" ]; then
    PYTEST_CMD="$PYTEST_CMD --browser-channel=$BROWSER_CHANNEL"
fi

# 添加测试文件（如果指定）
if [ -n "$TEST_PATTERN" ]; then
    PYTEST_CMD="$PYTEST_CMD $TEST_PATTERN"
fi

# 并行执行（如果指定）
if [ "$PARALLEL" = true ]; then
    PYTEST_CMD="$PYTEST_CMD -n auto"
fi

# 多浏览器测试（如果指定）
if [ "$MULTI_BROWSER" = true ]; then
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}多浏览器测试模式${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    
    # 运行所有配置的浏览器
    for browser_name in chrome webkit chromium; do
        echo -e "${GREEN}========================================${NC}"
        echo -e "${GREEN}正在测试：${browser_name}${NC}"
        echo -e "${GREEN}========================================${NC}"
        echo ""
        
        MULTI_PYTEST_CMD="pytest --env=$ENV"
        
        if [ "$browser_name" == "chrome" ]; then
            MULTI_PYTEST_CMD="$MULTI_PYTEST_CMD --browser-type=chromium --browser-channel=chrome"
        elif [ "$browser_name" == "webkit" ]; then
            MULTI_PYTEST_CMD="$MULTI_PYTEST_CMD --browser-type=webkit"
        else
            MULTI_PYTEST_CMD="$MULTI_PYTEST_CMD --browser-type=chromium"
        fi
        
        if [ -n "$TEST_PATTERN" ]; then
            MULTI_PYTEST_CMD="$MULTI_PYTEST_CMD $TEST_PATTERN"
        fi
        
        if [ "$PARALLEL" = true ]; then
            MULTI_PYTEST_CMD="$MULTI_PYTEST_CMD -n auto"
        fi
        
        echo "命令：$MULTI_PYTEST_CMD"
        eval $MULTI_PYTEST_CMD
        
        echo ""
    done
    
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}所有浏览器测试完成！${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo -e "${YELLOW}查看 Allure 报告:${NC}"
    echo "  allure generate allure-results -o allure-report --clean"
    echo "  allure open allure-report"
    exit 0
fi

# 运行测试
echo -e "${GREEN}运行测试...${NC}"
echo "命令：$PYTEST_CMD"
echo ""

eval $PYTEST_CMD

# 显示测试结果
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}测试完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}查看 Allure 报告:${NC}"
echo "  allure generate allure-results -o allure-report --clean"
echo "  allure open allure-report"
