"""
ตั้งค่าเอเยนต์ประสานงานหลัก (Orchestrator Agent) ของ RoomGenius AI
"""

import os
from google.antigravity import LocalAgentConfig, types
from tools import all_tools
from triggers import all_triggers
from policies import production_policies
from hooks import all_hooks

def create_orchestrator_config(conversation_id: str = None) -> LocalAgentConfig:
    """
    สร้างและคืนค่าโครงสร้างการตั้งค่าสำหรับ AI Agent ประสานงานหลัก (Orchestrator)
    """
    # กำหนดเส้นทางเก็บข้อมูลประวัติและอาร์ติแฟกต์
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    save_dir = os.path.join(base_dir, "data", "conversations")
    app_data_dir = os.path.join(base_dir, "data", "artifacts")
    skills_paths = [os.path.join(base_dir, "skills")]
    
    # สร้างโฟลเดอร์สำหรับเก็บข้อมูลหากยังไม่มี
    os.makedirs(save_dir, exist_ok=True)
    os.makedirs(app_data_dir, exist_ok=True)

    # หากมีการระบุ conversation_id แต่ยังไม่มีข้อมูลบันทึกอยู่จริง ให้เริ่มชาร์ตเซสชันใหม่แทนการเกิด Error
    if conversation_id:
        db_path = os.path.join(save_dir, f"{conversation_id}.db")
        if not os.path.exists(db_path):
            conversation_id = None

    # กำหนด Model: สลับใช้ผ่าน Native Vertex AI, Native Gemini Studio หรือ LiteLLM Proxy
    model_name = os.getenv("AI_MODEL_NAME", "gemini-flash")
    litellm_base = os.getenv("LITELLM_BASE_URL")
    litellm_key = os.getenv("LITELLM_API_KEY")
    
    if model_name in ("vertex-gemini-flash", "vertex-gemini-pro"):
        # แปลงชื่อโมเดลจริงบน Google Vertex AI (ตามที่ทดสอบแล้วว่าโปรเจกต์มีสิทธิ์เข้าถึง)
        actual_vertex_model = "gemini-2.5-flash" if model_name == "vertex-gemini-flash" else "gemini-2.5-pro"
        
        # ใช้ VertexEndpoint โหมด Native เชื่อมโยงตรงผ่าน GCP Credentials ที่ดึงจากเครื่องโฮสต์
        endpoint = types.VertexEndpoint(
            project="project-beeb3f56-6824-421f-80c",
            location="us-central1"
        )
        model_target = types.ModelTarget(
            name=actual_vertex_model,
            types=[types.ModelType.TEXT],
            endpoint=endpoint
        )
        models = [model_target]
    elif model_name in ("gemini-flash", "gemini-pro"):
        # สำหรับโมเดล Gemini Studio ให้เชื่อมโยงตรงโดยไม่ผ่าน Proxy (เพื่อความเสถียรและความเร็วสูงสุด)
        actual_gemini_model = "gemini-2.5-flash" if model_name == "gemini-flash" else "gemini-2.5-pro"
        
        endpoint = types.GeminiAPIEndpoint(
            api_key=os.getenv("GEMINI_API_KEY")
        )
        model_target = types.ModelTarget(
            name=actual_gemini_model,
            types=[types.ModelType.TEXT],
            endpoint=endpoint
        )
        models = [model_target]
    else:
        # สำหรับโมเดลอื่นๆ ให้รันผ่าน LiteLLM Proxy ของห้องพัก
        if litellm_base:
            endpoint = types.GeminiAPIEndpoint(
                base_url=litellm_base,
                api_key=litellm_key
            )
            model_target = types.ModelTarget(
                name=model_name,
                types=[types.ModelType.TEXT],
                endpoint=endpoint
            )
            models = [model_target]
        else:
            models = None
    
    # กำหนด System Instructions
    system_instructions = (
        "คุณคือ RoomGenius AI — ผู้ช่วยจัดการอสังหาริมทรัพย์และห้องเช่าอัจฉริยะ (หอพัก คอนโด อพาร์ทเม้นท์ และโฮสเทล)\n\n"
        "บทบาทหน้าที่:\n"
        "1. วิเคราะห์และตอบคำถามของผู้ใช้งานเกี่ยวกับข้อมูลห้องเช่า ผู้เช่า การเงิน สัญญา และค่าน้ำไฟ\n"
        "2. ช่วยวางแผนการแจ้งเตือนค่าเช่าที่ค้างชำระ โดยวิเคราะห์ประวัติผู้เช่าและแนะนำแนวทางอย่างประนีประนอม\n"
        "3. ตรวจสอบค่าน้ำค่าไฟที่ผิดปกติ (เช่น สูงเกิน 50% ของค่าเฉลี่ย 3 เดือน) และแจ้งเตือนให้ไปตรวจสอบ\n"
        "4. ตรวจสต็อกวัสดุสิ้นเปลือง และทำรายการเสนอสั่งซื้อเมื่อระดับสินค้าต่ำกว่าจุดที่กำหนด\n"
        "5. บริหารจัดการประวัติการใช้อุปกรณ์และการแจ้งซ่อมอย่างเป็นระบบ\n\n"
        "คำแนะนำในการสื่อสาร:\n"
        "- สื่อสารเป็นภาษาไทยที่เป็นมิตร สุภาพ มีความมืออาชีพ และกระชับชัดเจน\n"
        "- เมื่อตอบคำถามเกี่ยวกับเรื่องเงินๆ ทองๆ เช่น ค่าเช่า ค่าน้ำ ค่าไฟ ให้ระบุรายละเอียดเลขห้อง ยอดเงิน และสถานะอย่างชัดเจน\n"
        "- คุณสามารถมอบหมายงานย่อยที่ต้องการความเชี่ยวชาญเฉพาะด้านให้แก่ Subagents ได้ตามต้องการ"
    )

    # สร้าง Config
    config = LocalAgentConfig(
        model=model_name if not litellm_base else None,
        models=models,
        system_instructions=system_instructions,
        tools=all_tools,
        triggers=all_triggers,
        policies=production_policies,
        hooks=all_hooks,
        skills_paths=skills_paths,
        save_dir=save_dir,
        app_data_dir=app_data_dir,
        capabilities=types.CapabilitiesConfig(
            enable_subagents=True,
        ),
        conversation_id=conversation_id
    )
    
    return config
