# Fish Audio WebSocket API 测试程序使用说明

## 概述
这是一个完整的 Fish Audio WebSocket API 测试程序，支持实时文本转语音功能测试。

## 文件说明
- `test.py` - 主测试程序
- `test_config.py` - 配置文件
- `README_TEST.md` - 本说明文件

## 快速开始

### 1. 配置 API 密钥
编辑 `test_config.py` 文件，设置以下参数：
```python
FISH_API_KEY = "你的_Fish_Audio_API_密钥"
REFERENCE_ID = "你的_参考音色ID"
```

### 2. 运行测试
有两种运行模式：

#### 自动测试模式（推荐）
```bash
python test.py
```
这将运行所有测试项目并生成详细报告。

#### 交互式测试模式
```bash
python test.py --interactive
```
这将启动交互式菜单，您可以选择单独运行特定测试。

## 测试项目

### 1. 基础 TTS 测试
- 测试基本的文本转语音功能
- 验证 API 连接和基础消息传递

### 2. 中文 TTS 测试
- 测试中文文本的语音合成
- 验证多语言支持

### 3. 流式 TTS 测试
- 测试实时流式文本输入
- 验证增量文本处理能力

### 4. 刷新功能测试
- 测试 flush 事件功能
- 验证强制缓冲区清空

### 5. 音频格式测试
- 测试不同音频格式 (opus, mp3, wav)
- 验证格式兼容性

## 配置选项

### API 设置
```python
TEST_SETTINGS = {
    "model": "speech-1.5",      # 可选: speech-1.5, speech-1.6, s1
    "latency": "normal",        # normal 或 balanced
    "format": "opus",           # opus, mp3, 或 wav
    "temperature": 0.7,         # 控制随机性 (0.0-1.0)
    "top_p": 0.7,              # 控制多样性 (0.0-1.0)
    "speed": 1.0,              # 语音速度 (0.5-2.0)
    "volume": 0                # 音量调整 (dB)
}
```

### 输出设置
```python
OUTPUT_CONFIG = {
    "save_audio": True,                    # 是否保存音频
    "output_dir": "test_output",           # 输出目录
    "filename_prefix": "fish_api_test"     # 文件名前缀
}
```

## 输出文件
- 音频文件将保存在 `test_output/` 目录下
- 文件名格式: `fish_api_test_时间戳.格式`
- 支持的格式: opus, mp3, wav

## 错误排查

### 常见问题

1. **连接失败**
   - 检查网络连接
   - 验证 API 密钥是否正确
   - 确认 Fish Audio 服务状态

2. **音频格式错误**
   - 检查请求的音频格式是否支持
   - 确认服务器返回的音频数据格式

3. **参考音色ID无效**
   - 验证 REFERENCE_ID 是否正确
   - 确认音色ID在您的账户中可用

### 调试模式
要查看详细的错误信息，可以在代码中添加：
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## API 协议说明

### WebSocket 事件类型

1. **start** - 初始化会话
2. **text** - 发送文本块
3. **audio** - 接收音频数据（服务器响应）
4. **stop** - 结束会话
5. **flush** - 刷新文本缓冲区
6. **finish** - 会话结束（服务器端）
7. **log** - 服务器日志消息

### 消息格式
所有消息使用 MessagePack 编码格式。

## 许可证
本测试程序遵循项目的开源许可证。

## 支持
如果您遇到问题，请检查：
1. Fish Audio API 文档
2. 网络连接状态
3. API 密钥和配额
4. 错误日志信息
