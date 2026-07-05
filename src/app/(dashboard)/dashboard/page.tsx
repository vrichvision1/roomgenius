'use client';

import React from 'react';
import Link from 'next/link';

// Mock data for demo
const stats = [
  { icon: '🏠', label: 'ห้องทั้งหมด', value: '48', trend: null, color: 'var(--color-primary-400)' },
  { icon: '🟢', label: 'มีผู้เช่า', value: '42', trend: { value: '+2', up: true }, color: 'var(--color-success-400)' },
  { icon: '🔵', label: 'ห้องว่าง', value: '4', trend: { value: '-1', up: false }, color: 'var(--color-info-400)' },
  { icon: '🔧', label: 'ซ่อมบำรุง', value: '2', trend: null, color: 'var(--color-warning-400)' },
];

const financialStats = [
  { icon: '💰', label: 'รายได้เดือนนี้', value: '฿247,500', trend: { value: '+12%', up: true } },
  { icon: '📥', label: 'รอชำระ', value: '฿35,000', trend: { value: '6 ห้อง', up: false } },
  { icon: '⚠️', label: 'เกินกำหนด', value: '฿12,500', trend: { value: '2 ห้อง', up: false } },
  { icon: '📊', label: 'Occupancy', value: '87.5%', trend: { value: '+4.2%', up: true } },
];

const recentPayments = [
  { room: '101', tenant: 'สมชาย มีสุข', amount: '฿5,500', status: 'PAID', date: '5 ก.ค.' },
  { room: '205', tenant: 'วิภา แสงทอง', amount: '฿6,000', status: 'PAID', date: '4 ก.ค.' },
  { room: '302', tenant: 'จิราพร ใจดี', amount: '฿7,500', status: 'PENDING', date: '1 ก.ค.' },
  { room: '203', tenant: 'ธนพล รักเรียน', amount: '฿5,500', status: 'OVERDUE', date: '1 ก.ค.' },
  { room: '108', tenant: 'ปิยะ สวัสดี', amount: '฿5,000', status: 'PENDING', date: '1 ก.ค.' },
];

const aiInsights = [
  { icon: '🔔', text: 'ห้อง 203, 108 ยังไม่ชำระค่าเช่าเดือนนี้ (รวม ฿10,500)', type: 'warning' },
  { icon: '⚡', text: 'ห้อง 305 ค่าไฟเดือนนี้สูงกว่าปกติ 40% — อาจมีเครื่องใช้ไฟฟ้าทำงานผิดปกติ', type: 'danger' },
  { icon: '🧻', text: 'ทิชชู่ ผ้าเช็ดตัว ใกล้หมดสต็อก — ควรสั่งซื้อภายในสัปดาห์นี้', type: 'warning' },
  { icon: '📋', text: 'สัญญาห้อง 401, 405 จะหมดอายุใน 30 วัน — ควรติดต่อต่อสัญญา', type: 'info' },
  { icon: '✅', text: 'Occupancy rate เพิ่มขึ้น 4.2% จากเดือนที่แล้ว — แนวโน้มดี', type: 'success' },
];

const statusBadge: Record<string, string> = {
  PAID: 'badge badge-success badge-dot',
  PENDING: 'badge badge-warning badge-dot',
  OVERDUE: 'badge badge-danger badge-dot',
};

const statusLabel: Record<string, string> = {
  PAID: 'ชำระแล้ว',
  PENDING: 'รอชำระ',
  OVERDUE: 'เกินกำหนด',
};

export default function DashboardPage() {
  return (
    <>
      {/* Page Header */}
      <div className="page-header">
        <div>
          <h1 className="page-title">แดชบอร์ด</h1>
          <p className="page-subtitle">ภาพรวมระบบจัดการห้องเช่าของคุณ</p>
        </div>
        <div className="flex gap-3">
          <Link href="/ai-assistant" className="btn btn-primary">
            🤖 ถาม AI
          </Link>
          <button className="btn btn-secondary">
            📥 ดาวน์โหลดรายงาน
          </button>
        </div>
      </div>

      {/* Room Stats */}
      <div className="grid grid-cols-4" style={{ marginBottom: 'var(--space-6)' }}>
        {stats.map((stat) => (
          <div key={stat.label} className="stats-card">
            <div className="stats-card__icon" style={{ background: `${stat.color}20`, color: stat.color }}>
              {stat.icon}
            </div>
            <div className="stats-card__value">{stat.value}</div>
            <div className="stats-card__label">{stat.label}</div>
            {stat.trend && (
              <span className={`stats-card__trend ${stat.trend.up ? 'stats-card__trend--up' : 'stats-card__trend--down'}`}>
                {stat.trend.up ? '↑' : '↓'} {stat.trend.value}
              </span>
            )}
          </div>
        ))}
      </div>

      {/* Financial Stats */}
      <div className="grid grid-cols-4" style={{ marginBottom: 'var(--space-8)' }}>
        {financialStats.map((stat) => (
          <div key={stat.label} className="stats-card">
            <div className="stats-card__icon">{stat.icon}</div>
            <div className="stats-card__value">{stat.value}</div>
            <div className="stats-card__label">{stat.label}</div>
            {stat.trend && (
              <span className={`stats-card__trend ${stat.trend.up ? 'stats-card__trend--up' : 'stats-card__trend--down'}`}>
                {stat.trend.up ? '↑' : '↓'} {stat.trend.value}
              </span>
            )}
          </div>
        ))}
      </div>

      <div className="grid grid-cols-2" style={{ gap: 'var(--space-6)' }}>
        {/* Recent Payments Table */}
        <div className="glass-card" style={{ padding: 0 }}>
          <div style={{ padding: 'var(--space-6)', borderBottom: '1px solid var(--border-primary)' }}>
            <div className="flex items-center justify-between">
              <h3 style={{ fontSize: 'var(--text-lg)', fontWeight: 'var(--font-bold)' }}>
                💰 การชำระเงินล่าสุด
              </h3>
              <Link href="/payments" className="btn btn-ghost btn-sm">
                ดูทั้งหมด →
              </Link>
            </div>
          </div>
          <div className="table-container" style={{ border: 'none', borderRadius: 0 }}>
            <table className="table">
              <thead>
                <tr>
                  <th>ห้อง</th>
                  <th>ผู้เช่า</th>
                  <th>จำนวน</th>
                  <th>สถานะ</th>
                </tr>
              </thead>
              <tbody>
                {recentPayments.map((p) => (
                  <tr key={p.room}>
                    <td style={{ fontWeight: 'var(--font-semibold)' }}>{p.room}</td>
                    <td>{p.tenant}</td>
                    <td style={{ fontWeight: 'var(--font-semibold)' }}>{p.amount}</td>
                    <td>
                      <span className={statusBadge[p.status]}>
                        {statusLabel[p.status]}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* AI Insights Panel */}
        <div className="glass-card">
          <div className="flex items-center justify-between" style={{ marginBottom: 'var(--space-6)' }}>
            <h3 style={{ fontSize: 'var(--text-lg)', fontWeight: 'var(--font-bold)' }}>
              🤖 AI วิเคราะห์
            </h3>
            <span className="badge badge-primary">
              <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: 'var(--color-success-400)', animation: 'pulse-dot 2s infinite' }}></span>
              Gemini Flash
            </span>
          </div>
          <div className="flex flex-col gap-4">
            {aiInsights.map((insight, idx) => {
              const bgMap: Record<string, string> = {
                warning: 'rgba(249, 115, 22, 0.08)',
                danger: 'rgba(239, 68, 68, 0.08)',
                info: 'rgba(14, 165, 233, 0.08)',
                success: 'rgba(34, 197, 94, 0.08)',
              };
              const borderMap: Record<string, string> = {
                warning: 'rgba(249, 115, 22, 0.2)',
                danger: 'rgba(239, 68, 68, 0.2)',
                info: 'rgba(14, 165, 233, 0.2)',
                success: 'rgba(34, 197, 94, 0.2)',
              };
              return (
                <div
                  key={idx}
                  style={{
                    display: 'flex',
                    alignItems: 'flex-start',
                    gap: 'var(--space-3)',
                    padding: 'var(--space-4)',
                    background: bgMap[insight.type],
                    border: `1px solid ${borderMap[insight.type]}`,
                    borderRadius: 'var(--radius-lg)',
                    fontSize: 'var(--text-sm)',
                    lineHeight: 'var(--leading-relaxed)',
                    animation: `slideUp 0.4s ease-out ${idx * 0.1}s both`,
                  }}
                >
                  <span style={{ fontSize: 'var(--text-lg)', flexShrink: 0 }}>{insight.icon}</span>
                  <span>{insight.text}</span>
                </div>
              );
            })}
          </div>
          <Link
            href="/ai-assistant"
            className="btn btn-primary w-full"
            style={{ marginTop: 'var(--space-6)' }}
          >
            🤖 สนทนากับ AI เพิ่มเติม
          </Link>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="glass-card" style={{ marginTop: 'var(--space-6)' }}>
        <h3 style={{ fontSize: 'var(--text-lg)', fontWeight: 'var(--font-bold)', marginBottom: 'var(--space-4)' }}>
          ⚡ Quick Actions
        </h3>
        <div className="flex gap-3" style={{ flexWrap: 'wrap' }}>
          <Link href="/rooms" className="btn btn-secondary">🚪 เพิ่มห้อง</Link>
          <Link href="/leases" className="btn btn-secondary">📋 สร้างสัญญาเช่า</Link>
          <Link href="/utilities" className="btn btn-secondary">⚡ จดมิเตอร์</Link>
          <Link href="/payments" className="btn btn-secondary">💰 บันทึกชำระเงิน</Link>
          <Link href="/maintenance" className="btn btn-secondary">🔧 แจ้งซ่อม</Link>
          <Link href="/supplies" className="btn btn-secondary">🧻 ตรวจสต็อก</Link>
        </div>
      </div>
    </>
  );
}
