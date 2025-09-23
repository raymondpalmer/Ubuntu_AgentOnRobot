
import json
import os
import threading
import time
from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

# ROS2
import rclpy
from rclpy.node import Node
from std_msgs.msg import String as StringMsg


class MoveJointReq(BaseModel):
    joint: str
    position_deg: float
    speed: Optional[float] = 0.5


class ROS2Bridge(Node):
    def __init__(self):
        super().__init__("agent_action_router")
        self.pub = self.create_publisher(StringMsg, "/agent/actions", 10)
        self.get_logger().info("ROS2Bridge ready: publishing to /agent/actions")

    def publish_action(self, tool: str, args: dict):
        payload = {
            "tool": tool,
            "args": args,
            "source": "agent",
            "ts": time.time(),
        }
        msg = StringMsg()
        msg.data = json.dumps(payload, ensure_ascii=False)
        self.pub.publish(msg)
        self.get_logger().info(f"Published: {msg.data}")


app = FastAPI()
ros2_node: Optional[ROS2Bridge] = None


@app.get("/healthz")
def health():
    return {"ok": True}


@app.post("/move_joint")
def move_joint(req: MoveJointReq):
    assert ros2_node is not None, "ROS2 node not ready"
    ros2_node.publish_action("move_joint", req.dict())
    return {"status": "published"}


def ros2_thread():
    global ros2_node
    rclpy.init()
    ros2_node = ROS2Bridge()
    rclpy.spin(ros2_node)
    ros2_node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    t = threading.Thread(target=ros2_thread, daemon=True)
    t.start()

    port = int(os.getenv("PORT", "8008"))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
