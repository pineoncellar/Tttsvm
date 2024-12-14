import threading
import wave
import numpy as np
import sounddevice as sd


class AudioPlayer:
    def __init__(self):
        pass

    def get_audio_devices(self):
        """ 获取所有音频输出设备名称与设备id的字典 """
        devices = {}
        device_info = sd.query_devices()

        for row in device_info:
            # 判断设备是否支持输出
            if float(row['max_output_channels']) > 0 and row['name'] not in devices:
                devices[row['name']] = row['index']  # 使用hostapi作为设备ID

        return devices

    play_Lock = threading.Lock()

    def play_audio_on_device(self, file_path, device_id, volume):
        """ 播放指定文件路径的音频到指定的设备 """
        # 打开WAV文件
        with wave.open(file_path, 'rb') as wf:
            # 读取音频参数
            channels = wf.getnchannels()
            width = wf.getsampwidth()
            frame_rate = wf.getframerate()
            frames = wf.readframes(wf.getnframes())

            # 将字节数据转换为numpy数组
            audio_data = np.frombuffer(frames, dtype=np.int16)

            # 调整音量
            audio_data = audio_data * volume
            # 格式转换
            audio_data = audio_data.astype(np.int16)
            with self.play_Lock:
                # 播放音频
                sd.play(audio_data, samplerate=frame_rate,
                        device=device_id, mapping=[1, 2])
                # 等待音频播放完成
                sd.wait()

    def play_audio_on_device_async(self, file_path, device_id, volume):
        """ 异步播放指定文件路径的音频到指定的设备 """
        # 创建并启动线程
        threading.Thread(target=self.play_audio_on_device,
                         args=(file_path, device_id, volume)).start()


# 示例使用：
if __name__ == '__main__':
    audio_player = AudioPlayer()

    # 获取设备列表
    devices = audio_player.get_audio_devices()
    print("音频设备列表:")
    for name, device_id in devices.items():
        print(f"设备名称: {name}, 设备ID: {device_id}")

    # 假设选择一个设备ID播放音频文件
    device_id = list(devices.values())[0]  # 选择第一个设备
    audio_player.play_audio_on_device("path_to_your_audio_file.wav", device_id)
