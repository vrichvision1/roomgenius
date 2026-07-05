import React from 'react';
import { prisma } from '@/lib/db';

export const revalidate = 0;

export default async function UtilitiesPage() {
  const readings = await prisma.utilityReading.findMany({
    include: { room: true },
    orderBy: { readingDate: 'desc' },
  });

  const getTypeLabel = (type: string) => {
    switch (type) {
      case 'WATER':
        return '💧 น้ำประปา';
      case 'ELECTRIC':
        return '⚡ ไฟฟ้า';
      default:
        return type;
    }
  };

  const getMonthLabel = (date: Date) => {
    return new Date(date).toLocaleDateString('th-TH', { month: 'long', year: 'numeric' });
  };

  return (
    <div className="space-y-6">
      <div className="page-header">
        <div>
          <h1 className="page-title">⚡ จดมิเตอร์ค่าน้ำ / ค่าไฟ</h1>
          <p className="page-subtitle">บันทึกและตรวจสอบปริมาณและยอดค่าไฟฟ้าค่าน้ำประปารายห้อง</p>
        </div>
      </div>

      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        <div style={{ overflowX: 'auto' }}>
          <table className="table" style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border-primary)', textAlign: 'left' }}>
                <th style={{ padding: 'var(--space-4) var(--space-6)', color: 'var(--text-secondary)' }}>รอบเดือน</th>
                <th style={{ padding: 'var(--space-4) var(--space-6)', color: 'var(--text-secondary)' }}>ห้อง</th>
                <th style={{ padding: 'var(--space-4) var(--space-6)', color: 'var(--text-secondary)' }}>ประเภท</th>
                <th style={{ padding: 'var(--space-4) var(--space-6)', color: 'var(--text-secondary)' }}>เลขมิเตอร์ครั้งก่อน</th>
                <th style={{ padding: 'var(--space-4) var(--space-6)', color: 'var(--text-secondary)' }}>เลขมิเตอร์ครั้งนี้</th>
                <th style={{ padding: 'var(--space-4) var(--space-6)', color: 'var(--text-secondary)' }}>หน่วยที่ใช้</th>
                <th style={{ padding: 'var(--space-4) var(--space-6)', color: 'var(--text-secondary)' }}>ยอดคำนวณเงิน</th>
                <th style={{ padding: 'var(--space-4) var(--space-6)', color: 'var(--text-secondary)' }}>วันที่บันทึก</th>
                <th style={{ padding: 'var(--space-4) var(--space-6)', color: 'var(--text-secondary)' }}></th>
              </tr>
            </thead>
            <tbody>
              {readings.map((reading) => {
                return (
                  <tr key={reading.id} style={{ borderBottom: '1px solid var(--border-secondary)' }}>
                    <td style={{ padding: 'var(--space-4) var(--space-6)', fontWeight: '500' }}>{getMonthLabel(reading.readingDate)}</td>
                    <td style={{ padding: 'var(--space-4) var(--space-6)', fontWeight: 'bold' }}>ห้อง {reading.room.number}</td>
                    <td style={{ padding: 'var(--space-4) var(--space-6)' }}>{getTypeLabel(reading.type)}</td>
                    <td style={{ padding: 'var(--space-4) var(--space-6)' }}>{reading.previousReading}</td>
                    <td style={{ padding: 'var(--space-4) var(--space-6)' }}>{reading.currentReading}</td>
                    <td style={{ padding: 'var(--space-4) var(--space-6)', fontWeight: 'bold' }}>{reading.unitsUsed} หน่วย</td>
                    <td style={{ padding: 'var(--space-4) var(--space-6)', fontWeight: 'bold', color: 'var(--color-primary-400)' }}>
                      ฿{reading.totalAmount.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                    </td>
                    <td style={{ padding: 'var(--space-4) var(--space-6)' }}>{new Date(reading.readingDate).toLocaleDateString('th-TH')}</td>
                    <td style={{ padding: 'var(--space-4) var(--space-6)', textAlign: 'right' }}>
                      <button className="btn btn-secondary btn-sm">แก้ไข</button>
                    </td>
                  </tr>
                );
              })}

              {readings.length === 0 && (
                <tr>
                  <td colSpan={9} style={{ textAlign: 'center', padding: 'var(--space-12)', color: 'var(--text-secondary)' }}>
                    <span style={{ fontSize: '32px' }}>⚡</span>
                    <p style={{ marginTop: 'var(--space-2)' }}>ไม่พบข้อมูลการจดมิเตอร์</p>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
