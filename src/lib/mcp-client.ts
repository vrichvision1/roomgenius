import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { SSEClientTransport } from "@modelcontextprotocol/sdk/client/sse.js";

/**
 * เรียกใช้งานเครื่องมือ (Tool) บน Python MCP Server (AGY Engine)
 * 
 * @param toolName ชื่อเครื่องมือ เช่น chat_with_ai, get_ai_insights, switch_ai_model
 * @param args อาร์กิวเมนต์ที่ต้องการส่งให้เครื่องมือ
 * @returns ผลลัพธ์จากการรันเครื่องมือ
 */
export async function callMcpTool(toolName: string, args: Record<string, any> = {}) {
  const host = process.env.MCP_SERVER_HOST || "localhost";
  const port = process.env.MCP_SERVER_PORT || "8765";
  const url = new URL(`http://${host}:${port}/sse`);

  const transport = new SSEClientTransport(url);
  const client = new Client(
    {
      name: "NextJsMcpClient",
      version: "1.0.0",
    },
    {
      capabilities: {},
    }
  );

  try {
    await client.connect(transport);
    const response = await client.callTool({
      name: toolName,
      arguments: args,
    });
    return response;
  } catch (error) {
    console.error(`Error calling MCP tool ${toolName}:`, error);
    throw error;
  } finally {
    // ปิดการเชื่อมต่อเสมอหลังใช้งานเสร็จ
    try {
      await client.close();
    } catch (closeError) {
      console.error("Error closing MCP transport:", closeError);
    }
  }
}
