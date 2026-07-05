'use client';

import React, { useState, useRef, useEffect } from 'react';

type Message = {
  id: string;
  role: 'user' | 'ai';
  content: string;
  timestamp: Date;
  model?: string;
};

const AI_MODELS = [
  { id: 'gemini-flash', name: 'Gemini Flash', provider: 'Google', icon: '✨', color: '#4285f4' },
  { id: 'gemini-pro', name: 'Gemini Pro', provider: 'Google', icon: '🧠', color: '#4285f4' },
  { id: 'gpt-4o', name: 'ChatGPT 4o', provider: 'OpenAI', icon: '💚', color: '#10a37f' },
  { id: 'gpt-4o-mini', name: 'GPT-4o Mini', provider: 'OpenAI', icon: '⚡', color: '#10a37f' },
  { id: 'claude-sonnet', name: 'Claude Sonnet', provider: 'Anthropic', icon: '🟠', color: '#d97706' },
  { id: 'claude-haiku', name: 'Claude Haiku', provider: 'Anthropic', icon: '🟡', color: '#d97706' },
  { id: 'vertex-gemini-flash', name: 'Vertex Gemini Flash', provider: 'VertexAI', icon: '☁️', color: '#34a853' },
  { id: 'vertex-gemini-pro', name: 'Vertex Gemini Pro', provider: 'VertexAI', icon: '🌐', color: '#34a853' },
];

const QUICK_COMMANDS = [
  '📊 สรุปรายได้เดือนนี้',
  '💰 ห้องไหนยังไม่จ่ายค่าเช่า?',
  '⚡ ค่าน้ำ/ค่าไฟห้องไหนผิดปกติ?',
  '📋 สัญญาไหนใกล้หมดอายุ?',
  '🧻 วัสดุอะไรใกล้หมด?',
  '🏠 Occupancy rate ตอนนี้เท่าไหร่?',
  '🔧 งานซ่อมที่ยังค้างอยู่?',
  '📈 เปรียบเทียบรายได้กับเดือนที่แล้ว',
];

// Demo AI responses
const DEMO_RESPONSES: Record<string, string> = {
  'สรุปรายได้เดือนนี้': `📊 **สรุปรายได้เดือน กรกฎาคม 2569**

| รายการ | จำนวน |
|:---|---:|
| รายได้ค่าเช่า | ฿231,000 |
| ค่าน้ำ/ค่าไฟ | ฿16,500 |
| ค่าส่วนกลาง | ฿12,000 |
| **รายได้รวม** | **฿259,500** |

📈 เพิ่มขึ้น 12% จากเดือน มิ.ย. (฿231,700)
✅ อัตราการเก็บเงินได้ 92% (42/48 ห้อง)
⚠️ ค้างชำระ 6 ห้อง รวม ฿35,000`,

  'ห้องไหนยังไม่จ่ายค่าเช่า': `💰 **ห้องที่ยังไม่ชำระค่าเช่าเดือน ก.ค. 2569**

🔴 **เกินกำหนด (2 ห้อง)**
1. ห้อง 203 — ธนพล รักเรียน — ฿5,500 (เกิน 3 วัน)
2. ห้อง 108 — ปิยะ สวัสดี — ฿5,000 (เกิน 3 วัน)

🟡 **รอชำระ (4 ห้อง)**
3. ห้อง 302 — จิราพร ใจดี — ฿7,500
4. ห้อง 310 — สุนิสา เก่ง — ฿6,000
5. ห้อง 405 — วรวุฒิ คงดี — ฿7,000
6. ห้อง 412 — พิมพ์ ลออ — ฿4,000

💡 **คำแนะนำ**: ส่งแจ้งเตือนทาง LINE ให้ห้อง 203 และ 108 ก่อน เพราะเกินกำหนดแล้ว ต้องการให้ส่งเตือนเลยไหม?`,

  default: `ขอบคุณสำหรับคำถามครับ 🙏

ขณะนี้ระบบกำลังอยู่ในโหมด Demo ยังไม่ได้เชื่อมต่อกับฐานข้อมูลจริง

เมื่อเชื่อมต่อ API แล้ว AI จะสามารถ:
- 📊 วิเคราะห์ข้อมูลรายได้/รายจ่าย
- 💰 ตรวจสอบสถานะค่าเช่า
- ⚡ ตรวจจับค่าน้ำ/ไฟผิดปกติ
- 📋 จัดการสัญญาเช่า
- 🧻 ติดตามวัสดุสิ้นเปลือง
- 🔧 จัดลำดับงานซ่อม

สามารถตั้งค่า API Key ได้ที่หน้า **ตั้งค่า > AI Configuration**`,
};

export default function AIAssistantPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'ai',
      content: `สวัสดีครับ! 👋 ผมคือ **RoomGenius AI** — ผู้ช่วยจัดการห้องเช่าอัจฉริยะของคุณ

ถามผมได้ทุกเรื่องเกี่ยวกับ:
- 📊 รายได้ / รายจ่าย / สถิติ
- 💰 สถานะค่าเช่า / ค่าน้ำ / ค่าไฟ
- 📋 สัญญาเช่า
- 🧻 วัสดุสิ้นเปลือง
- 🔧 งานซ่อมบำรุง
- 🏠 ข้อมูลห้อง / ผู้เช่า

หรือเลือก Quick Command ด้านล่างเลยครับ! 👇`,
      timestamp: new Date('2026-07-05T18:00:00'),
      model: 'vertex-gemini-flash',
    },
  ]);
  const [input, setInput] = useState('');
  const [selectedModel, setSelectedModel] = useState('vertex-gemini-flash');
  const [showModelSelector, setShowModelSelector] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // โหลด conversationId จาก localStorage และซิงก์โมเดลเริ่มต้นไปยัง Backend
  useEffect(() => {
    const savedId = localStorage.getItem('roomgenius_conversation_id');
    if (savedId) {
      setConversationId(savedId);
    }
    
    // ตั้งค่าโมเดลเริ่มต้นบน backend ทันทีที่โหลดหน้าเว็บ
    handleModelChange('vertex-gemini-flash');
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const currentModel = AI_MODELS.find((m) => m.id === selectedModel) || AI_MODELS[0];

  // จัดการการเปลี่ยนโมเดลและแจ้ง Python Engine
  const handleModelChange = async (modelId: string) => {
    setSelectedModel(modelId);
    setShowModelSelector(false);
    
    const model = AI_MODELS.find(m => m.id === modelId);
    if (!model) return;

    try {
      await fetch('/api/ai/models', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          provider: model.provider.toLowerCase(),
          modelName: model.id
        })
      });
    } catch (err) {
      console.error('Failed to notify model change to backend:', err);
    }
  };

  const handleSend = async (text?: string) => {
    const message = text || input.trim();
    if (!message) return;

    const userMsg: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: message,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setIsTyping(true);

    try {
      // เรียกใช้งาน API จริง
      const response = await fetch('/api/ai/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message,
          conversationId: conversationId
        }),
      });

      if (!response.ok) {
        throw new Error('API request failed');
      }

      const data = await response.json();
      
      if (data.status === 'success') {
        const aiMsg: Message = {
          id: Date.now().toString(),
          role: 'ai',
          content: data.response,
          timestamp: new Date(),
          model: selectedModel,
        };

        if (data.conversation_id) {
          setConversationId(data.conversation_id);
          localStorage.setItem('roomgenius_conversation_id', data.conversation_id);
        }

        setIsTyping(false);
        setMessages((prev) => [...prev, aiMsg]);
        return;
      }
      
      throw new Error(data.message || 'API returned failure status');
    } catch (err) {
      console.warn('API error, falling back to demo responses:', err);
      
      // Fallback ไปใช้ Demo Mock Responses เมื่อเชื่อมต่อ API จริงไม่ได้
      await new Promise((resolve) => setTimeout(resolve, 1200));

      const matchKey = Object.keys(DEMO_RESPONSES).find((key) =>
        message.includes(key)
      );
      const responseText = matchKey
        ? DEMO_RESPONSES[matchKey]
        : DEMO_RESPONSES.default;

      const aiMsg: Message = {
        id: Date.now().toString(),
        role: 'ai',
        content: responseText,
        timestamp: new Date(),
        model: selectedModel,
      };

      setIsTyping(false);
      setMessages((prev) => [...prev, aiMsg]);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <>
      <div className="page-header">
        <div>
          <h1 className="page-title">🤖 AI Assistant</h1>
          <p className="page-subtitle">สนทนากับ AI เพื่อวิเคราะห์และจัดการห้องเช่าของคุณ</p>
        </div>
      </div>

      <div className="ai-chat">
        {/* Chat Header */}
        <div className="ai-chat__header">
          <div className="flex items-center gap-3">
            <div
              style={{
                width: '32px',
                height: '32px',
                borderRadius: 'var(--radius-full)',
                background: 'var(--gradient-accent)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: 'var(--text-sm)',
              }}
            >
              🏠
            </div>
            <div>
              <div style={{ fontWeight: 'var(--font-semibold)', fontSize: 'var(--text-sm)' }}>
                RoomGenius AI
              </div>
              <div style={{ fontSize: 'var(--text-xs)', color: 'var(--text-tertiary)' }}>
                {isTyping ? 'กำลังพิมพ์...' : 'ออนไลน์'}
              </div>
            </div>
          </div>

          {/* Model Selector */}
          <div style={{ position: 'relative' }}>
            <button
              className="ai-chat__model-selector"
              onClick={() => setShowModelSelector(!showModelSelector)}
              id="model-selector"
            >
              <span>{currentModel.icon}</span>
              <span>{currentModel.name}</span>
              <span style={{ fontSize: '10px' }}>▼</span>
            </button>

            {showModelSelector && (
              <div
                style={{
                  position: 'absolute',
                  top: '100%',
                  right: 0,
                  marginTop: 'var(--space-2)',
                  background: 'var(--bg-secondary)',
                  border: '1px solid var(--border-secondary)',
                  borderRadius: 'var(--radius-xl)',
                  padding: 'var(--space-2)',
                  width: '260px',
                  zIndex: 'var(--z-dropdown)',
                  animation: 'slideDown 0.2s ease-out',
                  boxShadow: 'var(--shadow-xl)',
                }}
              >
                {AI_MODELS.map((model) => (
                  <button
                    key={model.id}
                    onClick={() => {
                      handleModelChange(model.id);
                    }}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: 'var(--space-3)',
                      width: '100%',
                      padding: 'var(--space-3) var(--space-4)',
                      background: model.id === selectedModel ? 'rgba(99, 102, 241, 0.1)' : 'transparent',
                      border: model.id === selectedModel ? '1px solid rgba(99, 102, 241, 0.3)' : '1px solid transparent',
                      borderRadius: 'var(--radius-lg)',
                      color: 'var(--text-primary)',
                      cursor: 'pointer',
                      transition: 'all 0.15s',
                      textAlign: 'left',
                      fontSize: 'var(--text-sm)',
                    }}
                    onMouseEnter={(e) => {
                      if (model.id !== selectedModel) {
                        e.currentTarget.style.background = 'var(--bg-glass-hover)';
                      }
                    }}
                    onMouseLeave={(e) => {
                      if (model.id !== selectedModel) {
                        e.currentTarget.style.background = 'transparent';
                      }
                    }}
                  >
                    <span style={{ fontSize: 'var(--text-lg)' }}>{model.icon}</span>
                    <div>
                      <div style={{ fontWeight: 'var(--font-semibold)' }}>{model.name}</div>
                      <div style={{ fontSize: 'var(--text-xs)', color: 'var(--text-tertiary)' }}>
                        {model.provider}
                      </div>
                    </div>
                    {model.id === selectedModel && (
                      <span style={{ marginLeft: 'auto', color: 'var(--color-primary-400)' }}>✓</span>
                    )}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Messages */}
        <div className="ai-chat__messages">
          {messages.map((msg) => (
            <div key={msg.id} className={`ai-chat__message ai-chat__message--${msg.role}`}>
              <div className={`ai-chat__message-avatar ai-chat__message-avatar--${msg.role}`}>
                {msg.role === 'ai' ? '🤖' : '👤'}
              </div>
              <div>
                <div className="ai-chat__message-bubble">
                  <div
                    style={{ whiteSpace: 'pre-wrap' }}
                    dangerouslySetInnerHTML={{
                      __html: msg.content
                        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                        .replace(/\n/g, '<br/>')
                    }}
                  />
                </div>
                <div
                  suppressHydrationWarning
                  style={{
                    fontSize: 'var(--text-xs)',
                    color: 'var(--text-tertiary)',
                    marginTop: 'var(--space-1)',
                    padding: '0 var(--space-2)',
                  }}
                >
                  {msg.timestamp.toLocaleTimeString('th-TH', { hour: '2-digit', minute: '2-digit' })}
                  {msg.model && ` • ${AI_MODELS.find(m => m.id === msg.model)?.name || msg.model}`}
                </div>
              </div>
            </div>
          ))}

          {/* Typing Indicator */}
          {isTyping && (
            <div className="ai-chat__message ai-chat__message--ai">
              <div className="ai-chat__message-avatar ai-chat__message-avatar--ai">🤖</div>
              <div className="ai-chat__message-bubble">
                <div className="ai-chat__typing">
                  <div className="ai-chat__typing-dot"></div>
                  <div className="ai-chat__typing-dot"></div>
                  <div className="ai-chat__typing-dot"></div>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Quick Commands */}
        {messages.length <= 1 && (
          <div
            style={{
              padding: '0 var(--space-6) var(--space-4)',
              display: 'flex',
              flexWrap: 'wrap',
              gap: 'var(--space-2)',
            }}
          >
            {QUICK_COMMANDS.map((cmd) => (
              <button
                key={cmd}
                className="btn btn-secondary btn-sm"
                onClick={() => handleSend(cmd)}
                style={{ fontSize: 'var(--text-xs)' }}
              >
                {cmd}
              </button>
            ))}
          </div>
        )}

        {/* Input Area */}
        <div className="ai-chat__input-area">
          <div className="ai-chat__input-wrapper">
            <textarea
              ref={inputRef}
              className="ai-chat__input"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={`ถาม ${currentModel.name} เกี่ยวกับห้องเช่าของคุณ...`}
              rows={1}
              id="ai-chat-input"
            />
            <button
              className="ai-chat__send-btn"
              onClick={() => handleSend()}
              disabled={!input.trim() || isTyping}
              aria-label="ส่งข้อความ"
              id="ai-chat-send"
              style={{ opacity: !input.trim() || isTyping ? 0.5 : 1 }}
            >
              ➤
            </button>
          </div>
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginTop: 'var(--space-2)',
              fontSize: 'var(--text-xs)',
              color: 'var(--text-tertiary)',
            }}
          >
            <span>
              Model: {currentModel.icon} {currentModel.name} ({currentModel.provider})
            </span>
            <span>Shift+Enter เพื่อขึ้นบรรทัดใหม่</span>
          </div>
        </div>
      </div>
    </>
  );
}
