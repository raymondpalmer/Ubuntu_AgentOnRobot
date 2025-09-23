#!/usr/bin/env python3
"""
使用 dragon_official_exact.py 中的音频配置进行播放测试：
- 打开输出流（优先 PulseAudio）
- 播放 2 秒 440Hz 正弦波（Float32 / 24000Hz / 单声道）
可通过设置环境变量 DRAGON_AUDIO_DEVICE_INDEX 指定设备索引。
"""
import os
import time
import math
import struct

import pyaudio

# 与 dragon_official_exact.py 保持一致的输出配置
OUTPUT_CONFIG = {
    "chunk": 1600,
    "format": "pcm",
    "channels": 1,
    "sample_rate": 24000,
    "bit_size": pyaudio.paFloat32
}


def list_devices(p):
    print("🎛️ 可用音频输出设备：")
    for i in range(p.get_device_count()):
        try:
            info = p.get_device_info_by_index(i)
            if info.get('maxOutputChannels', 0) > 0:
                print(f"  - {i}: {info.get('name')} | out={info.get('maxOutputChannels')} | rate={int(info.get('defaultSampleRate',0))}")
        except Exception:
            pass


def open_output_stream(p):
    frames_per_buffer = max(64, int(OUTPUT_CONFIG["chunk"]))
    fmt = OUTPUT_CONFIG["bit_size"]
    channels = OUTPUT_CONFIG["channels"]
    sr = OUTPUT_CONFIG["sample_rate"]

    try_order = []

    env_idx = os.environ.get('DRAGON_AUDIO_DEVICE_INDEX')
    if env_idx is not None:
        try:
            try_order.append(('env', int(env_idx)))
        except ValueError:
            print(f"⚠️ DRAGON_AUDIO_DEVICE_INDEX 无效: {env_idx}")

    # pulse
    for i in range(p.get_device_count()):
        try:
            info = p.get_device_info_by_index(i)
            if info.get('maxOutputChannels', 0) > 0 and 'pulse' in str(info.get('name','')).lower():
                try_order.append(('pulse', i))
                break
        except Exception:
            pass

    # first out
    for i in range(p.get_device_count()):
        try:
            info = p.get_device_info_by_index(i)
            if info.get('maxOutputChannels', 0) > 0:
                try_order.append(('first_out', i))
                break
        except Exception:
            pass

    try_order.append(('default', None))

    last_err = None
    for label, idx in try_order:
        try:
            kwargs = dict(format=fmt, channels=channels, rate=sr, output=True, frames_per_buffer=frames_per_buffer, start=False)
            if idx is not None:
                kwargs['output_device_index'] = idx
            stream = p.open(**kwargs)
            stream.start_stream()
            if idx is not None:
                info = p.get_device_info_by_index(idx)
                print(f"✅ 打开输出成功 -> 设备 {idx}: {info.get('name')}")
            else:
                print(f"✅ 打开输出成功 -> 默认设备 ({label})")
            return stream
        except Exception as e:
            print(f"⚠️ 尝试 {label} 失败: {e}")
            last_err = e

    # fallback 44.1k int16
    try:
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, output=True, frames_per_buffer=1024, start=False)
        stream.start_stream()
        print("✅ 回退 44100Hz Int16 打开成功")
        return stream
    except Exception as e3:
        print(f"❌ 全部失败: {e3}")
        if last_err:
            raise last_err
        raise


def gen_sine_float32(freq=440.0, duration=2.0, sr=24000, amp=0.3):
    total = int(sr * duration)
    data = bytearray()
    for n in range(total):
        val = amp * math.sin(2 * math.pi * freq * (n / sr))
        data.extend(struct.pack('<f', val))
    return bytes(data)


def main():
    p = pyaudio.PyAudio()
    list_devices(p)
    stream = open_output_stream(p)

    print("🔊 播放 2 秒 440Hz 测试音...")
    tone = gen_sine_float32()

    # 分块写入
    frames_per_write = 512
    sample_size = p.get_sample_size(OUTPUT_CONFIG['bit_size'])
    bytes_per_frame = sample_size * OUTPUT_CONFIG['channels']
    chunk = frames_per_write * bytes_per_frame

    for i in range(0, len(tone), chunk):
        stream.write(tone[i:i+chunk], exception_on_underflow=False)
        time.sleep(0.001)

    time.sleep(0.1)
    stream.stop_stream()
    stream.close()
    p.terminate()
    print("✅ 播放完成。若仍无声，请尝试：\n- 检查系统音量与输出设备\n- 设置环境变量 DRAGON_AUDIO_DEVICE_INDEX 指定正确设备索引\n- 确认 PulseAudio 正在运行 (pulseaudio --check)")

if __name__ == '__main__':
    main()
