'use client';

import React from 'react';
import Link from 'next/link';

const features = [
  {
    icon: '🧠',
    title: 'Multi-Model AI Brain',
    description: 'สลับสมอง AI ได้หลากหลายค่าย ทั้ง Gemini, ChatGPT, Claude หรือ Codex เลือกตัวที่ดีที่สุดสำหรับทุกงานวิเคราะห์',
  },
  {
    icon: '🔔',
    title: 'แจ้งเตือนค้างชำระอัตโนมัติ',
    description: 'AI ติดตามยอดหนี้และส่งข้อความแจ้งเตือนค่าเช่าที่เป็นมิตรแต่มีประสิทธิภาพทาง LINE และอีเมล ป้องกันการลืมชำระ',
  },
  {
    icon: '⚡',
    title: 'ตรวจจับค่าน้ำไฟผิดปกติ',
    description: 'จดมิเตอร์ปุ๊บ AI คำนวณและวิเคราะห์เทียบย้อนหลังทันที หากมีการใช้น้ำไฟกระโดดผิดปกติจะแจ้งเตือนผู้จัดการเผื่อท่อรั่วแอร์เสีย',
  },
  {
    icon: '📋',
    title: 'จัดการสัญญาเช่าอัจฉริยะ',
    description: 'สร้างสัญญาเช่า สรุปประเด็น และแจ้งเตือนสัญญาเช่าใกล้หมดอายุล่วงหน้า 30-90 วันโดยอัตโนมัติ',
  },
  {
    icon: '🧻',
    title: 'ตัดสต็อกและสั่งซื้อของใช้สิ้นเปลือง',
    description: 'ติดตามกระดาษทิชชู่ สบู่ ของใช้ในห้องพัก แม่บ้านกดเบิกสต็อกลดลง AI ทำเอกสารเสนอสั่งซื้อส่งให้คุณอนุมัติทันที',
  },
  {
    icon: '🔧',
    title: 'ระบบแจ้งซ่อมบำรุงเชิงรุก',
    description: 'ผู้เช่าแจ้งซ่อมผ่านระบบ AI ประเมินระดับความสำคัญ เสนอช่างผู้เชี่ยวชาญ และติดตามงานซ่อมจนเสร็จสิ้น',
  },
];

const pricingPlans = [
  {
    name: 'Starter',
    price: '฿499',
    period: '/ เดือน',
    trial: 'ทดลองใช้ฟรี 14 วัน',
    description: 'เหมาะสำหรับเจ้าของหอพักเริ่มต้น',
    features: [
      'รองรับ 1 โครงการ (สูงสุด 15 ห้อง)',
      'โมเดล AI มาตรฐาน (Gemini Flash)',
      'ระบบคำนวณค่าน้ำ/ค่าไฟ',
      'แจ้งเตือนยอดชำระเบื้องต้น',
    ],
    buttonText: 'เริ่มทดลองใช้ฟรี',
    featured: false,
  },
  {
    name: 'Professional',
    price: '฿1,499',
    period: '/ เดือน',
    trial: 'ทดลองใช้ฟรี 14 วัน',
    description: 'แพ็กเกจยอดนิยมสำหรับผู้ประกอบการหอพักและคอนโด',
    features: [
      'รองรับสูงสุด 5 โครงการ (ไม่จำกัดห้อง)',
      'เลือกสลับสมอง AI ได้ทุกค่าย (Gemini, Claude, GPT)',
      'แจ้งเตือนทาง LINE / Email แบบอัตโนมัติ',
      'ระบบวิเคราะห์ค่าน้ำไฟผิดปกติเชิงลึก',
      'ระบบจัดการของใช้สิ้นเปลือง (สต็อกทิชชู่, ของในห้อง)',
    ],
    buttonText: 'เริ่มทดลองใช้ฟรี',
    featured: true,
  },
  {
    name: 'Business',
    price: '฿3,999',
    period: '/ เดือน',
    trial: 'ทดลองใช้ฟรี 14 วัน',
    description: 'สำหรับธุรกิจห้องเช่าระดับใหญ่และโฮสเทลหลายสาขา',
    features: [
      'ไม่จำกัดโครงการและห้องพัก',
      'ฟีเจอร์ AI ครบทุกฟังก์ชัน + มอบหมาย Subagents ทำงานเบื้องหลัง',
      'ระบบร่างใบสั่งซื้อของใช้อัตโนมัติ (Auto-Reorder)',
      'การสกัดข้อมูลและสรุปข้อมูลสัญญากฎหมาย',
      'แดชบอร์ดการเงินเปรียบเทียบ ROI หลายสาขา',
    ],
    buttonText: 'เริ่มทดลองใช้ฟรี',
    featured: false,
  },
];

export default function LandingPage() {
  return (
    <div style={{ background: 'var(--bg-primary)', minHeight: '100vh', color: 'var(--text-primary)' }}>
      {/* Header / Nav */}
      <header
        style={{
          position: 'sticky',
          top: 0,
          background: 'rgba(15, 15, 35, 0.8)',
          backdropFilter: 'blur(20px)',
          borderBottom: '1px solid var(--border-primary)',
          padding: 'var(--space-4) var(--space-8)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          zIndex: 100,
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
          <span style={{ fontSize: 'var(--text-2xl)' }}>🏠</span>
          <span
            style={{
              fontWeight: 'var(--font-bold)',
              fontSize: 'var(--text-lg)',
              background: 'var(--gradient-accent)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}
          >
            RoomGenius AI
          </span>
        </div>
        <div style={{ display: 'flex', gap: 'var(--space-4)', alignItems: 'center' }}>
          <a href="#features" style={{ fontSize: 'var(--text-sm)', color: 'var(--text-secondary)' }}>
            ฟีเจอร์
          </a>
          <a href="#pricing" style={{ fontSize: 'var(--text-sm)', color: 'var(--text-secondary)' }}>
            ราคา
          </a>
          <Link href="/dashboard" className="btn btn-secondary btn-sm">
            เข้าสู่ระบบ
          </Link>
          <Link href="/dashboard" className="btn btn-primary btn-sm">
            ทดลองใช้ฟรี
          </Link>
        </div>
      </header>

      {/* Hero Section */}
      <section
        style={{
          padding: 'var(--space-24) var(--space-8) var(--space-16)',
          textAlign: 'center',
          background: 'var(--gradient-hero)',
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        <div
          style={{
            position: 'absolute',
            top: '20%',
            left: '50%',
            transform: 'translateX(-50%)',
            width: '600px',
            height: '600px',
            background: 'var(--gradient-accent)',
            filter: 'blur(150px)',
            opacity: 0.15,
            zIndex: 0,
            borderRadius: '50%',
          }}
        ></div>

        <div style={{ position: 'relative', zIndex: 1, maxWidth: '800px', margin: '0 auto' }}>
          <span
            className="badge badge-primary"
            style={{ marginBottom: 'var(--space-4)', padding: 'var(--space-2) var(--space-4)' }}
          >
            ✨ ระบบจัดการห้องเช่า Agentic AI รุ่นแรกของโลก
          </span>
          <h1
            style={{
              fontSize: '3.5rem',
              fontWeight: 900,
              lineHeight: 1.1,
              marginBottom: 'var(--space-6)',
              background: 'linear-gradient(135deg, #ffffff 0%, #a5b4fc 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}
          >
            ปฏิวัติการดูแลหอพักและคอนโด ด้วย AI อัจฉริยะหลายค่าย
          </h1>
          <p
            style={{
              fontSize: 'var(--text-lg)',
              color: 'var(--text-secondary)',
              marginBottom: 'var(--space-10)',
              lineHeight: 1.6,
            }}
          >
            ให้ AI ทำหน้าที่เป็นผู้ดูแลโครงการแทนคุณ สลับสมองได้ทั้ง Gemini, Claude และ ChatGPT
            พร้อมช่วยทวงค่าเช่าอัตโนมัติ แจ้งเตือนน้ำไฟรั่ว และจัดการของใช้สิ้นเปลืองแบบไร้รอยต่อ
          </p>
          <div className="flex justify-center gap-4">
            <Link href="/dashboard" className="btn btn-primary btn-lg">
              เริ่มต้นทดลองใช้ฟรี 14 วัน
            </Link>
            <a href="#features" className="btn btn-secondary btn-lg">
              ดูฟีเจอร์ทั้งหมด
            </a>
          </div>
          <div style={{ marginTop: 'var(--space-4)', fontSize: 'var(--text-xs)', color: 'var(--text-tertiary)' }}>
            * ไม่ต้องใช้บัตรเครดิตในการเริ่มต้นทดลองใช้งาน
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section id="features" style={{ padding: 'var(--space-20) var(--space-8)', maxWidth: '1200px', margin: '0 auto' }}>
        <div style={{ textAlign: 'center', marginBottom: 'var(--space-16)' }}>
          <h2 style={{ fontSize: 'var(--text-3xl)', marginBottom: 'var(--space-4)' }}>
            ยกระดับธุรกิจหอพักสู่ยุค AI เจนเนอเรชันใหม่
          </h2>
          <p style={{ color: 'var(--text-secondary)', maxWidth: '600px', margin: '0 auto' }}>
            ฟีเจอร์ที่ออกแบบมาเพื่อลดเวลาจัดการงานแอดมินลงถึง 80% ให้คุณโฟกัสการขยายธุรกิจได้เต็มที่
          </p>
        </div>

        <div className="grid grid-cols-3" style={{ gap: 'var(--space-8)' }}>
          {features.map((f, i) => (
            <div key={i} className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
              <div
                style={{
                  width: '50px',
                  height: '50px',
                  borderRadius: 'var(--radius-lg)',
                  background: 'rgba(99, 102, 241, 0.1)',
                  color: 'var(--color-primary-400)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: 'var(--text-2xl)',
                }}
              >
                {f.icon}
              </div>
              <h3 style={{ fontSize: 'var(--text-lg)', fontWeight: 'var(--font-bold)' }}>{f.title}</h3>
              <p style={{ fontSize: 'var(--text-sm)', lineHeight: 1.6 }}>{f.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Pricing Section */}
      <section
        id="pricing"
        style={{
          padding: 'var(--space-20) var(--space-8)',
          background: 'rgba(255, 255, 255, 0.02)',
          borderTop: '1px solid var(--border-primary)',
        }}
      >
        <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: 'var(--space-16)' }}>
            <h2 style={{ fontSize: 'var(--text-3xl)', marginBottom: 'var(--space-4)' }}>
              แพ็กเกจราคาสำหรับทุกระดับผู้ประกอบการ
            </h2>
            <p style={{ color: 'var(--text-secondary)' }}>
              สมัครทดลองใช้งานฟรี 14 วันก่อนตัดสินใจ ยกเลิกเมื่อไหร่ก็ได้
            </p>
          </div>

          <div className="grid grid-cols-3" style={{ gap: 'var(--space-8)', alignItems: 'stretch' }}>
            {pricingPlans.map((plan, i) => (
              <div
                key={i}
                className={`pricing-card ${plan.featured ? 'pricing-card--featured' : ''}`}
                style={{ display: 'flex', flexDirection: 'column', height: '100%' }}
              >
                {plan.featured && (
                  <span className="badge badge-accent pricing-card__badge">RECOMMENDED</span>
                )}
                <div style={{ marginBottom: 'var(--space-6)' }}>
                  <h3 className="pricing-card__name">{plan.name}</h3>
                  <div style={{ margin: 'var(--space-4) 0' }}>
                    <span className="pricing-card__price">{plan.price}</span>
                    <span className="pricing-card__period">{plan.period}</span>
                  </div>
                  <span className="badge badge-success">{plan.trial}</span>
                  <p style={{ fontSize: 'var(--text-xs)', color: 'var(--text-tertiary)', marginTop: 'var(--space-3)' }}>
                    {plan.description}
                  </p>
                </div>

                <ul className="pricing-card__features" style={{ flex: 1 }}>
                  {plan.features.map((f, j) => (
                    <li key={j} className="pricing-card__feature">
                      {f}
                    </li>
                  ))}
                </ul>

                <Link
                  href="/dashboard"
                  className={`btn w-full ${plan.featured ? 'btn-primary' : 'btn-secondary'}`}
                  style={{ marginTop: 'var(--space-6)' }}
                >
                  {plan.buttonText}
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer
        style={{
          borderTop: '1px solid var(--border-primary)',
          padding: 'var(--space-10) var(--space-8)',
          textAlign: 'center',
          fontSize: 'var(--text-xs)',
          color: 'var(--text-tertiary)',
        }}
      >
        <p>© 2026 RoomGenius AI. All rights reserved. พัฒนาและออกแบบเพื่อยกระดับผู้ประกอบการหอพักไทย</p>
      </footer>
    </div>
  );
}
