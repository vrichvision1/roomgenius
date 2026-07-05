import React from 'react';
import { prisma } from '@/lib/db';

export const revalidate = 0;

export default async function PaymentsPage() {
  const payments = await prisma.payment.findMany({
    include: { lease: { include: { room: true } } },
    orderBy: { dueDate: 'desc' },
  });

  const getStatusBadgeClass = (status: string) => {
    switch (status) {
      case 'PAID':
        return 'badge-success';
      case 'OVERDUE':
        return 'badge-danger';
      case 'PENDING':
        return 'badge-warning';
      default:
        return 'badge-secondary';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'PAID':
        return 'จ่ายแล้ว';
      case 'OVERDUE':
        return 'ค้างชำระ';
      case 'PENDING':
        return 'รอจ่าย';
      default:
        return status;
    }
  };

  const getTypeLabel = (type: string) => {
    switch (type) {
      case 'RENT':
        return 'ค่าเช่าห้อง';
      case 'UTILITY':
        return 'ค่าน้ำ/ค่าไฟ';
      case 'DEPOSIT':
        return 'เงินมัดจำ';
      default:
        return type;
    }
  };

  return (
    <div className="space-y-6">
      <div className="page-header">
        <div>
          <h1 className="page-title">💰 การชำระเงิน</h1>
          <p className="page-subtitle">ตรวจสอบ บันทึก และบริหารรายรับรายจ่ายในระบบหอพัก</p>
        </div>
      </div>

      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        <div style={{ overflowX: 'auto' }}>
          <table className="table" style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border-primary)', textAlign: 'left' }}>
                <th style={{ padding: 'var(--space-4) var(--space-6)', color: 'var(--text-secondary)' }}>ห้อง</th>
                <th style={{ padding: 'var(--space-4) var(--space-6)', color: 'var(--text-secondary)' }}>ผู้เช่า</th>
                <th style={{ padding: 'var(--space-4) var(--space-6)', color: 'var(--text-secondary)' }}>ประเภท</th>
                <th style={{ padding: 'var(--space-4) var(--space-6)', color: 'var(--text-secondary)' }}>จำนวนเงิน</th>
                <th style={{ padding: 'var(--space-4) var(--space-6)', color: 'var(--text-secondary)' }}>กำหนดชำระ</th>
                <th style={{ padding: 'var(--space-4) var(--space-6)', color: 'var(--text-secondary)' }}>วันที่ชำระ</th>
                <th style={{ padding: 'var(--space-4) var(--space-6)', color: 'var(--text-secondary)' }}>วิธีชำระ</th>
                <th style={{ padding: 'var(--space-4) var(--space-6)', color: 'var(--text-secondary)' }}>สถานะ</th>
                <th style={{ padding: 'var(--space-4) var(--space-6)', color: 'var(--text-secondary)' }}></th>
              </tr>
            </thead>
            <tbody>
              {payments.map((payment) => (
                <tr key={payment.id} style={{ borderBottom: '1px solid var(--border-secondary)' }}>
                  <td style={{ padding: 'var(--space-4) var(--space-6)', fontWeight: 'bold' }}>ห้อง {payment.lease.room.number}</td>
                  <td style={{ padding: 'var(--space-4) var(--space-6)' }}>{payment.lease.tenantName}</td>
                  <td style={{ padding: 'var(--space-4) var(--space-6)' }}>{getTypeLabel(payment.type)}</td>
                  <td style={{ padding: 'var(--space-4) var(--space-6)', fontWeight: 'bold', color: 'var(--color-primary-400)' }}>
                    ฿{payment.amount.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                  </td>
                  <td style={{ padding: 'var(--space-4) var(--space-6)' }}>{new Date(payment.dueDate).toLocaleDateString('th-TH')}</td>
                  <td style={{ padding: 'var(--space-4) var(--space-6)' }}>
                    {payment.paidDate ? new Date(payment.paidDate).toLocaleDateString('th-TH') : '-'}
                  </td>
                  <td style={{ padding: 'var(--space-4) var(--space-6)' }}>{payment.method}</td>
                  <td style={{ padding: 'var(--space-4) var(--space-6)' }}>
                    <span className={`badge ${getStatusBadgeClass(payment.status)}`}>{getStatusLabel(payment.status)}</span>
                  </td>
                  <td style={{ padding: 'var(--space-4) var(--space-6)', textAlign: 'right' }}>
                    {payment.status !== 'PAID' && (
                      <button className="btn btn-primary btn-sm">บันทึกรับเงิน</button>
                    )}
                  </td>
                </tr>
              ))}

              {payments.length === 0 && (
                <tr>
                  <td colSpan={9} style={{ textAlign: 'center', padding: 'var(--space-12)', color: 'var(--text-secondary)' }}>
                    <span style={{ fontSize: '32px' }}>💰</span>
                    <p style={{ marginTop: 'var(--space-2)' }}>ไม่พบข้อมูลรายการเงินเรียกเก็บ</p>
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
