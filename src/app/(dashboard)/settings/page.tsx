'use client';

import React, { useState, useEffect } from 'react';

export default function SettingsPage() {
  const [modelName, setModelName] = useState('vertex-gemini-flash');
  const [saveStatus, setSaveStatus] = useState('');

  useEffect(() => {
    // ดึงค่าโมเดลปัจจุบันจาก Python Engine ผ่าน api/ai/models
    const fetchCurrentModel = async () => {
      try {
        const res = await fetch('/api/ai/models');
        if (res.ok) {
          const data = await res.json();
          if (data.model_name) {
            setModelName(data.model_name);
          }
        }
      } catch (err) {
        console.error('Failed to load current model:', err);
      }
    };
    fetchCurrentModel();
  }, []);

  const handleSaveModel = async (modelId: string) => {
    setModelName(modelId);
    setSaveStatus('กำลังสลับโมเดล...');

    let provider = 'google';
    if (modelId.startsWith('vertex')) {
      provider = 'vertexai';
    } else if (modelId.startsWith('gpt')) {
      provider = 'openai';
    } else if (modelId.startsWith('claude')) {
      provider = 'anthropic';
    }

    try {
      const res = await fetch('/api/ai/models', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          provider,
          modelName: modelId
        })
      });
      if (res.ok) {
        const data = await res.json();
        setSaveStatus(`สลับโมเดลสำเร็จเป็น: ${data.model_name}`);
      } else {
        setSaveStatus('ไม่สามารถบันทึกการสลับโมเดลได้');
      }
    } catch (err) {
      setSaveStatus('เกิดข้อผิดพลาดในการบันทึกข้อมูล');
    }

    setTimeout(() => setSaveStatus(''), 4000);
  };

  return (
    <div className="space-y-6">
      <div className="page-header">
        <div>
          <h1 className="page-title">⚙️ ตั้งค่าระบบ</h1>
          <p className="page-subtitle">จัดการการเชื่อมโยงระบบและตั้งค่าสมองปัญญาประดิษฐ์ RoomGenius AI</p>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.5fr', gap: 'var(--space-6)', alignItems: 'start' }}>
        {/* Left Card: AI Configuration */}
        <div className="card space-y-4">
          <h2 style={{ fontSize: 'var(--text-lg)', fontWeight: 'bold', color: 'var(--color-primary-400)' }}>
            🤖 การตั้งค่า AI Engine
          </h2>
          
          <div className="space-y-2">
            <label style={{ fontSize: 'var(--text-xs)', color: 'var(--text-secondary)' }}>
              โมเดลหลักที่ใช้งาน (Active Brain)
            </label>
            <select
              value={modelName}
              onChange={(e) => handleSaveModel(e.target.value)}
              style={{
                width: '100%',
                padding: 'var(--space-3) var(--space-4)',
                background: 'var(--bg-secondary)',
                border: '1px solid var(--border-secondary)',
                borderRadius: 'var(--radius-lg)',
                color: 'var(--text-primary)',
                outline: 'none',
              }}
            >
              <option value="vertex-gemini-flash">Vertex Gemini Flash (แนะนำสำหรับระบบนี้)</option>
              <option value="vertex-gemini-pro">Vertex Gemini Pro</option>
              <option value="gemini-flash">Gemini Flash (Studio)</option>
              <option value="gemini-pro">Gemini Pro (Studio)</option>
              <option value="gpt-4o">ChatGPT 4o</option>
              <option value="claude-sonnet">Claude Sonnet</option>
            </select>
          </div>

          {saveStatus && (
            <div style={{
              fontSize: 'var(--text-xs)',
              padding: 'var(--space-2) var(--space-4)',
              background: 'rgba(99, 102, 241, 0.1)',
              border: '1px solid rgba(99, 102, 241, 0.3)',
              borderRadius: 'var(--radius-md)',
              color: 'var(--color-primary-300)'
            }}>
              {saveStatus}
            </div>
          )}

          <div style={{ fontSize: 'var(--text-xs)', color: 'var(--text-secondary)' }} className="space-y-2 pt-4">
            <p><strong>สถานะเชื่อมต่อ GCP Vertex AI:</strong></p>
            <p style={{ color: 'var(--color-success-400)' }}>✓ Credentials mounted successfully</p>
            <p>Project: <code>project-beeb3f56-6824-421f-80c</code></p>
            <p>Location: <code>us-central1</code></p>
          </div>
        </div>

        {/* Right Card: General settings */}
        <div className="card space-y-4">
          <h2 style={{ fontSize: 'var(--text-lg)', fontWeight: 'bold' }}>🏠 ข้อมูลหอพัก & ระบบความปลอดภัย</h2>
          
          <div className="space-y-4" style={{ fontSize: 'var(--text-sm)' }}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-4)' }}>
              <div>
                <label style={{ fontSize: 'var(--text-xs)', color: 'var(--text-secondary)' }}>ชื่อแอปพลิเคชัน</label>
                <input type="text" className="topbar__search-input" value="RoomGenius AI" disabled style={{ width: '100%', border: '1px solid var(--border-secondary)', padding: 'var(--space-3)' }} />
              </div>
              <div>
                <label style={{ fontSize: 'var(--text-xs)', color: 'var(--text-secondary)' }}>โซนเวลาเริ่มต้น</label>
                <input type="text" className="topbar__search-input" value="Asia/Bangkok" disabled style={{ width: '100%', border: '1px solid var(--border-secondary)', padding: 'var(--space-3)' }} />
              </div>
            </div>

            <div>
              <label style={{ fontSize: 'var(--text-xs)', color: 'var(--text-secondary)' }}>ที่อยู่การเชื่อมต่อฐานข้อมูล (Database URL)</label>
              <input type="password" value="postgresql://roomgenius:******@localhost:5432/roomgenius_db" disabled style={{ width: '100%', background: 'var(--bg-secondary)', border: '1px solid var(--border-secondary)', borderRadius: 'var(--radius-lg)', color: 'var(--text-secondary)', padding: 'var(--space-3) var(--space-4)', outline: 'none' }} />
            </div>

            <div style={{ borderTop: '1px solid var(--border-primary)', paddingTop: 'var(--space-4)' }}>
              <h3 style={{ fontWeight: 'bold', marginBottom: 'var(--space-2)' }}>แผนการใช้งาน SaaS</h3>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'var(--bg-glass)', border: '1px solid var(--border-secondary)', padding: 'var(--space-4)', borderRadius: 'var(--radius-xl)' }}>
                <div>
                  <div style={{ fontWeight: 'bold', color: 'var(--color-primary-400)' }}>Professional Plan</div>
                  <div style={{ fontSize: 'var(--text-xs)', color: 'var(--text-secondary)' }}>รองรับสูงสุด 10 โครงการ 250 ห้องพัก</div>
                </div>
                <span className="badge badge-success">เปิดใช้งานแล้ว</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
