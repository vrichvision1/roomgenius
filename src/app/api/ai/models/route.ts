import { NextRequest, NextResponse } from "next/server";
import { callMcpTool } from "@/lib/mcp-client";

// รายชื่อ AI Models ทั้งหมดที่รองรับ
const AI_MODELS = [
  { id: 'gemini-flash', name: 'Gemini Flash', provider: 'Google', icon: '✨', description: 'โมเดลรวดเร็ว คุ้มค่าที่สุด สำหรับงานทั่วไป' },
  { id: 'gemini-pro', name: 'Gemini Pro', provider: 'Google', icon: '🧠', description: 'โมเดลขั้นสูง สำหรับการวิเคราะห์เชิงลึก' },
  { id: 'gpt-4o', name: 'ChatGPT 4o', provider: 'OpenAI', icon: '💚', description: 'โมเดลอัจฉริยะจาก OpenAI ประมวลผลได้ดีเยี่ยม' },
  { id: 'gpt-4o-mini', name: 'GPT-4o Mini', provider: 'OpenAI', icon: '⚡', description: 'รวดเร็วและคุ้มราคา เหมาะกับงานสกัดข้อมูล' },
  { id: 'claude-sonnet', name: 'Claude Sonnet', provider: 'Anthropic', icon: '🟠', description: 'โมเดลวิเคราะห์ข้อมูลและการเขียนที่ลื่นไหล' },
  { id: 'claude-haiku', name: 'Claude Haiku', provider: 'Anthropic', icon: '🟡', description: 'โมเดลขนาดเล็ก ทำงานเร็วเป็นพิเศษ' },
  { id: 'vertex-gemini-flash', name: 'Vertex Gemini Flash', provider: 'VertexAI', icon: '☁️', description: 'Google Vertex AI Gemini Flash สำหรับการใช้งานระดับองค์กร' },
  { id: 'vertex-gemini-pro', name: 'Vertex Gemini Pro', provider: 'VertexAI', icon: '🌐', description: 'Google Vertex AI Gemini Pro คุณภาพสูงสุด บนระบบคลาวด์องค์กร' },
];

export async function GET() {
  return NextResponse.json({
    status: "success",
    models: AI_MODELS,
    model_name: process.env.AI_MODEL_NAME || "vertex-gemini-flash",
  });
}

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { provider, modelName } = body;

    if (!provider || !modelName) {
      return NextResponse.json(
        { error: "กรุณาระบุ provider และ modelName" },
        { status: 400 }
      );
    }

    // เรียกใช้เครื่องมือ switch_ai_model บน Python AGY Engine ผ่าน MCP Bridge
    const mcpResponse = await callMcpTool("switch_ai_model", {
      provider,
      model_name: modelName,
    });

    if (mcpResponse && mcpResponse.content && mcpResponse.content.length > 0) {
      const firstContent = mcpResponse.content[0];
      if (firstContent.type === "text") {
        const parsedResult = JSON.parse(firstContent.text);
        return NextResponse.json(parsedResult);
      }
    }

    return NextResponse.json(
      { error: "ไม่ได้รับคำตอบที่ถูกต้องจาก AI Engine" },
      { status: 500 }
    );
  } catch (error: any) {
    console.error("Error in AI Model Switch API route:", error);
    return NextResponse.json(
      { error: `เกิดข้อผิดพลาดในการสลับโมเดล AI: ${error.message}` },
      { status: 500 }
    );
  }
}
