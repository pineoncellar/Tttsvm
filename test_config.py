# Fish Audio API 测试配置文件
# 配置项已迁移到 config/config.ini 文件中

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
