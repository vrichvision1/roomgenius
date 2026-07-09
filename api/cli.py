"""
RoomGenius AI Engine — CLI Wrapper
ใช้สำหรับเรียกใช้งาน AI Agent โดยตรงผ่าน CLI/Subprocess (ไม่ต้องผ่าน API Web Server)
"""

import sys
import os
import asyncio
import json
from dotenv import load_dotenv

# เพิ่มเส้นทางโมดูลหลักเข้า sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# โหลด Environment Variables
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(root_dir, ".env"))

# ตั้งค่า GCP credentials ถ้ามีระบุผ่านสภาพแวดล้อม
gcp_creds = os.getenv("GCP_CREDS_JSON")
if gcp_creds:
    import tempfile
    try:
        temp_dir = tempfile.gettempdir()
        creds_path = os.path.join(temp_dir, "gcp-creds.json")
        with open(creds_path, "w") as f:
            f.write(gcp_creds)
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = creds_path
    except Exception as e:
        sys.stderr.write(f"Error setting GCP credentials: {e}\n")

from google.antigravity import Agent
from agents.orchestrator import create_orchestrator_config

async def main():
    # อ่าน input ในรูปแบบ JSON จาก standard input (หลีกเลี่ยงปัญหาการแปลงเครื่องหมายคำพูดใน shell)
    try:
        input_data = json.loads(sys.stdin.read())
        message = input_data.get("message", "")
        conversation_id = input_data.get("conversation_id", None)
        model_name = input_data.get("model_name", None)
    except Exception as e:
        sys.stderr.write(f"Error parsing input JSON: {e}\n")
        sys.exit(1)

    if not message:
        sys.stderr.write("Error: message is required\n")
        sys.exit(1)

    if model_name:
        os.environ["AI_MODEL_NAME"] = model_name

    try:
        # สตาร์ท AI Agent ด้วย configuration
        config = create_orchestrator_config(conversation_id=conversation_id)
        async with Agent(config) as agent:
            response = await agent.chat(message)
            response_text = await response.text()
            
            output = {
                "status": "success",
                "response": response_text,
                "conversation_id": agent.conversation_id
            }
            print(json.dumps(output, ensure_ascii=False))
    except Exception as e:
        sys.stderr.write(f"Error running agent: {e}\n")
        output = {
            "status": "error",
            "message": str(e)
        }
        print(json.dumps(output, ensure_ascii=False))
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
