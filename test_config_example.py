# Fish Audio TTS 配置示例
# 请复制此文件为 test_config.py 并填入您的实际配置

# Fish Audio API 配置
FISH_API_KEY = "your_fish_audio_api_key_here"  # 从 Fish Audio 官网获取
REFERENCE_ID = "your_reference_voice_id_here"  # 在 Fish Audio 控制台选择音色

# 测试配置
TEST_SETTINGS = {
    "model": "speech-1.5",  # 可选: speech-1.5, speech-1.6, s1
    "latency": "normal",    # normal 或 balanced
    "format": "opus",       # opus, mp3, 或 wav
    "temperature": 0.7,     # 控制语音生成的随机性 (0.0-1.0)
    "top_p": 0.7,          # 控制多样性 (0.0-1.0)
    "speed": 1.0,          # 语音速度 (0.5-2.0)
    "volume": 0            # 音量调整 (dB)
}

# 测试文本
TEST_TEXTS = {
    "basic": "Hello, this is a test of Fish Audio TTS API.",
    "chinese": "你好，这是 Fish Audio 文本转语音 API 的测试。",
    "long": """
    This is a longer test text to evaluate the streaming capabilities of the Fish Audio API.
    We will send this text in multiple chunks to test real-time processing.
    The system should be able to handle continuous text input and produce high-quality audio output.
    """,
    "streaming": [
        "This is the first part of the streaming test. ",
        "Now we're sending the second part to see how well it handles real-time input. ",
        "Here comes the third segment of our streaming test. ",
        "And finally, this is the last part of our streaming evaluation. "
    ]
}

# 输出配置
OUTPUT_CONFIG = {
    "save_audio": True,
    "output_dir": "test_output",
    "filename_prefix": "fish_api_test"
}

# 🔧 配置说明
"""
1. FISH_API_KEY: 您的 Fish Audio API 密钥
   - 访问 https://fish.audio/ 注册账户
   - 在控制台获取 API Key

2. REFERENCE_ID: 参考音色ID
   - 在 Fish Audio 控制台选择或创建音色
   - 复制音色的 ID

3. 模型选择:
   - speech-1.5: 标准模型，平衡质量和速度
   - speech-1.6: 改进模型，更好的质量
   - s1: 快速模型，低延迟

4. 音频格式:
   - opus: 推荐格式，文件小质量高
   - mp3: 通用格式，兼容性好
   - wav: 无损格式，文件较大

5. 语音参数:
   - temperature: 控制随机性，0.7 为推荐值
   - top_p: 控制多样性，0.7 为推荐值
   - speed: 语音速度，1.0 为正常速度
   - volume: 音量调整，0 为默认音量
"""
