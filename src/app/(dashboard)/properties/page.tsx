import React from 'react';
import { prisma } from '@/lib/db';

export const revalidate = 0; // Disable caching to always show fresh data

export default async function PropertiesPage() {
  const properties = await prisma.property.findMany({
    orderBy: { createdAt: 'desc' },
  });

  return (
    <div className="space-y-6">
      <div className="page-header">
        <div>
          <h1 className="page-title">🏠 อสังหาริมทรัพย์</h1>
          <p className="page-subtitle">จัดการโครงการ อาคาร และข้อมูลสาธารณูปโภคหลัก</p>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: 'var(--space-6)' }}>
        {properties.map((prop) => (
          <div key={prop.id} className="card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
            <div>
              <div className="flex items-center justify-between mb-4">
                <h3 style={{ fontSize: 'var(--text-lg)', fontWeight: 'var(--font-bold)', color: 'var(--color-primary-400)' }}>
                  {prop.name}
                </h3>
                <span className="badge badge-primary">{prop.type}</span>
              </div>
              
              <p style={{ color: 'var(--text-secondary)', fontSize: 'var(--text-sm)', marginBottom: 'var(--space-4)' }}>
                📍 {prop.address} {prop.district} {prop.subDistrict} {prop.province}
              </p>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-4)', margin: 'var(--space-4) 0', padding: 'var(--space-4) 0', borderTop: '1px solid var(--border-primary)', borderBottom: '1px solid var(--border-primary)' }}>
                <div>
                  <div style={{ fontSize: 'var(--text-xs)', color: 'var(--text-tertiary)' }}>ห้องทั้งหมด</div>
                  <div style={{ fontSize: 'var(--text-lg)', fontWeight: 'var(--font-bold)' }}>{prop.totalRooms} ห้อง</div>
                </div>
                <div>
                  <div style={{ fontSize: 'var(--text-xs)', color: 'var(--text-tertiary)' }}>จำนวนชั้น</div>
                  <div style={{ fontSize: 'var(--text-lg)', fontWeight: 'var(--font-bold)' }}>{prop.totalFloors} ชั้น</div>
                </div>
              </div>

              <div className="space-y-2" style={{ fontSize: 'var(--text-xs)', color: 'var(--text-secondary)' }}>
                <div className="flex justify-between">
                  <span>ค่าน้ำประปา:</span>
                  <span style={{ fontWeight: 'bold' }}>{prop.waterRate} บาท / หน่วย</span>
                </div>
                <div className="flex justify-between">
                  <span>ค่าไฟฟ้า:</span>
                  <span style={{ fontWeight: 'bold' }}>{prop.electricRate} บาท / หน่วย</span>
                </div>
                <div className="flex justify-between">
                  <span>ค่าส่วนกลาง:</span>
                  <span style={{ fontWeight: 'bold' }}>฿{prop.commonAreaFee.toLocaleString()} / เดือน</span>
                </div>
              </div>
            </div>

            <div style={{ marginTop: 'var(--space-6)' }}>
              <button className="btn btn-secondary w-full">ดูข้อมูลห้องพักทั้งหมด ➔</button>
            </div>
          </div>
        ))}

        {properties.length === 0 && (
          <div className="card text-center" style={{ gridColumn: '1 / -1', padding: 'var(--space-12)' }}>
            <span style={{ fontSize: '48px' }}>🏠</span>
            <h3 style={{ marginTop: 'var(--space-4)', fontSize: 'var(--text-lg)', fontWeight: 'bold' }}>ไม่พบข้อมูลอสังหาริมทรัพย์</h3>
            <p style={{ color: 'var(--text-secondary)' }}>เริ่มสร้างโครงการแรกของคุณเพื่อจัดการห้องเช่า</p>
          </div>
        )}
      </div>
    </div>
  );
}
