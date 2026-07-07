/**
 * เรียกใช้งานเครื่องมือ (Tool) บน Python FastAPI Backend (แทนที่ MCP Client เดิม)
 * 
 * @param toolName ชื่อเครื่องมือ เช่น chat_with_ai, switch_ai_model
 * @param args อาร์กิวเมนต์ที่ต้องการส่งให้เครื่องมือ
 * @returns ผลลัพธ์ในรูปแบบเดียวกับ MCP response เพื่อให้สอดคล้องกับ API route เดิม
 */
export async function callMcpTool(toolName: string, args: Record<string, any> = {}) {
  // ในพัฒนาการ (development): เชื่อมต่อไปยังพอร์ต 8765 ที่ uvicorn รัน
  // ในโปรดักชัน (production): เชื่อมต่อผ่านโดเมนตัวเองบน Vercel
  const isDev = process.env.NODE_ENV === "development";
  const baseUrl = isDev
    ? "http://127.0.0.1:8765"
    : `https://${process.env.VERCEL_URL || "roomgenius.vercel.app"}`;

  try {
    if (toolName === "chat_with_ai") {
      const response = await fetch(`${baseUrl}/api/python/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: args.message,
          conversation_id: args.conversation_id || null,
        }),
      });

      if (!response.ok) {
        throw new Error(`FastAPI chat error: ${response.statusText}`);
      }

      const data = await response.json();
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(data),
          },
        ],
      };
    } else if (toolName === "switch_ai_model") {
      const response = await fetch(`${baseUrl}/api/python/models`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          provider: args.provider,
          modelName: args.model_name,
        }),
      });

      if (!response.ok) {
        throw new Error(`FastAPI model switch error: ${response.statusText}`);
      }

      const data = await response.json();
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(data),
          },
        ],
      };
    } else {
      throw new Error(`Unsupported tool name: ${toolName}`);
    }
  } catch (error) {
    console.error(`Error in callMcpTool bridge (${toolName}):`, error);
    throw error;
  }
}
