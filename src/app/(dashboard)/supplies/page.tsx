import React from 'react';
import { prisma } from '@/lib/db';

export const revalidate = 0;

export default async function SuppliesPage() {
  const supplies = await prisma.supplyItem.findMany({
    orderBy: { name: 'asc' },
  });

  return (
    <div className="space-y-6">
      <div className="page-header">
        <div>
          <h1 className="page-title">🧻 วัสดุสิ้นเปลือง / สินค้าคงคลัง</h1>
          <p className="page-subtitle">จัดการสต็อกวัสดุและอุปกรณ์สิ้นเปลืองสำหรับอำนวยความสะดวกในโครงการ</p>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 'var(--space-6)' }}>
        {supplies.map((item) => {
          const isLowStock = item.currentStock <= item.minimumStock;
          return (
            <div key={item.id} className="card" style={{ borderLeft: `6px solid ${isLowStock ? 'var(--color-danger-500)' : 'var(--color-success-500)'}` }}>
              <div className="flex items-center justify-between mb-4">
                <h3 style={{ fontSize: 'var(--text-md)', fontWeight: 'bold' }}>{item.name}</h3>
                {isLowStock ? (
                  <span className="badge badge-danger">ใกล้หมด 🚨</span>
                ) : (
                  <span className="badge badge-success">เพียงพอ</span>
                )}
              </div>

              <div className="space-y-2 mb-4" style={{ fontSize: 'var(--text-xs)', color: 'var(--text-secondary)' }}>
                <div className="flex justify-between">
                  <span>จำนวนคงคลังปัจจุบัน:</span>
                  <span style={{ fontSize: 'var(--text-sm)', fontWeight: 'bold', color: isLowStock ? 'var(--color-danger-400)' : 'var(--text-primary)' }}>
                    {item.currentStock} {item.unit || 'ชิ้น'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>เกณฑ์แจ้งเตือนขั้นต่ำ:</span>
                  <span style={{ color: 'var(--text-primary)' }}>{item.minimumStock} {item.unit || 'ชิ้น'}</span>
                </div>
                <div className="flex justify-between">
                  <span>ราคาทุนต่อหน่วย:</span>
                  <span style={{ color: 'var(--text-primary)' }}>฿{item.costPerUnit.toLocaleString(undefined, { minimumFractionDigits: 2 })}</span>
                </div>
              </div>

              <div style={{ marginTop: 'var(--space-4)', display: 'flex', gap: 'var(--space-2)' }}>
                <button className="btn btn-secondary btn-sm w-full">แก้ไขจำนวน</button>
                <button className="btn btn-primary btn-sm">🛒 สั่งซื้อ</button>
              </div>
            </div>
          );
        })}

        {supplies.length === 0 && (
          <div className="card text-center" style={{ gridColumn: '1 / -1', padding: 'var(--space-12)' }}>
            <span style={{ fontSize: '48px' }}>🧻</span>
            <h3 style={{ marginTop: 'var(--space-4)', fontSize: 'var(--text-lg)', fontWeight: 'bold' }}>ไม่พบข้อมูลวัสดุ</h3>
            <p style={{ color: 'var(--text-secondary)' }}>เริ่มสร้างรายการของใช้และควบคุมสต็อกได้ที่นี่</p>
          </div>
        )}
      </div>
    </div>
  );
}
