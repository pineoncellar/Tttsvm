import json
import os
import hashlib
import threading
import time
import pyttsx3
import requests

do_not_use_cache = True

def pyttsx3_tts(text, filepath):
    # 文件不存在，使用pyttsx3合成wav文件
    try:
        engine = pyttsx3.init('sapi5')
    except:
        try:
            engine = pyttsx3.init()
        except:
            try:
                engine = pyttsx3.init('nsss')
            except:
                print("WARN: No TTS engine found")
                engine = pyttsx3.init('dummy')
    # 设置输出到文件
    engine.save_to_file(text, filepath)
    # 执行TTS
    engine.runAndWait()
    # 关闭引擎
    engine.stop()

    # 返回文件的绝对路径
    return os.path.abspath(filepath)

def send_request(url, method, params=None, headers=None, proxies=None, body=None, encoding='utf-8', timeout=10, verify=True):
    """
    Sends an HTTP request with given URL, method, params, headers, and body.

    Args:
        url (str): The URL to send the request to.
        method (str): The HTTP method to use ('GET', 'POST', etc.).
        params (dict): A dictionary of query parameters to include in the request.
        headers (dict): A dictionary of headers to include in the request.
        proxies (dict): A dictionary to configure proxies for the request.
        body (dict): A dictionary containing the data to send in the body of a POST request.
                     If the value is a file path and the file exists, the file will be uploaded.
        encoding (str): The encoding to use for decoding the response content.

    Returns:
        The response text from the HTTP request (decoded using specified encoding).
    """
    files = {}
    if method.upper() == 'GET':
        response = requests.get(url, params=params, headers=headers,
                                proxies=proxies, timeout=timeout, verify=verify)
    elif method.upper() == 'POST':
        data = {}
        if body:
            for key, value in body.items():
                    data[key] = value
        if headers and 'Content-Type' in headers and headers['Content-Type'] == 'application/json':
            data = json.dumps(data)
        if files:
            # if not headers:
            # headers = dict()
            # headers['Content-Type'] = 'multipart/form-data'
            response = requests.post(url, params=params, data=data, files=files,
                                     headers=headers, proxies=proxies, timeout=timeout, verify=verify)
        else:
            response = requests.post(url, params=params, data=data, headers=headers,
                                     proxies=proxies, timeout=timeout, verify=verify)
    else:
        raise ValueError("Unsupported HTTP method: %s" % method)

    # Ensure all opened files are closed
    for file in files.values():
        file.close()

    # Decode the response text using specified encoding
    return response.content.decode(encoding)

tts_lock = threading.Lock()
def api_tts(text, filepath, language="ZH"):
    # ZH|JA
    result = send_request("http://127.0.0.1:10086/",'POST',body={"text": text, "language": language, 'file_path' : os.path.abspath(filepath), 'file_type' : 'wav'})
    return result

def fish_audio_tts(text, filepath, language="ZH"):
    """Fish Audio TTS API 调用"""
    try:
        # 调用本地 Fish Audio API 服务器
        result = send_request(
            "http://127.0.0.1:10087/", 
            'POST',
            body={
                "text": text, 
                "language": language, 
                'file_path': os.path.abspath(filepath), 
                'file_type': 'wav'  # 改为 wav 格式以兼容音频播放器
            },
            headers={'Content-Type': 'application/json'}
        )
        
        # 解析响应
        import json
        response_data = json.loads(result)
        
        if response_data.get('success'):
            return response_data.get('file_path', filepath)
        else:
            error_msg = response_data.get('error', '未知错误')
            print(f"Fish Audio TTS 错误: {error_msg}")
            return None
            
    except Exception as e:
        print(f"Fish Audio TTS 调用失败: {e}")
        return None


def tts_if_not_exists(text, directory, tts_engine = 'pyttsx3_tts'):
    global do_not_use_cache
    # 计算字符串的MD5值
    md5_hash = hashlib.md5(text.encode()).hexdigest()
    
    # 所有 TTS 引擎都使用 WAV 格式以确保兼容性
    file_extension = 'wav'
    
    filename = f"{md5_hash}.{file_extension}"
    filepath = os.path.join(directory, filename)
    
    # 检查文件是否存在于指定目录中
    # 如果不使用缓存
    if do_not_use_cache and os.path.exists(filepath):
        # 删除文件
        try:
            os.remove(filepath)
        # 如果文件被占用，则等待一段时间后再次尝试
        except PermissionError:
            time.sleep(0.1)
            return tts_if_not_exists(text, directory, tts_engine)
    
    if not os.path.exists(filepath):
        if tts_engine == 'pyttsx3_tts':
            result = pyttsx3_tts(text, filepath)
        elif tts_engine == 'api_tts':
            result = api_tts(text, directory)
        elif tts_engine == 'fish_audio_tts':
            result = fish_audio_tts(text, filepath)
            if result is None:
                # Fish Audio 失败时回退到 pyttsx3
                print("Fish Audio TTS 失败，回退到 pyttsx3")
                result = pyttsx3_tts(text, filepath)
        else:
            raise ValueError("Invalid TTS engine specified.")
    else:
        result = filepath
    
    return os.path.abspath(result)