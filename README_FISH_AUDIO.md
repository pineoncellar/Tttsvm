# Fish Audio TTS 集成使用说明

## 概述
本项目已成功集成 Fish Audio TTS API，可以通过本地服务器调用 Fish Audio 的高质量语音合成服务。

## 🚀 快速开始

### 1. 配置 Fish Audio API
编辑 `test_config.py` 文件，设置您的 Fish Audio API 配置：
```python
FISH_API_KEY = "your_fish_audio_api_key"
REFERENCE_ID = "your_reference_voice_id"
```

### 2. 安装依赖
```bash
pip install flask
# 或使用 uv
uv add flask
```

### 3. 配置 TTS 引擎
编辑 `config/config.ini` 文件，将 TTS 引擎设置为 Fish Audio：
```ini
TTS_ENGINE=fish_audio_tts
```

### 4. 启动应用
```bash
python app.py
# 或
uv run app.py
```

应用启动时会自动启动 Fish Audio TTS 服务器。

## 📁 新增文件

### 🔧 核心文件
- `fish_audio_server.py` - Fish Audio TTS 本地服务器
- `start_fish_server.py` - 独立启动服务器脚本
- `test_fish_server.py` - 服务器功能测试脚本

### 📋 API 端点

#### TTS 生成端点
```
POST http://127.0.0.1:10087/
Content-Type: application/json

{
    "text": "要转换的文本",
    "language": "ZH",  // ZH(中文) 或 EN(英文)
    "file_path": "/path/to/output.opus",  // 可选，不指定则自动生成
    "file_type": "opus"  // 可选，支持 opus, mp3, wav
}
```

#### 健康检查端点
```
GET http://127.0.0.1:10087/health
```

#### 配置信息端点
```
GET http://127.0.0.1:10087/config
```

## 🎛️ TTS 引擎选项

在 `config/config.ini` 中可以选择以下 TTS 引擎：

1. **pyttsx3_tts** - 系统内置 TTS（默认）
   - 优点：无需网络，启动快
   - 缺点：语音质量一般

2. **api_tts** - 本地 API TTS（端口 10086）
   - 需要单独的 TTS 服务

3. **fish_audio_tts** - Fish Audio TTS（推荐）
   - 优点：高质量语音合成，多语言支持
   - 缺点：需要网络连接和 API 密钥

## 🧪 测试命令

### 测试 Fish Audio 服务器
```bash
python test_fish_server.py
```

### 独立启动服务器
```bash
python start_fish_server.py
```

### 快速 API 测试
```bash
python quick_test.py
```

### 完整 WebSocket API 测试
```bash
python test.py
```

## 🔧 工作原理

1. **应用启动时**：
   - 检查 TTS 引擎配置
   - 如果设置为 `fish_audio_tts`，自动启动本地 Fish Audio 服务器
   - 服务器监听 `127.0.0.1:10087`

2. **TTS 调用时**：
   - `tts.py` 中的 `fish_audio_tts()` 函数调用本地服务器
   - 服务器使用 WebSocket 连接到 Fish Audio API
   - 接收音频数据并保存为文件
   - 返回文件路径给应用

3. **错误处理**：
   - 如果 Fish Audio 服务失败，自动回退到 `pyttsx3_tts`
   - 支持音频格式自动转换

## 📊 性能特点

- **音频质量**：Fish Audio 提供专业级语音合成
- **支持格式**：opus（推荐）、mp3、wav
- **语言支持**：中文、英文等多语言
- **缓存机制**：相同文本的音频会被缓存
- **容错设计**：网络失败时自动回退

## 🛠️ 故障排除

### 服务器启动失败
1. 检查 `test_config.py` 中的 API 密钥配置
2. 确认网络连接正常
3. 检查端口 10087 是否被占用

### TTS 生成失败
1. 运行 `python test_fish_server.py` 检查服务状态
2. 查看控制台日志了解具体错误
3. 尝试使用其他 TTS 引擎作为备选

### 音频播放问题
1. 确认音频输出设备配置正确
2. 检查生成的音频文件是否存在
3. 验证音频播放器支持对应格式

## 🔄 与原有系统的兼容性

- ✅ 完全兼容现有的热键和剪贴板功能
- ✅ 保持原有的音频播放和设备选择
- ✅ 支持本地音频文件缓存（`./local/` 目录）
- ✅ 保持原有的配置文件格式
- ✅ 错误时自动回退到原有 TTS 引擎

## 📈 使用建议

1. **首次使用**：先运行测试脚本确认服务正常
2. **生产环境**：建议配置适当的错误重试机制
3. **性能优化**：可以调整 Fish Audio API 的参数（温度、速度等）
4. **网络环境**：确保稳定的网络连接以获得最佳体验

现在您可以享受 Fish Audio 提供的高质量 TTS 服务了！🎵
