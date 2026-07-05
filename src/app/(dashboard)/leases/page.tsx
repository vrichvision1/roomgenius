import React from 'react';
import { prisma } from '@/lib/db';

export const revalidate = 0;

export default async function LeasesPage() {
  const leases = await prisma.lease.findMany({
    include: { room: true },
    orderBy: { startDate: 'desc' },
  });

  const getStatusBadgeClass = (status: string) => {
    switch (status) {
      case 'ACTIVE':
        return 'badge-success';
      case 'TERMINATED':
        return 'badge-danger';
      case 'EXPIRED':
        return 'badge-secondary';
      default:
        return 'badge-primary';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'ACTIVE':
        return 'สัญญาใช้งานอยู่';
      case 'TERMINATED':
        return 'ยกเลิกแล้ว';
      case 'EXPIRED':
        return 'หมดอายุ';
      case 'PENDING':
        return 'รอดำเนินการ';
      default:
        return status;
    }
  };

  return (
    <div className="space-y-6">
      <div className="page-header">
        <div>
          <h1 className="page-title">📋 สัญญาเช่าห้อง</h1>
          <p className="page-subtitle">ติดตามและตรวจสอบสัญญาของผู้เช่าทุกคน</p>
        </div>
      </div>

      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        <div style={{ overflowX: 'auto' }}>
          <table className="table" style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border-primary)', textAlign: 'left' }}>
                <th style={{ padding: 'var(--space-4) var(--space-6)', color: 'var(--text-secondary)' }}>ห้อง</th>
                <th style={{ padding: 'var(--space-4) var(--space-6)', color: 'var(--text-secondary)' }}>ชื่อผู้เช่า</th>
                <th style={{ padding: 'var(--space-4) var(--space-6)', color: 'var(--text-secondary)' }}>เบอร์โทร</th>
                <th style={{ padding: 'var(--space-4) var(--space-6)', color: 'var(--text-secondary)' }}>วันเริ่มต้นสัญญา</th>
                <th style={{ padding: 'var(--space-4) var(--space-6)', color: 'var(--text-secondary)' }}>วันสิ้นสุดสัญญา</th>
                <th style={{ padding: 'var(--space-4) var(--space-6)', color: 'var(--text-secondary)' }}>ค่าเช่า / มัดจำ</th>
                <th style={{ padding: 'var(--space-4) var(--space-6)', color: 'var(--text-secondary)' }}>สถานะ</th>
                <th style={{ padding: 'var(--space-4) var(--space-6)', color: 'var(--text-secondary)' }}></th>
              </tr>
            </thead>
            <tbody>
              {leases.map((lease) => (
                <tr key={lease.id} style={{ borderBottom: '1px solid var(--border-secondary)' }}>
                  <td style={{ padding: 'var(--space-4) var(--space-6)', fontWeight: 'bold' }}>ห้อง {lease.room.number}</td>
                  <td style={{ padding: 'var(--space-4) var(--space-6)' }}>{lease.tenantName}</td>
                  <td style={{ padding: 'var(--space-4) var(--space-6)' }}>{lease.tenantPhone || 'N/A'}</td>
                  <td style={{ padding: 'var(--space-4) var(--space-6)' }}>{new Date(lease.startDate).toLocaleDateString('th-TH')}</td>
                  <td style={{ padding: 'var(--space-4) var(--space-6)' }}>{new Date(lease.endDate).toLocaleDateString('th-TH')}</td>
                  <td style={{ padding: 'var(--space-4) var(--space-6)' }}>
                    <div style={{ fontWeight: 'bold' }}>฿{lease.rentAmount.toLocaleString()}</div>
                    <div style={{ fontSize: 'var(--text-xs)', color: 'var(--text-tertiary)' }}>มัดจำ: ฿{lease.depositAmount.toLocaleString()}</div>
                  </td>
                  <td style={{ padding: 'var(--space-4) var(--space-6)' }}>
                    <span className={`badge ${getStatusBadgeClass(lease.status)}`}>{getStatusLabel(lease.status)}</span>
                  </td>
                  <td style={{ padding: 'var(--space-4) var(--space-6)', textAlign: 'right' }}>
                    <button className="btn btn-secondary btn-sm">ดูรายละเอียด</button>
                  </td>
                </tr>
              ))}

              {leases.length === 0 && (
                <tr>
                  <td colSpan={8} style={{ textAlign: 'center', padding: 'var(--space-12)', color: 'var(--text-secondary)' }}>
                    <span style={{ fontSize: '32px' }}>📋</span>
                    <p style={{ marginTop: 'var(--space-2)' }}>ไม่พบข้อมูลสัญญาเช่าในระบบ</p>
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
