"""
Fish Audio 本地 API 服务器
基于 Flask 框架，提供与原有 API 兼容的接口
"""

import asyncio
import os
import hashlib
import time
import threading
from flask import Flask, request, jsonify, send_file
from werkzeug.serving import make_server
import tempfile
import logging

# 导入我们的 Fish Audio WebSocket API 客户端
from test import FishAudioWebSocketAPI
from test_config import FISH_API_KEY, REFERENCE_ID, TEST_SETTINGS
from audio_converter import convert_opus_to_wav_simple

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class FishAudioService:
    """Fish Audio TTS 服务类"""
    
    def __init__(self):
        self.api_key = FISH_API_KEY
        self.reference_id = REFERENCE_ID
        self.temp_dir = tempfile.gettempdir()
        self.audio_cache = {}  # 简单的内存缓存
        
    async def generate_tts_async(self, text: str, output_path: str, language: str = "ZH"):
        """异步生成 TTS 音频"""
        try:
            # 创建 Fish Audio API 客户端
            api_client = FishAudioWebSocketAPI(self.api_key)
            
            # 根据语言选择合适的设置
            session_settings = TEST_SETTINGS.copy()
            if 'model' in session_settings:
                model = session_settings.pop('model')
            else:
                model = "speech-1.5"
            
            # 连接到 API
            if not await api_client.connect(model=model):
                raise Exception("无法连接到 Fish Audio API")
            
            try:
                # 启动会话
                await api_client.start_session(
                    reference_id=self.reference_id,
                    **session_settings
                )
                
                # 发送文本
                await api_client.send_text(text + " ")
                
                # 停止会话
                await api_client.stop_session()
                
                # 接收音频数据
                audio_chunks = []
                start_time = time.time()
                
                while api_client.connected and (time.time() - start_time) < 30:
                    message = await api_client.receive_message()
                    if not message:
                        break
                    
                    event = message.get("event")
                    if event == "audio":
                        audio_data = message.get("audio")
                        if audio_data:
                            audio_chunks.append(audio_data)
                    elif event == "finish":
                        break
                
                # 合并音频数据并保存
                if audio_chunks:
                    # 写入原始音频数据
                    temp_output = output_path + ".temp"
                    with open(temp_output, "wb") as f:
                        for chunk in audio_chunks:
                            if isinstance(chunk, str):
                                import base64
                                audio_bytes = base64.b64decode(chunk)
                            else:
                                audio_bytes = chunk
                            f.write(audio_bytes)
                    
                    # 如果请求的是 WAV 格式，而 Fish Audio 返回的是 opus，需要转换
                    if output_path.endswith('.wav') and session_settings.get('format', 'opus') == 'wav':
                        # 尝试使用 ffmpeg 或其他工具转换，这里先简单重命名
                        try:
                            import shutil
                            shutil.move(temp_output, output_path)
                            
                            # 验证生成的文件
                            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                                logger.info(f"TTS 音频已生成: {output_path}")
                                return True
                            else:
                                logger.error("生成的音频文件无效")
                                return False
                        except Exception as e:
                            logger.error(f"音频文件处理失败: {e}")
                            return False
                    else:
                        # 直接移动文件
                        try:
                            import shutil
                            shutil.move(temp_output, output_path)
                            logger.info(f"TTS 音频已生成: {output_path}")
                            return True
                        except Exception as e:
                            logger.error(f"文件移动失败: {e}")
                            return False
                else:
                    logger.error("未收到音频数据")
                    return False
                    
            finally:
                await api_client.disconnect()
                
        except Exception as e:
            logger.error(f"TTS 生成失败: {e}")
            return False
    
    def generate_tts(self, text: str, output_path: str, language: str = "ZH"):
        """同步生成 TTS 音频（包装异步方法）"""
        # 创建新的事件循环（避免与主线程冲突）
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                self.generate_tts_async(text, output_path, language)
            )
            return result
        finally:
            loop.close()

# 创建服务实例
fish_service = FishAudioService()

def convert_opus_to_wav(opus_file, wav_file):
    """将 opus 文件转换为 wav 文件"""
    try:
        # 方法1: 尝试使用 pydub (如果安装了)
        try:
            from pydub import AudioSegment
            audio = AudioSegment.from_file(opus_file, format="opus")
            audio.export(wav_file, format="wav")
            logger.info(f"使用 pydub 转换成功: {opus_file} -> {wav_file}")
            return True
        except ImportError:
            logger.warning("pydub 未安装，尝试其他方法")
        except Exception as e:
            logger.warning(f"pydub 转换失败: {e}")
        
        # 方法2: 尝试使用 ffmpeg (如果系统中有)
        try:
            import subprocess
            result = subprocess.run([
                'ffmpeg', '-i', opus_file, '-y', wav_file
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and os.path.exists(wav_file):
                logger.info(f"使用 ffmpeg 转换成功: {opus_file} -> {wav_file}")
                return True
            else:
                logger.warning(f"ffmpeg 转换失败: {result.stderr}")
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            logger.warning(f"ffmpeg 不可用: {e}")
        except Exception as e:
            logger.warning(f"ffmpeg 转换错误: {e}")
        
        # 方法3: 简单的字节复制（作为最后的备选方案）
        # 注意：这种方法可能不会产生有效的 WAV 文件
        logger.warning("尝试直接复制音频数据（可能不兼容）")
        try:
            import shutil
            shutil.copy2(opus_file, wav_file)
            logger.info(f"直接复制完成: {opus_file} -> {wav_file}")
            return True
        except Exception as e:
            logger.error(f"直接复制失败: {e}")
        
        return False
        
    except Exception as e:
        logger.error(f"音频转换失败: {e}")
        return False

@app.route('/', methods=['POST'])
def tts_endpoint():
    """TTS API 端点 - 与原有 API 兼容"""
    try:
        # 获取请求数据
        data = request.get_json() if request.is_json else request.form.to_dict()
        
        if not data:
            return jsonify({"error": "没有提供数据"}), 400
        
        # 提取参数
        text = data.get('text', '')
        language = data.get('language', 'ZH')
        file_path = data.get('file_path', '')
        file_type = data.get('file_type', 'wav')
        
        if not text:
            return jsonify({"error": "文本内容不能为空"}), 400
        
        # 如果没有指定文件路径，生成一个临时路径
        if not file_path:
            # 使用文本的 MD5 作为文件名
            md5_hash = hashlib.md5(text.encode()).hexdigest()
            # 首先生成 opus 文件
            opus_path = os.path.join(fish_service.temp_dir, f"fish_tts_{md5_hash}.opus")
            file_path = opus_path
        
        # 确保输出目录存在
        output_dir = os.path.dirname(file_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        logger.info(f"开始生成 TTS: 文本='{text[:50]}...', 语言={language}, 输出={file_path}")
        
        # 生成 TTS (使用 opus 格式)
        opus_file = file_path if file_path.endswith('.opus') else file_path.replace(f'.{file_type}', '.opus')
        success = fish_service.generate_tts(text, opus_file, language)
        
        if success and os.path.exists(opus_file):
            # 如果请求的是 WAV 格式，需要转换
            if file_type == 'wav' and not file_path.endswith('.opus'):
                wav_file = file_path
                converted = convert_opus_to_wav_simple(opus_file, wav_file)
                if converted:
                    logger.info(f"TTS 转换成功: {wav_file}")
                    # 删除临时 opus 文件
                    try:
                        os.remove(opus_file)
                    except:
                        pass
                    return jsonify({
                        "success": True,
                        "file_path": os.path.abspath(wav_file),
                        "message": "TTS 生成并转换成功"
                    })
                else:
                    logger.error("音频格式转换失败")
                    return jsonify({"error": "音频格式转换失败"}), 500
            else:
                logger.info(f"TTS 生成成功: {opus_file}")
                return jsonify({
                    "success": True,
                    "file_path": os.path.abspath(opus_file),
                    "message": "TTS 生成成功"
                })
        else:
            logger.error("TTS 生成失败")
            return jsonify({"error": "TTS 生成失败"}), 500
            
    except Exception as e:
        logger.error(f"API 处理错误: {e}")
        return jsonify({"error": f"服务器错误: {str(e)}"}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    return jsonify({
        "status": "ok",
        "service": "Fish Audio TTS Server",
        "timestamp": time.time()
    })

@app.route('/config', methods=['GET'])
def get_config():
    """获取当前配置"""
    return jsonify({
        "model": TEST_SETTINGS.get('model', 'speech-1.5'),
        "reference_id": REFERENCE_ID[:8] + "...",  # 只显示前8位
        "settings": {k: v for k, v in TEST_SETTINGS.items() if k != 'model'}
    })

class FishAudioServer:
    """Fish Audio API 服务器管理类"""
    
    def __init__(self, host='127.0.0.1', port=10087):
        self.host = host
        self.port = port
        self.server = None
        self.thread = None
        self.running = False
    
    def start(self):
        """启动服务器"""
        if self.running:
            logger.warning("服务器已在运行")
            return
        
        # 检查配置
        if FISH_API_KEY == "your_api_key_here":
            logger.error("请先在 test_config.py 中配置 FISH_API_KEY")
            return False
        
        if REFERENCE_ID == "your_reference_id_here":
            logger.error("请先在 test_config.py 中配置 REFERENCE_ID")
            return False
        
        def run_server():
            try:
                self.server = make_server(self.host, self.port, app, threaded=True)
                logger.info(f"🐟 Fish Audio TTS 服务器启动在 http://{self.host}:{self.port}")
                logger.info(f"📋 健康检查: http://{self.host}:{self.port}/health")
                logger.info(f"⚙️ 配置信息: http://{self.host}:{self.port}/config")
                self.running = True
                self.server.serve_forever()
            except Exception as e:
                logger.error(f"服务器启动失败: {e}")
                self.running = False
        
        self.thread = threading.Thread(target=run_server, daemon=True)
        self.thread.start()
        
        # 等待一小段时间确保服务器启动
        time.sleep(1)
        return self.running
    
    def stop(self):
        """停止服务器"""
        if self.server and self.running:
            logger.info("正在停止 Fish Audio TTS 服务器...")
            self.server.shutdown()
            self.running = False
            if self.thread:
                self.thread.join(timeout=5)
            logger.info("Fish Audio TTS 服务器已停止")

# 全局服务器实例
fish_audio_server = FishAudioServer()

def start_fish_audio_server():
    """启动 Fish Audio 服务器的便捷函数"""
    return fish_audio_server.start()

def stop_fish_audio_server():
    """停止 Fish Audio 服务器的便捷函数"""
    fish_audio_server.stop()

if __name__ == '__main__':
    # 直接运行服务器
    try:
        if start_fish_audio_server():
            logger.info("服务器启动成功，按 Ctrl+C 退出")
            while fish_audio_server.running:
                time.sleep(1)
        else:
            logger.error("服务器启动失败")
    except KeyboardInterrupt:
        logger.info("收到中断信号，正在关闭服务器...")
        stop_fish_audio_server()
