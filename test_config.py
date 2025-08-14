# Fish Audio API 测试配置文件
# 请在这里设置您的配置信息

# Fish Audio API 配置
FISH_API_KEY = "91b0867a9c5a4f46a8058d6cd142b6d2"  # 请替换为您的 Fish Audio API 密钥
REFERENCE_ID = "3d1cb00d75184099992ddbaf0fdd7387"  # 请替换为您的参考音色ID

# 测试配置
TEST_SETTINGS = {
    "model": "speech-1.5",  # 可选: speech-1.5, speech-1.6, s1
    "latency": "normal",    # normal 或 balanced
    "format": "opus",       # opus, mp3, 或 wav - 使用 opus 获得最佳质量
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
