"""
MCP Bridge Server สำหรับเชื่อมต่อระหว่าง Next.js (TypeScript) กับ Antigravity AI Engine (Python)
"""

import os
import json
import logging
from fastmcp import FastMCP
from google.antigravity import Agent
from agents.orchestrator import create_orchestrator_config

# ตั้งค่า Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("roomgenius.mcp")

# สร้าง MCP Server instance
mcp = FastMCP("RoomGeniusAI")

@mcp.tool()
async def chat_with_ai(message: str, conversation_id: str | None = None) -> str:
    """
    ส่งข้อความสนทนากับ AI Agent หลักเพื่อวิเคราะห์ข้อมูลหรือสั่งการทำงาน
    
    Args:
        message: ข้อความคำถามหรือคำสั่งภาษาไทย
        conversation_id: รหัสเซสชันสนทนาเดิมเพื่อความต่อเนื่อง (หากมี)
    """
    logger.info(f"MCP Call: chat_with_ai | message: '{message[:30]}...' | conv_id: {conversation_id}")
    try:
        config = create_orchestrator_config(conversation_id=conversation_id)
        async with Agent(config) as agent:
            response = await agent.chat(message)
            response_text = await response.text()
            
            return json.dumps({
                "status": "success",
                "response": response_text,
                "conversation_id": agent.conversation_id,
            }, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error in chat_with_ai: {e}")
        return json.dumps({
            "status": "error",
            "message": f"เกิดข้อผิดพลาดในการสนทนากับ AI: {str(e)}"
        }, ensure_ascii=False)

@mcp.tool()
async def get_ai_insights(property_id: str) -> str:
    """
    ให้ AI วิเคราะห์ข้อมูลของอสังหาริมทรัพย์และรายงาน Insights ล่าสุด (น้ำ/ไฟ/ค้างชำระ)
    
    Args:
        property_id: รหัสอสังหาริมทรัพย์ที่ต้องการวิเคราะห์
    """
    logger.info(f"MCP Call: get_ai_insights | property_id: {property_id}")
    try:
        config = create_orchestrator_config()
        async with Agent(config) as agent:
            prompt = (
                f"ช่วยวิเคราะห์ภาพรวมข้อมูลของอสังหาริมทรัพย์รหัส {property_id} "
                "ตรวจสอบค่าน้ำค่ายูนิตไฟที่ผิดปกติ, สต็อกของใช้สิ้นเปลือง และผู้เช่าค้างชำระค่าเช่า "
                "สรุปเป็น Insights ออกมาสั้นๆ 3-5 บรรทัด"
            )
            response = await agent.chat(prompt)
            response_text = await response.text()
            return json.dumps({
                "status": "success",
                "insights": response_text
            }, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error in get_ai_insights: {e}")
        return json.dumps({
            "status": "error",
            "message": str(e)
        }, ensure_ascii=False)

@mcp.tool()
async def switch_ai_model(provider: str, model_name: str) -> str:
    """
    สลับไปใช้ AI Model ของค่ายต่างๆ (Gemini, ChatGPT, Claude)
    
    Args:
        provider: ชื่อค่าย เช่น gemini, openai, anthropic
        model_name: ชื่อโมเดล เช่น gemini-flash, gpt-4o, claude-sonnet
    """
    logger.info(f"MCP Call: switch_ai_model | provider: {provider} | model_name: {model_name}")
    try:
        model_mapping = {
            "gemini-flash": "gemini-flash",
            "gemini-pro": "gemini-pro",
            "gpt-4o": "gpt-4o",
            "gpt-4o-mini": "gpt-4o-mini",
            "claude-sonnet": "claude-sonnet",
            "claude-haiku": "claude-haiku",
            "vertex-gemini-flash": "vertex-gemini-flash",
            "vertex-gemini-pro": "vertex-gemini-pro",
        }
        
        mapped_model = model_mapping.get(model_name, "gemini-flash")
        
        # ตั้งค่า Environment Variable เพื่อให้ create_orchestrator_config นำไปใช้
        os.environ["AI_MODEL_NAME"] = mapped_model
        
        return json.dumps({
            "status": "success",
            "message": f"สลับไปใช้งานโมเดล {mapped_model} (ค่าย {provider}) สำเร็จ",
            "model_name": mapped_model
        }, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error in switch_ai_model: {e}")
        return json.dumps({
            "status": "error",
            "message": str(e)
        }, ensure_ascii=False)

@mcp.tool()
async def trigger_analysis(analysis_type: str, target_id: str) -> str:
    """
    สั่ง AI วิเคราะห์ข้อมูลเฉพาะ (เช่น สัญญาเช่า, การเงิน)
    
    Args:
        analysis_type: ประเภทการวิเคราะห์ เช่น lease, financial, utility, supply
        target_id: รหัสเป้าหมาย เช่น เลขห้อง หรือ รหัสสัญญา
    """
    logger.info(f"MCP Call: trigger_analysis | type: {analysis_type} | target_id: {target_id}")
    try:
        config = create_orchestrator_config()
        async with Agent(config) as agent:
            if analysis_type == "lease":
                prompt = f"ช่วยสรุปประเด็นสำคัญและวิเคราะห์ความเสี่ยงในสัญญาเช่าของห้อง {target_id} ให้หน่อย"
            elif analysis_type == "financial":
                prompt = f"ช่วยวิเคราะห์ประวัติการเงินและการชำระค่าเช่าของห้อง {target_id} ย้อนหลัง"
            elif analysis_type == "utility":
                prompt = f"ช่วยตรวจสอบค่าน้ำและค่าไฟของห้อง {target_id} ว่ามีระดับการใช้งานผิดปกติหรือไม่"
            else:
                prompt = f"ช่วยวิเคราะห์สถานะสต็อกของใช้สิ้นเปลืองของไอเทมรหัส {target_id}"
                
            response = await agent.chat(prompt)
            response_text = await response.text()
            return json.dumps({
                "status": "success",
                "analysis": response_text
            }, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error in trigger_analysis: {e}")
        return json.dumps({
            "status": "error",
            "message": str(e)
        }, ensure_ascii=False)

def run_mcp_server():
    """
    เริ่มการทำงานของ MCP Server โดยใช้ SSE transport ตามพอร์ตที่กำหนด
    """
    port = int(os.getenv("MCP_SERVER_PORT", 8765))
    host = os.getenv("MCP_SERVER_HOST", "0.0.0.0")
    logger.info(f"กำลังเริ่ม MCP Server (SSE) ที่ {host}:{port}...")
    mcp.run(transport="sse", host=host, port=port)

if __name__ == "__main__":
    run_mcp_server()
