import { NextRequest, NextResponse } from "next/server";
import { callMcpTool } from "@/lib/mcp-client";

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { message, conversationId } = body;

    if (!message) {
      return NextResponse.json(
        { error: "กรุณาส่งข้อความ (message) ที่ต้องการสนทนา" },
        { status: 400 }
      );
    }

    const args: Record<string, any> = { message };
    if (conversationId) {
      args.conversation_id = conversationId;
    }

    // เรียกใช้งานเครื่องมือ chat_with_ai บน Python AGY Engine ผ่าน MCP Bridge
    const mcpResponse = await callMcpTool("chat_with_ai", args);

    // ผลลัพธ์จาก MCP จะอยู่ในรูป text ใน content array
    if (mcpResponse && mcpResponse.content && mcpResponse.content.length > 0) {
      const firstContent = mcpResponse.content[0];
      if (firstContent.type === "text") {
        try {
          const parsedResult = JSON.parse(firstContent.text);
          return NextResponse.json(parsedResult);
        } catch (jsonError: any) {
          console.error("Failed to parse JSON. Raw text was:", firstContent.text);
          throw jsonError;
        }
      }
    }

    return NextResponse.json(
      { error: "ไม่ได้รับคำตอบที่ถูกต้องจาก AI Engine" },
      { status: 500 }
    );
  } catch (error: any) {
    console.error("Error in AI Chat API route:", error);
    return NextResponse.json(
      { error: `เกิดข้อผิดพลาดในการเชื่อมต่อกับ AI Engine: ${error.message}` },
      { status: 500 }
    );
  }
}
