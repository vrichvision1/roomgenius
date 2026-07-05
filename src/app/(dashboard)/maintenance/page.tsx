import React from 'react';
import { prisma } from '@/lib/db';

export const revalidate = 0;

export default async function MaintenancePage() {
  const requests = await prisma.maintenanceRequest.findMany({
    include: { property: true },
    orderBy: { createdAt: 'desc' },
  });

  const getPriorityBadgeClass = (priority: string) => {
    switch (priority) {
      case 'URGENT':
        return 'badge-danger';
      case 'HIGH':
        return 'badge-warning';
      case 'MEDIUM':
        return 'badge-primary';
      case 'LOW':
        return 'badge-secondary';
      default:
        return 'badge-secondary';
    }
  };

  const getPriorityLabel = (priority: string) => {
    switch (priority) {
      case 'URGENT':
        return 'ด่วนที่สุด 🚨';
      case 'HIGH':
        return 'ด่วน ⚠️';
      case 'MEDIUM':
        return 'ปานกลาง';
      case 'LOW':
        return 'ต่ำ';
      default:
        return priority;
    }
  };

  const getStatusBadgeClass = (status: string) => {
    switch (status) {
      case 'OPEN':
        return 'badge-primary';
      case 'IN_PROGRESS':
        return 'badge-warning';
      case 'RESOLVED':
        return 'badge-success';
      case 'CANCELLED':
        return 'badge-secondary';
      default:
        return 'badge-secondary';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'OPEN':
        return 'รอดำเนินการ';
      case 'IN_PROGRESS':
        return 'กำลังดำเนินการ';
      case 'RESOLVED':
        return 'ซ่อมเสร็จสิ้น';
      case 'CANCELLED':
        return 'ยกเลิก';
      default:
        return status;
    }
  };

  return (
    <div className="space-y-6">
      <div className="page-header">
        <div>
          <h1 className="page-title">🔧 งานแจ้งซ่อมบำรุง</h1>
          <p className="page-subtitle">จัดการและติดตามสถานะงานแจ้งซ่อมบำรุงในโครงการทั้งหมด</p>
        </div>
      </div>

      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        <div style={{ overflowX: 'auto' }}>
          <table className="table" style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border-primary)', textAlign: 'left' }}>
                <th style={{ padding: 'var(--space-4) var(--space-6)', color: 'var(--text-secondary)' }}>หัวข้องาน</th>
                <th style={{ padding: 'var(--space-4) var(--space-6)', color: 'var(--text-secondary)' }}>อาคาร / ห้อง</th>
                <th style={{ padding: 'var(--space-4) var(--space-6)', color: 'var(--text-secondary)' }}>หมวดหมู่</th>
                <th style={{ padding: 'var(--space-4) var(--space-6)', color: 'var(--text-secondary)' }}>ความสำคัญ</th>
                <th style={{ padding: 'var(--space-4) var(--space-6)', color: 'var(--text-secondary)' }}>ผู้รับผิดชอบ</th>
                <th style={{ padding: 'var(--space-4) var(--space-6)', color: 'var(--text-secondary)' }}>ประมาณการค่าใช้จ่าย</th>
                <th style={{ padding: 'var(--space-4) var(--space-6)', color: 'var(--text-secondary)' }}>วันที่แจ้ง</th>
                <th style={{ padding: 'var(--space-4) var(--space-6)', color: 'var(--text-secondary)' }}>สถานะ</th>
                <th style={{ padding: 'var(--space-4) var(--space-6)', color: 'var(--text-secondary)' }}></th>
              </tr>
            </thead>
            <tbody>
              {requests.map((req) => (
                <tr key={req.id} style={{ borderBottom: '1px solid var(--border-secondary)' }}>
                  <td style={{ padding: 'var(--space-4) var(--space-6)' }}>
                    <div style={{ fontWeight: 'bold' }}>{req.title}</div>
                    <div style={{ fontSize: 'var(--text-xs)', color: 'var(--text-secondary)', marginTop: 'var(--space-1)' }}>
                      {req.description}
                    </div>
                  </td>
                  <td style={{ padding: 'var(--space-4) var(--space-6)' }}>
                    <div>{req.property.name}</div>
                    {req.roomNumber && (
                      <div style={{ fontSize: 'var(--text-xs)', fontWeight: 'bold', color: 'var(--color-primary-400)', marginTop: 'var(--space-1)' }}>
                        ห้อง {req.roomNumber}
                      </div>
                    )}
                  </td>
                  <td style={{ padding: 'var(--space-4) var(--space-6)' }}>{req.category || '-'}</td>
                  <td style={{ padding: 'var(--space-4) var(--space-6)' }}>
                    <span className={`badge ${getPriorityBadgeClass(req.priority)}`}>{getPriorityLabel(req.priority)}</span>
                  </td>
                  <td style={{ padding: 'var(--space-4) var(--space-6)' }}>{req.assignedTo || 'ยังไม่ได้มอบหมาย'}</td>
                  <td style={{ padding: 'var(--space-4) var(--space-6)', fontWeight: 'bold' }}>
                    {req.estimatedCost ? `฿${req.estimatedCost.toLocaleString()}` : '-'}
                  </td>
                  <td style={{ padding: 'var(--space-4) var(--space-6)' }}>{new Date(req.createdAt).toLocaleDateString('th-TH')}</td>
                  <td style={{ padding: 'var(--space-4) var(--space-6)' }}>
                    <span className={`badge ${getStatusBadgeClass(req.status)}`}>{getStatusLabel(req.status)}</span>
                  </td>
                  <td style={{ padding: 'var(--space-4) var(--space-6)', textAlign: 'right' }}>
                    <button className="btn btn-secondary btn-sm">อัปเดตสถานะ</button>
                  </td>
                </tr>
              ))}

              {requests.length === 0 && (
                <tr>
                  <td colSpan={9} style={{ textAlign: 'center', padding: 'var(--space-12)', color: 'var(--text-secondary)' }}>
                    <span style={{ fontSize: '32px' }}>🔧</span>
                    <p style={{ marginTop: 'var(--space-2)' }}>ไม่พบข้อมูลรายการแจ้งซ่อม</p>
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
