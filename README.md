# **文本转语音虚拟麦克风 Tttsvm (Tttsvm is Text to Speech Virtual Microphone)**

[![GitHub license](https://img.shields.io/github/license/GDNDZZK/keyboardControlMouse.svg)](https://github.com/GDNDZZK/keyboardControlMouse/blob/master/LICENSE) ![Python版本](https://img.shields.io/badge/python-3.8%2B-yellow)

打游戏时不敢开麦,打字又没人看,于是我写了这个软件

需要配合[VB-Audio Virtual Cable](https://vb-audio.com/Cable/index.htm)等软件才可以工作

按下快捷键后会读取剪贴板,合成音频或读取文件并通过指定设备输出

[演示视频...还没做](https://www.bilibili.com/video/)

## 使用方法

#### 1.使用 Release 版本

1. 下载并解压 7z 压缩包
2. 运行程序:

   ```
   Tttsvm.exe
   ```
3. 开始使用

#### 2.从源代码构建

1. 克隆或下载此仓库到本地
2. 确保你的 Python 版本在 3.8 及以上
3. 安装必要的 Python 库：

   ```shell
   pip install -r requirements.txt
   ```
4. 运行程序：

   ```
   app.py
   ```
5. 开始使用

## 默认快捷键

`<shift>+<alt>+x`

## 自定义设置

1. 在 `config.ini`文件中,你可以自定义快捷键设置与输出设备名称
2. 可以播放自定义文件(仅支持wav(PCM_16)格式),例如你想在输入 `input`后播放 `demo.wav`,你可以将 `demo.wav`改名为 `input.wav`后放入 `local`目录中

## 使用到的库

- [pynput](https://github.com/moses-palmer/pynput):用于获取键盘输入
- [sounddevice](https://github.com/spatialaudio/python-sounddevice):读取音频设备,输出音频
- [pystray](https://github.com/moses-palmer/pystray):用于创建托盘图标
- [Pillow](https://github.com/python-pillow):用于加载托盘图标的图像
- [pyttsx3](https://github.com/nateshmbhat/pyttsx3):用于语音合成
- [numpy](https://github.com/numpy/numpy):用于快速计算
- [pyperclip](https://github.com/asweigart/pyperclip):用于读取剪贴板
- [requests](https://github.com/psf/requests):用于调用ttsapi

## 开发者

由[GDNDZZK](https://github.com/GDNDZZK)开发和维护

## 许可证

本项目使用 MIT 许可证,详情请参阅[LICENSE](https://github.com/GDNDZZK/Tttsvm/blob/master/LICENSE)文件
