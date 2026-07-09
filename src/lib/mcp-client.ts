import { spawn } from "child_process";
import path from "path";
import fs from "fs";

/**
 * เรียกใช้งานเครื่องมือ (Tool) บน Python AGY Engine โดยตรงผ่านช่องทาง CLI Subprocess
 * 
 * @param toolName ชื่อเครื่องมือ เช่น chat_with_ai, switch_ai_model
 * @param args อาร์กิวเมนต์ที่ต้องการส่งให้เครื่องมือ
 * @returns ผลลัพธ์ในรูปแบบเดียวกับ MCP response เพื่อให้สอดคล้องกับ API route เดิม
 */
export async function callMcpTool(toolName: string, args: Record<string, any> = {}) {
  const modelFilePath = path.join(process.cwd(), "agy-engine", "data", "selected_model.txt");

  try {
    if (toolName === "chat_with_ai") {
      // อ่านโมเดลปัจจุบันที่ผู้ใช้เลือกไว้จากไฟล์ข้อความ
      let selectedModel = "vertex-gemini-flash";
      if (fs.existsSync(modelFilePath)) {
        selectedModel = fs.readFileSync(modelFilePath, "utf8").trim();
      }

      return new Promise((resolve, reject) => {
        const cliPath = path.join(process.cwd(), "agy-engine", "cli.py");
        const pythonProcess = spawn("python3", [cliPath]);

        let stdout = "";
        let stderr = "";

        pythonProcess.stdout.on("data", (data) => {
          stdout += data.toString();
        });

        pythonProcess.stderr.on("data", (data) => {
          stderr += data.toString();
        });

        pythonProcess.on("close", (code) => {
          if (code !== 0) {
            console.error(`CLI execution failed (code ${code}):`, stderr);
            reject(new Error(`CLI error: Code ${code}. Stderr: ${stderr}`));
            return;
          }

          try {
            const data = JSON.parse(stdout);
            resolve({
              content: [
                {
                  type: "text",
                  text: JSON.stringify(data),
                },
              ],
            });
          } catch (err) {
            reject(new Error(`Failed to parse CLI output: ${stdout}`));
          }
        });

        // ส่งข้อความประเด็นพูดคุยและคอนฟิกไปให้ stdin ของ Python CLI
        const payload = {
          message: args.message,
          conversation_id: args.conversation_id || null,
          model_name: selectedModel
        };
        pythonProcess.stdin.write(JSON.stringify(payload));
        pythonProcess.stdin.end();
      });

    } else if (toolName === "switch_ai_model") {
      // บันทึกโมเดลที่เลือกลงไฟล์
      const dirPath = path.dirname(modelFilePath);
      if (!fs.existsSync(dirPath)) {
        fs.mkdirSync(dirPath, { recursive: true });
      }
      fs.writeFileSync(modelFilePath, args.model_name, "utf8");

      return {
        content: [
          {
            type: "text",
            text: JSON.stringify({
              status: "success",
              provider: args.provider,
              model_name: args.model_name,
              message: `สลับไปใช้โมเดล ${args.model_name} เรียบร้อยแล้ว`,
            }),
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
