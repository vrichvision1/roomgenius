"""
Lifecycle Hooks สำหรับตรวจสอบ ติดตามการทำความเข้าใจ และกู้คืนข้อผิดพลาดในการทำงานของ AI Agent
"""

import logging
from google.antigravity import hooks

logger = logging.getLogger("roomgenius.audit")

@hooks.post_tool_call
async def audit_tool_calls(data):
    """
    บันทึกการใช้งานเครื่องมือ (Tool Call) ทุกครั้งลงในระบบ Log เพื่อนำไปทำ Audit Trail
    """
    result_str = str(data.result)[:200]
    logger.info(
        f"[AUDIT] AI รันเครื่องมือ: {data.name} | ผลลัพธ์: {result_str}"
    )

@hooks.on_tool_error
async def handle_tool_error(data):
    """
    จัดการเมื่อเกิดข้อผิดพลาดในการรันเครื่องมือ ป้องกันไม่ให้ระบบแครช
    และคืนคำแนะนำเพื่อให้ AI สามารถลองวิเคราะห์วิธีอื่นได้
    """
    logger.error(
        f"[ERROR] เครื่องมือทำงานผิดพลาด: {data}"
    )
    # คืนค่าข้อความเพื่อให้ AI เข้าใจว่าเกิดปัญหาขึ้น
    return f"เกิดข้อผิดพลาดในการใช้งานเครื่องมือ: {data}. กรุณาตรวจสอบข้อมูลนำเข้าและลองใหม่อีกครั้ง"

@hooks.on_session_start
async def on_session_start():
    """
    แจ้งเตือนการเริ่มทำงานของเซสชันใหม่
    """
    logger.info("เริ่มเซสชันสนทนากับ AI ใหม่")

# รวม hooks ทั้งหมดเพื่อนำไปใช้งาน
all_hooks = [
    audit_tool_calls,
    handle_tool_error,
    on_session_start,
]
