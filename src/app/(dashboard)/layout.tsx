'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

const navItems = [
  {
    section: 'หลัก',
    items: [
      { href: '/dashboard', icon: '📊', label: 'แดชบอร์ด' },
      { href: '/properties', icon: '🏠', label: 'อสังหาริมทรัพย์' },
      { href: '/rooms', icon: '🚪', label: 'จัดการห้อง' },
    ],
  },
  {
    section: 'การเงิน',
    items: [
      { href: '/leases', icon: '📋', label: 'สัญญาเช่า' },
      { href: '/payments', icon: '💰', label: 'การชำระเงิน' },
      { href: '/utilities', icon: '⚡', label: 'ค่าน้ำ / ค่าไฟ' },
    ],
  },
  {
    section: 'ดูแลอาคาร',
    items: [
      { href: '/maintenance', icon: '🔧', label: 'แจ้งซ่อม' },
      { href: '/supplies', icon: '🧻', label: 'วัสดุสิ้นเปลือง' },
    ],
  },
  {
    section: 'AI',
    items: [
      { href: '/ai-assistant', icon: '🤖', label: 'AI Assistant' },
    ],
  },
  {
    section: 'ตั้งค่า',
    items: [
      { href: '/settings', icon: '⚙️', label: 'ตั้งค่า' },
    ],
  },
];

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [notificationsOpen, setNotificationsOpen] = useState(false);

  return (
    <div className="dashboard-layout">
      {/* Sidebar */}
      <aside className={`sidebar ${!sidebarOpen ? 'sidebar--collapsed' : ''}`}>
        <div className="sidebar__logo">
          <div className="sidebar__logo-icon">🏠</div>
          {sidebarOpen && <span className="sidebar__logo-text">RoomGenius AI</span>}
        </div>
        <nav className="sidebar__nav">
          {navItems.map((section) => (
            <React.Fragment key={section.section}>
              {sidebarOpen && (
                <div className="sidebar__section-title">{section.section}</div>
              )}
              {section.items.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`sidebar__nav-item ${
                    pathname === item.href ? 'sidebar__nav-item--active' : ''
                  }`}
                  title={item.label}
                >
                  <span className="sidebar__nav-icon">{item.icon}</span>
                  {sidebarOpen && (
                    <span className="sidebar__nav-label">{item.label}</span>
                  )}
                </Link>
              ))}
            </React.Fragment>
          ))}
        </nav>

        {/* Sidebar Toggle */}
        <div style={{ padding: 'var(--space-4)', borderTop: '1px solid var(--border-primary)' }}>
          <button
            className="btn btn-ghost w-full"
            onClick={() => setSidebarOpen(!sidebarOpen)}
            aria-label={sidebarOpen ? 'ย่อแถบข้าง' : 'ขยายแถบข้าง'}
          >
            {sidebarOpen ? '◀ ย่อ' : '▶'}
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <div className={`dashboard-content ${!sidebarOpen ? 'dashboard-content--expanded' : ''}`}>
        {/* Top Bar */}
        <header className="topbar">
          <div className="topbar__left">
            <button
              className="btn btn-icon btn-ghost"
              style={{ display: 'none' }}
              onClick={() => setSidebarOpen(!sidebarOpen)}
              aria-label="เปิด/ปิดเมนู"
            >
              ☰
            </button>
            <div className="topbar__search">
              <input
                type="search"
                className="topbar__search-input"
                placeholder="ค้นหาห้อง ผู้เช่า สัญญา..."
                id="global-search"
              />
            </div>
          </div>
          <div className="topbar__right">
            {/* AI Model Indicator */}
            <div className="badge badge-primary" style={{ cursor: 'pointer' }}>
              <span>🧠</span>
              <span>Gemini Flash</span>
            </div>

            {/* Notifications */}
            <button
              className="topbar__notification-btn"
              onClick={() => setNotificationsOpen(!notificationsOpen)}
              aria-label="การแจ้งเตือน"
              id="notification-toggle"
            >
              🔔
              <span className="topbar__notification-badge">3</span>
            </button>

            {/* User Avatar */}
            <div
              style={{
                width: '36px',
                height: '36px',
                borderRadius: 'var(--radius-full)',
                background: 'var(--gradient-accent)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: 'var(--text-sm)',
                fontWeight: 'bold',
                color: 'white',
                cursor: 'pointer',
              }}
            >
              U
            </div>
          </div>
        </header>

        {/* Notification Panel */}
        <div className={`notification-panel ${notificationsOpen ? 'notification-panel--open' : ''}`}>
          <div style={{ padding: 'var(--space-6)', borderBottom: '1px solid var(--border-primary)' }}>
            <div className="flex items-center justify-between">
              <h3 style={{ fontSize: 'var(--text-lg)', fontWeight: 'var(--font-bold)' }}>
                การแจ้งเตือน
              </h3>
              <button
                className="btn btn-ghost btn-sm"
                onClick={() => setNotificationsOpen(false)}
              >
                ✕
              </button>
            </div>
          </div>

          {/* Sample Notifications */}
          <div className="notification-item notification-item--unread">
            <div className="notification-item__icon" style={{ background: 'rgba(239, 68, 68, 0.15)' }}>
              💰
            </div>
            <div className="notification-item__content">
              <div className="notification-item__title">ค่าเช่าเกินกำหนด</div>
              <div className="notification-item__message">
                ห้อง 203 ค่าเช่าเดือน ก.ค. ยังไม่ได้ชำระ (เกินกำหนด 3 วัน)
              </div>
              <div className="notification-item__time">5 นาทีที่แล้ว</div>
            </div>
          </div>
          <div className="notification-item notification-item--unread">
            <div className="notification-item__icon" style={{ background: 'rgba(249, 115, 22, 0.15)' }}>
              🧻
            </div>
            <div className="notification-item__content">
              <div className="notification-item__title">วัสดุใกล้หมด</div>
              <div className="notification-item__message">
                ทิชชู่ เหลือ 2 ม้วน (ต่ำกว่าขั้นต่ำ 5 ม้วน)
              </div>
              <div className="notification-item__time">1 ชั่วโมงที่แล้ว</div>
            </div>
          </div>
          <div className="notification-item">
            <div className="notification-item__icon" style={{ background: 'rgba(34, 197, 94, 0.15)' }}>
              ✅
            </div>
            <div className="notification-item__content">
              <div className="notification-item__title">ชำระเงินแล้ว</div>
              <div className="notification-item__message">
                ห้อง 101 ชำระค่าเช่าเดือน ก.ค. จำนวน ฿5,500
              </div>
              <div className="notification-item__time">3 ชั่วโมงที่แล้ว</div>
            </div>
          </div>
        </div>

        {/* Page Content */}
        <main className="page-content">
          {children}
        </main>
      </div>
    </div>
  );
}
