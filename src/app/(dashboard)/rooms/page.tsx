import React from 'react';
import { prisma } from '@/lib/db';

export const revalidate = 0;

export default async function RoomsPage() {
  const rooms = await prisma.room.findMany({
    include: { property: true },
    orderBy: { number: 'asc' },
  });

  const getStatusBadgeClass = (status: string) => {
    switch (status) {
      case 'OCCUPIED':
        return 'badge-success';
      case 'VACANT':
        return 'badge-primary';
      case 'MAINTENANCE':
        return 'badge-danger';
      default:
        return 'badge-secondary';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'OCCUPIED':
        return 'มีผู้เช่า';
      case 'VACANT':
        return 'ว่าง';
      case 'MAINTENANCE':
        return 'กำลังซ่อม';
      default:
        return status;
    }
  };

  return (
    <div className="space-y-6">
      <div className="page-header">
        <div>
          <h1 className="page-title">🚪 จัดการห้องพัก</h1>
          <p className="page-subtitle">ตรวจสอบสถานะการเช่าและรายละเอียดห้องทั้งหมด</p>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))', gap: 'var(--space-6)' }}>
        {rooms.map((room) => (
          <div key={room.id} className="card" style={{ borderTop: `4px solid ${room.status === 'OCCUPIED' ? 'var(--color-success-500)' : room.status === 'MAINTENANCE' ? 'var(--color-danger-500)' : 'var(--color-primary-500)'}` }}>
            <div className="flex items-center justify-between mb-4">
              <span style={{ fontSize: 'var(--text-xl)', fontWeight: 'var(--font-bold)' }}>ห้อง {room.number}</span>
              <span className={`badge ${getStatusBadgeClass(room.status)}`}>{getStatusLabel(room.status)}</span>
            </div>

            <div className="space-y-2 mb-4" style={{ fontSize: 'var(--text-xs)', color: 'var(--text-secondary)' }}>
              <div className="flex justify-between">
                <span>อาคาร:</span>
                <span style={{ color: 'var(--text-primary)', fontWeight: '500' }}>{room.property.name}</span>
              </div>
              <div className="flex justify-between">
                <span>ชั้นที่:</span>
                <span style={{ color: 'var(--text-primary)', fontWeight: '500' }}>ชั้น {room.floor}</span>
              </div>
              <div className="flex justify-between">
                <span>ประเภทห้อง:</span>
                <span style={{ color: 'var(--text-primary)', fontWeight: '500' }}>{room.type}</span>
              </div>
              <div className="flex justify-between">
                <span>ค่าเช่ารายเดือน:</span>
                <span style={{ color: 'var(--text-primary)', fontWeight: 'bold' }}>
                  ฿{room.monthlyRate ? room.monthlyRate.toLocaleString() : 'N/A'}
                </span>
              </div>
            </div>

            <div style={{ marginTop: 'var(--space-4)', display: 'flex', gap: 'var(--space-2)' }}>
              <button className="btn btn-secondary btn-sm w-full">ดูประวัติเช่า</button>
              <button className="btn btn-ghost btn-sm">⚙️</button>
            </div>
          </div>
        ))}

        {rooms.length === 0 && (
          <div className="card text-center" style={{ gridColumn: '1 / -1', padding: 'var(--space-12)' }}>
            <span style={{ fontSize: '48px' }}>🚪</span>
            <h3 style={{ marginTop: 'var(--space-4)', fontSize: 'var(--text-lg)', fontWeight: 'bold' }}>ไม่พบข้อมูลห้องพัก</h3>
            <p style={{ color: 'var(--text-secondary)' }}>กรุณาสร้างอสังหาริมทรัพย์เพื่อเริ่มเพิ่มห้องเช่า</p>
          </div>
        )}
      </div>
    </div>
  );
}
