#!/usr/bin/env python3
import os
from dotenv import load_dotenv

load_dotenv()

KEYS = [
	"DOUBAO_API_KEY",
	"DOUBAO_BASE_URL",
	"DOUBAO_MODEL",
	"DOUBAO_WS_BASE_URL",
	"DOUBAO_API_APP_ID",
	"DOUBAO_API_ACCESS_KEY",
	"DOUBAO_API_APP_KEY",
	"DOUBAO_API_RESOURCE_ID",
]

def mask(val: str) -> str:
	if not val:
		return ""
	if len(val) <= 8:
		return "*" * len(val)
	return val[:4] + "*" * (len(val) - 8) + val[-4:]

def main():
	print("=== 环境变量自检 (dotenv + os.environ) ===")
	for k in KEYS:
		v = os.getenv(k, "")
		print(f"{k} = {mask(v)}" if v else f"{k} = (未设置)")
	print("\n提示：\n- 复制 .env.example 为 .env 并填好值；\n- 你也可以直接 export 这些变量。\n- WebSocket 头字段通常需要 APP_ID/ACCESS_KEY/APP_KEY/RESOURCE_ID 四个。")

if __name__ == "__main__":
	main()
