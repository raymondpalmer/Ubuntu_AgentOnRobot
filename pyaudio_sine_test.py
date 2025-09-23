import time
import math
import pyaudio

RATE = 24000
CH = 1
FMT = pyaudio.paFloat32
DURATION = 1.5
FREQ = 440.0

p = pyaudio.PyAudio()
print('设备数量:', p.get_device_count())
for i in range(p.get_device_count()):
    info = p.get_device_info_by_index(i)
    print(i, info.get('name'), 'out', info.get('maxOutputChannels'))

# 选择pulse设备优先
device_index = 0 if p.get_device_count() > 0 else None

sample_size = p.get_sample_size(FMT)
bytes_per_frame = sample_size * CH
frames_per_buffer = max(64, 1600 // bytes_per_frame)

stream = p.open(
    format=FMT,
    channels=CH,
    rate=RATE,
    output=True,
    frames_per_buffer=frames_per_buffer,
    output_device_index=device_index,
    start=False,
)
stream.start_stream()

# 生成正弦波块并写入
frames_per_write = 512
bytes_per_write = frames_per_write * bytes_per_frame

t = 0.0
step = 1.0 / RATE

def make_chunk(n):
    import numpy as np
    ts = (t + step * np.arange(n)).astype(np.float32)
    sig = (0.2 * np.sin(2 * math.pi * FREQ * ts)).astype(np.float32)
    return sig.tobytes(), float(ts[-1])

import numpy as np
samples_total = int(DURATION * RATE)
written = 0
while written < samples_total:
    need = min(frames_per_write, samples_total - written)
    buf, tlast = make_chunk(need)
    # 等待可写帧
    while True:
        try:
            avail = stream.get_write_available()
            if avail >= frames_per_write:
                break
        except Exception:
            break
        time.sleep(0.001)
    stream.write(buf, exception_on_underflow=False)
    written += need
    t = t + need * step

stream.stop_stream()
stream.close()
p.terminate()
print('正弦波播放完成')
