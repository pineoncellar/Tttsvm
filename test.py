import asyncio
import websockets
import ormsgpack as msgpack
import json
import base64
import os
import time
from typing import Optional, Dict, Any, List
from test_config import FISH_API_KEY, REFERENCE_ID, TEST_SETTINGS, TEST_TEXTS, OUTPUT_CONFIG


class FishAudioWebSocketAPI:
    """Fish Audio WebSocket API 测试客户端"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.websocket = None
        self.url = "wss://api.fish.audio/v1/tts/live"
        self.connected = False
        
    async def connect(self, model: str = "speech-1.5"):
        """连接到 WebSocket API"""
        # 构建完整的 URL，包含查询参数
        url_with_params = f"{self.url}?model={model}"
        
        # 设置请求头
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        
        try:
            self.websocket = await websockets.connect(
                url_with_params,
                additional_headers=headers,
                ping_interval=30,
                ping_timeout=10
            )
            self.connected = True
            print(f"✅ 成功连接到 Fish Audio API (模型: {model})")
            return True
        except Exception as e:
            print(f"❌ 连接失败: {e}")
            return False
    
    async def disconnect(self):
        """断开 WebSocket 连接"""
        if self.websocket and self.connected:
            await self.websocket.close()
            self.connected = False
            print("🔌 已断开连接")
    
    async def send_message(self, message: Dict[str, Any]):
        """发送消息到服务器"""
        if not self.connected or not self.websocket:
            raise Exception("WebSocket 未连接")
        
        # 使用 MessagePack 编码
        packed_message = msgpack.packb(message)
        await self.websocket.send(packed_message)
        print(f"📤 发送消息: {message['event']}")
    
    async def receive_message(self) -> Optional[Dict[str, Any]]:
        """接收服务器消息"""
        if not self.connected or not self.websocket:
            return None
        
        try:
            raw_message = await self.websocket.recv()
            # 使用 MessagePack 解码
            message = msgpack.unpackb(raw_message)
            return message
        except websockets.exceptions.ConnectionClosed:
            print("🔌 连接已关闭")
            self.connected = False
            return None
        except Exception as e:
            print(f"❌ 接收消息错误: {e}")
            return None
    
    async def start_session(
        self,
        reference_id: str,
        latency: str = "normal",
        format: str = "opus",
        temperature: float = 0.7,
        top_p: float = 0.7,
        speed: float = 1.0,
        volume: int = 0,
        references: Optional[List[Dict]] = None
    ):
        """启动 TTS 会话"""
        start_message = {
            "event": "start",
            "request": {
                "text": "",
                "latency": latency,
                "format": format,
                "temperature": temperature,
                "top_p": top_p,
                "prosody": {
                    "speed": speed,
                    "volume": volume
                },
                "reference_id": reference_id
            }
        }
        
        # 如果提供了参考音频，添加到请求中
        if references:
            start_message["request"]["references"] = references
            # 移除 reference_id，因为使用了自定义参考音频
            del start_message["request"]["reference_id"]
        
        await self.send_message(start_message)
    
    async def send_text(self, text: str):
        """发送文本内容"""
        text_message = {
            "event": "text",
            "text": text
        }
        await self.send_message(text_message)
    
    async def flush_buffer(self):
        """刷新文本缓冲区"""
        flush_message = {"event": "flush"}
        await self.send_message(flush_message)
    
    async def stop_session(self):
        """停止会话"""
        stop_message = {"event": "stop"}
        await self.send_message(stop_message)


class FishAudioTester:
    """Fish Audio API 测试器"""
    
    def __init__(self, api_key: str):
        self.api = FishAudioWebSocketAPI(api_key)
        self.audio_data_received = []
        
    async def test_basic_tts(self, reference_id: str, test_text: str = None):
        """基础 TTS 测试"""
        print("\n🧪 开始基础 TTS 测试...")
        
        if test_text is None:
            test_text = TEST_TEXTS["basic"]
        
        # 连接
        if not await self.api.connect(model=TEST_SETTINGS.get('model', 'speech-1.5')):
            return False
        
        try:
            # 启动会话 - 过滤掉不属于会话的参数
            session_settings = {k: v for k, v in TEST_SETTINGS.items() if k != 'model'}
            await self.api.start_session(
                reference_id=reference_id,
                **session_settings
            )
            
            # 发送文本
            await self.api.send_text(test_text + " ")
            
            # 停止会话
            await self.api.stop_session()
            
            # 接收消息
            audio_count = 0
            start_time = time.time()
            
            while self.api.connected and (time.time() - start_time) < 30:  # 30秒超时
                message = await self.api.receive_message()
                if not message:
                    break
                
                event = message.get("event")
                print(f"📥 收到事件: {event}")
                
                if event == "audio":
                    audio_count += 1
                    audio_data = message.get("audio")
                    processing_time = message.get("time", 0)
                    print(f"🎵 收到音频数据 #{audio_count}, 处理时间: {processing_time}ms")
                    
                    # 保存音频数据
                    if audio_data:
                        self.audio_data_received.append(audio_data)
                        
                elif event == "finish":
                    reason = message.get("reason", "unknown")
                    print(f"🏁 会话结束, 原因: {reason}")
                    break
                    
                elif event == "log":
                    log_message = message.get("message", "")
                    print(f"📋 服务器日志: {log_message}")
            
            print(f"✅ 基础测试完成，收到 {audio_count} 个音频片段")
            return True
            
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            return False
        finally:
            await self.api.disconnect()
    
    async def test_streaming_tts(self, reference_id: str):
        """流式 TTS 测试"""
        print("\n🧪 开始流式 TTS 测试...")
        
        if not await self.api.connect(model=TEST_SETTINGS.get('model', 'speech-1.5')):
            return False
        
        try:
            # 启动会话 - 过滤掉不属于会话的参数
            session_settings = {k: v for k, v in TEST_SETTINGS.items() if k != 'model'}
            await self.api.start_session(
                reference_id=reference_id,
                **session_settings
            )
            
            # 分批发送文本
            text_chunks = TEST_TEXTS["streaming"]
            
            # 创建接收任务
            async def receive_messages():
                audio_count = 0
                while self.api.connected:
                    message = await self.api.receive_message()
                    if not message:
                        break
                    
                    event = message.get("event")
                    if event == "audio":
                        audio_count += 1
                        processing_time = message.get("time", 0)
                        print(f"🎵 流式音频 #{audio_count}, 处理时间: {processing_time}ms")
                        # 保存音频数据
                        audio_data = message.get("audio")
                        if audio_data:
                            self.audio_data_received.append(audio_data)
                    elif event == "finish":
                        print(f"🏁 流式会话结束")
                        break
                        
            # 启动接收任务
            receive_task = asyncio.create_task(receive_messages())
            
            # 逐步发送文本
            for i, chunk in enumerate(text_chunks):
                print(f"📤 发送文本块 {i+1}: {chunk.strip()}")
                await self.api.send_text(chunk)
                await asyncio.sleep(1)  # 等待1秒模拟实时输入
            
            # 停止会话
            await self.api.stop_session()
            
            # 等待接收任务完成
            await receive_task
            
            print("✅ 流式测试完成")
            return True
            
        except Exception as e:
            print(f"❌ 流式测试失败: {e}")
            return False
        finally:
            await self.api.disconnect()
    
    async def test_flush_functionality(self, reference_id: str):
        """测试刷新功能"""
        print("\n🧪 开始刷新功能测试...")
        
        if not await self.api.connect(model=TEST_SETTINGS.get('model', 'speech-1.5')):
            return False
        
        try:
            # 启动会话 - 过滤掉不属于会话的参数
            session_settings = {k: v for k, v in TEST_SETTINGS.items() if k != 'model'}
            await self.api.start_session(
                reference_id=reference_id,
                **session_settings
            )
            
            # 发送短文本
            await self.api.send_text("Short text for flush test. ")
            
            # 立即刷新
            await self.api.flush_buffer()
            
            # 接收消息
            audio_received = False
            start_time = time.time()
            
            while self.api.connected and (time.time() - start_time) < 15:  # 15秒超时
                message = await self.api.receive_message()
                if not message:
                    break
                
                event = message.get("event")
                if event == "audio":
                    print("🎵 刷新后收到音频")
                    audio_received = True
                    # 保存音频数据
                    audio_data = message.get("audio")
                    if audio_data:
                        self.audio_data_received.append(audio_data)
                elif event == "finish":
                    break
            
            await self.api.stop_session()
            print("✅ 刷新功能测试完成")
            return True
            
        except Exception as e:
            print(f"❌ 刷新功能测试失败: {e}")
            return False
        finally:
            await self.api.disconnect()
    
    def save_audio_data(self, filename: str = None):
        """保存接收到的音频数据"""
        if not self.audio_data_received:
            print("❌ 没有音频数据可保存")
            return
        
        try:
            # 确保输出目录存在
            output_dir = OUTPUT_CONFIG["output_dir"]
            os.makedirs(output_dir, exist_ok=True)
            
            if filename is None:
                # 使用时间戳生成文件名
                timestamp = int(time.time())
                prefix = OUTPUT_CONFIG["filename_prefix"]
                format_ext = TEST_SETTINGS["format"]
                filename = f"{prefix}_{timestamp}.{format_ext}"
            
            filepath = os.path.join(output_dir, filename)
            with open(filepath, "wb") as f:
                for audio_chunk in self.audio_data_received:
                    if isinstance(audio_chunk, str):
                        # 如果是 base64 编码的字符串
                        audio_bytes = base64.b64decode(audio_chunk)
                    else:
                        # 如果是字节数据
                        audio_bytes = audio_chunk
                    f.write(audio_bytes)
            
            print(f"💾 音频已保存到: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"❌ 保存音频失败: {e}")
            return None

    async def test_chinese_tts(self, reference_id: str):
        """中文 TTS 测试"""
        print("\n🧪 开始中文 TTS 测试...")
        return await self.test_basic_tts(reference_id, TEST_TEXTS["chinese"])

    async def test_different_formats(self, reference_id: str):
        """测试不同音频格式"""
        print("\n🧪 开始音频格式测试...")
        
        formats = ["opus", "mp3", "wav"]
        results = []
        
        for fmt in formats:
            print(f"\n🎵 测试格式: {fmt}")
            
            if not await self.api.connect(model=TEST_SETTINGS.get('model', 'speech-1.5')):
                results.append((fmt, False))
                continue
            
            try:
                # 临时修改设置 - 过滤掉不属于会话的参数
                temp_settings = {k: v for k, v in TEST_SETTINGS.items() if k != 'model'}
                temp_settings["format"] = fmt
                
                await self.api.start_session(
                    reference_id=reference_id,
                    **temp_settings
                )
                
                await self.api.send_text(f"Testing {fmt} format. ")
                await self.api.stop_session()
                
                # 接收音频
                audio_received = False
                start_time = time.time()
                
                while self.api.connected and (time.time() - start_time) < 15:
                    message = await self.api.receive_message()
                    if not message:
                        break
                    
                    if message.get("event") == "audio":
                        audio_received = True
                        audio_data = message.get("audio")
                        if audio_data:
                            self.audio_data_received.append(audio_data)
                        print(f"✅ {fmt} 格式音频接收成功")
                    elif message.get("event") == "finish":
                        break
                
                results.append((fmt, audio_received))
                
            except Exception as e:
                print(f"❌ {fmt} 格式测试失败: {e}")
                results.append((fmt, False))
            finally:
                await self.api.disconnect()
        
        # 显示结果
        print("\n📊 格式测试结果:")
        for fmt, success in results:
            status = "✅ 成功" if success else "❌ 失败"
            print(f"  {fmt}: {status}")
        
        return all(success for _, success in results)


async def main():
    """主测试函数"""
    print("🐟 Fish Audio WebSocket API 测试程序")
    print("=" * 50)
    
    # 检查配置
    if FISH_API_KEY == "your_api_key_here":
        print("❌ 请在 test_config.py 中设置您的 FISH_API_KEY")
        print("💡 提示: 编辑 test_config.py 文件，将 FISH_API_KEY 替换为您的实际 API 密钥")
        return
    
    if REFERENCE_ID == "your_reference_id_here":
        print("❌ 请在 test_config.py 中设置您的 REFERENCE_ID")
        print("💡 提示: 编辑 test_config.py 文件，将 REFERENCE_ID 替换为您的参考音色ID")
        return
    
    print(f"🔧 使用模型: {TEST_SETTINGS['model']}")
    print(f"🎯 参考音色ID: {REFERENCE_ID}")
    print(f"🎵 音频格式: {TEST_SETTINGS['format']}")
    
    # 创建测试器
    tester = FishAudioTester(FISH_API_KEY)
    
    try:
        # 运行各种测试
        tests = [
            ("基础 TTS 测试", tester.test_basic_tts(REFERENCE_ID)),
            ("中文 TTS 测试", tester.test_chinese_tts(REFERENCE_ID)),
            ("流式 TTS 测试", tester.test_streaming_tts(REFERENCE_ID)),
            ("刷新功能测试", tester.test_flush_functionality(REFERENCE_ID)),
            ("音频格式测试", tester.test_different_formats(REFERENCE_ID))
        ]
        
        results = []
        for test_name, test_coro in tests:
            print(f"\n{'='*20} {test_name} {'='*20}")
            try:
                result = await test_coro
                results.append((test_name, result))
            except Exception as e:
                print(f"❌ {test_name} 执行失败: {e}")
                results.append((test_name, False))
        
        # 保存音频文件
        if OUTPUT_CONFIG["save_audio"] and tester.audio_data_received:
            saved_file = tester.save_audio_data()
            if saved_file:
                print(f"\n💾 所有测试音频已合并保存到: {saved_file}")
        
        # 显示测试结果
        print("\n" + "="*50)
        print("📊 测试结果汇总:")
        passed_tests = 0
        total_tests = len(results)
        
        for test_name, result in results:
            status = "✅ 通过" if result else "❌ 失败"
            print(f"  {test_name}: {status}")
            if result:
                passed_tests += 1
        
        print(f"\n🎯 总体结果: {passed_tests}/{total_tests} 个测试通过")
        
        if passed_tests == total_tests:
            print("🎉 所有测试都通过了！Fish Audio API 工作正常。")
        elif passed_tests > 0:
            print("⚠️ 部分测试通过，请检查失败的测试项。")
        else:
            print("💥 所有测试都失败了，请检查您的 API 密钥和网络连接。")
        
    except KeyboardInterrupt:
        print("\n⏹️ 测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


def run_interactive_test():
    """交互式测试模式"""
    print("🎮 Fish Audio API 交互式测试")
    print("=" * 40)
    
    while True:
        print("\n请选择测试项目:")
        print("1. 基础 TTS 测试")
        print("2. 中文 TTS 测试")
        print("3. 流式 TTS 测试")
        print("4. 刷新功能测试")
        print("5. 音频格式测试")
        print("6. 运行所有测试")
        print("7. 自定义文本测试")
        print("0. 退出")
        
        choice = input("\n请输入选项 (0-7): ").strip()
        
        if choice == "0":
            print("👋 再见！")
            break
        elif choice == "6":
            asyncio.run(main())
        elif choice == "7":
            custom_text = input("请输入要测试的文本: ").strip()
            if custom_text:
                async def custom_test():
                    tester = FishAudioTester(FISH_API_KEY)
                    result = await tester.test_basic_tts(REFERENCE_ID, custom_text)
                    if result and tester.audio_data_received:
                        tester.save_audio_data(f"custom_test_{int(time.time())}.{TEST_SETTINGS['format']}")
                
                asyncio.run(custom_test())
        else:
            # 运行单个测试
            test_map = {
                "1": lambda: asyncio.run(_run_single_test("基础 TTS 测试", FishAudioTester(FISH_API_KEY).test_basic_tts(REFERENCE_ID))),
                "2": lambda: asyncio.run(_run_single_test("中文 TTS 测试", FishAudioTester(FISH_API_KEY).test_chinese_tts(REFERENCE_ID))),
                "3": lambda: asyncio.run(_run_single_test("流式 TTS 测试", FishAudioTester(FISH_API_KEY).test_streaming_tts(REFERENCE_ID))),
                "4": lambda: asyncio.run(_run_single_test("刷新功能测试", FishAudioTester(FISH_API_KEY).test_flush_functionality(REFERENCE_ID))),
                "5": lambda: asyncio.run(_run_single_test("音频格式测试", FishAudioTester(FISH_API_KEY).test_different_formats(REFERENCE_ID)))
            }
            
            if choice in test_map:
                test_map[choice]()
            else:
                print("❌ 无效选项，请重新选择")


async def _run_single_test(test_name: str, test_coro):
    """运行单个测试"""
    print(f"\n{'='*20} {test_name} {'='*20}")
    try:
        tester = FishAudioTester(FISH_API_KEY)
        result = await test_coro
        if result and tester.audio_data_received:
            tester.save_audio_data()
        print(f"\n{test_name}: {'✅ 通过' if result else '❌ 失败'}")
    except Exception as e:
        print(f"❌ {test_name} 执行失败: {e}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        run_interactive_test()
    else:
        # 运行所有测试
        asyncio.run(main())