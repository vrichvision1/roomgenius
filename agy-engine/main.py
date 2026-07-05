"""
RoomGenius AI Engine — Main Entry Point
สตาร์ทระบบ AI Agent และบริการเชื่อมต่อ Next.js (MCP Bridge Server)
"""

import sys
import os
from dotenv import load_dotenv

# เพิ่มเส้นทางโมดูลหลักเข้า sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# โหลด Environment Variables จากไฟล์ .env ในโครงการหลัก
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(root_dir, ".env"))

from mcp_bridge.server import run_mcp_server

def main():
    print("==================================================")
    print("       🚀 RoomGenius AI Engine (Python) 🚀        ")
    print("==================================================")
    
    # รัน MCP server เพื่อรอนัดหมายเชื่อมโยงจาก Next.js
    run_mcp_server()

if __name__ == "__main__":
    main()
