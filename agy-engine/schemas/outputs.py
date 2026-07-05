"""
Pydantic Output Schemas สำหรับ RoomGenius AI

กำหนด structured output schemas ที่ AI agent ใช้สำหรับส่งข้อมูล
ในรูปแบบที่ Next.js frontend สามารถ parse ได้อย่างถูกต้อง
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date
from enum import Enum


# =============================================================================
# Enums
# =============================================================================

class PaymentStatus(str, Enum):
    """สถานะการชำระเงิน"""
    PAID = "paid"
    UNPAID = "unpaid"
    OVERDUE = "overdue"
    PARTIAL = "partial"


class LeaseStatus(str, Enum):
    """สถานะสัญญาเช่า"""
    ACTIVE = "active"
    EXPIRED = "expired"
    TERMINATED = "terminated"
    PENDING = "pending"


class RoomStatus(str, Enum):
    """สถานะห้องพัก"""
    OCCUPIED = "occupied"
    VACANT = "vacant"
    MAINTENANCE = "maintenance"
    RESERVED = "reserved"


class NotificationType(str, Enum):
    """ประเภทการแจ้งเตือน"""
    RENT_DUE = "rent_due"
    RENT_OVERDUE = "rent_overdue"
    LEASE_EXPIRING = "lease_expiring"
    UTILITY_HIGH = "utility_high"
    SUPPLY_LOW = "supply_low"
    MAINTENANCE = "maintenance"
    GENERAL = "general"


class SupplyCategory(str, Enum):
    """หมวดหมู่สิ่งของ"""
    CLEANING = "cleaning"
    TOILETRIES = "toiletries"
    ELECTRICAL = "electrical"
    PLUMBING = "plumbing"
    FURNITURE = "furniture"
    KITCHEN = "kitchen"
    OTHER = "other"


# =============================================================================
# Tenant & Room Schemas
# =============================================================================

class TenantInfo(BaseModel):
    """ข้อมูลผู้เช่า"""
    id: int = Field(description="รหัสผู้เช่า")
    name: str = Field(description="ชื่อ-นามสกุลผู้เช่า")
    phone: Optional[str] = Field(default=None, description="เบอร์โทรศัพท์")
    email: Optional[str] = Field(default=None, description="อีเมล")
    room_number: Optional[str] = Field(default=None, description="หมายเลขห้อง")
    move_in_date: Optional[date] = Field(default=None, description="วันที่เข้าพัก")
    status: Optional[str] = Field(default=None, description="สถานะผู้เช่า")


class RoomInfo(BaseModel):
    """ข้อมูลห้องพัก"""
    id: int = Field(description="รหัสห้อง")
    room_number: str = Field(description="หมายเลขห้อง")
    floor: Optional[int] = Field(default=None, description="ชั้น")
    room_type: Optional[str] = Field(default=None, description="ประเภทห้อง")
    monthly_rent: float = Field(description="ค่าเช่ารายเดือน (บาท)")
    status: RoomStatus = Field(description="สถานะห้อง")
    tenant_name: Optional[str] = Field(default=None, description="ชื่อผู้เช่าปัจจุบัน")


# =============================================================================
# Rent Schemas
# =============================================================================

class RentPaymentRecord(BaseModel):
    """บันทึกการชำระค่าเช่า"""
    id: int = Field(description="รหัสรายการ")
    room_number: str = Field(description="หมายเลขห้อง")
    tenant_name: str = Field(description="ชื่อผู้เช่า")
    amount: float = Field(description="จำนวนเงิน (บาท)")
    due_date: date = Field(description="วันครบกำหนด")
    paid_date: Optional[date] = Field(default=None, description="วันที่ชำระ")
    status: PaymentStatus = Field(description="สถานะการชำระ")
    month: str = Field(description="เดือนที่ชำระ (YYYY-MM)")


class RentSummary(BaseModel):
    """สรุปค่าเช่ารายเดือน"""
    month: str = Field(description="เดือน (YYYY-MM)")
    total_rooms: int = Field(description="จำนวนห้องทั้งหมด")
    total_expected: float = Field(description="ยอดค่าเช่าที่คาดหวัง (บาท)")
    total_collected: float = Field(description="ยอดค่าเช่าที่เก็บได้ (บาท)")
    total_outstanding: float = Field(description="ยอดค้างชำระ (บาท)")
    paid_count: int = Field(description="จำนวนห้องที่ชำระแล้ว")
    unpaid_count: int = Field(description="จำนวนห้องที่ยังไม่ชำระ")
    overdue_count: int = Field(description="จำนวนห้องที่เลยกำหนด")
    collection_rate: float = Field(description="อัตราการเก็บค่าเช่า (%)")


# =============================================================================
# Utility Schemas
# =============================================================================

class UtilityReading(BaseModel):
    """ข้อมูลมิเตอร์น้ำ/ไฟ"""
    id: int = Field(description="รหัสรายการ")
    room_number: str = Field(description="หมายเลขห้อง")
    utility_type: str = Field(description="ประเภท (water/electric)")
    previous_reading: float = Field(description="เลขมิเตอร์ครั้งก่อน")
    current_reading: float = Field(description="เลขมิเตอร์ปัจจุบัน")
    units_used: float = Field(description="หน่วยที่ใช้")
    rate_per_unit: float = Field(description="ราคาต่อหน่วย (บาท)")
    total_cost: float = Field(description="ค่าใช้จ่ายรวม (บาท)")
    reading_date: date = Field(description="วันที่จดมิเตอร์")
    month: str = Field(description="เดือน (YYYY-MM)")


class UtilityBill(BaseModel):
    """บิลค่าน้ำ/ค่าไฟ"""
    room_number: str = Field(description="หมายเลขห้อง")
    tenant_name: str = Field(description="ชื่อผู้เช่า")
    water_cost: float = Field(description="ค่าน้ำ (บาท)")
    electric_cost: float = Field(description="ค่าไฟ (บาท)")
    total_cost: float = Field(description="รวมทั้งหมด (บาท)")
    month: str = Field(description="เดือน (YYYY-MM)")
    status: PaymentStatus = Field(description="สถานะการชำระ")


# =============================================================================
# Supply Schemas
# =============================================================================

class SupplyItem(BaseModel):
    """รายการสิ่งของในคลัง"""
    id: int = Field(description="รหัสสิ่งของ")
    name: str = Field(description="ชื่อสิ่งของ")
    category: SupplyCategory = Field(description="หมวดหมู่")
    quantity: int = Field(description="จำนวนคงเหลือ")
    min_quantity: int = Field(description="จำนวนขั้นต่ำ")
    unit: str = Field(description="หน่วยนับ")
    unit_cost: float = Field(description="ราคาต่อหน่วย (บาท)")
    last_restocked: Optional[date] = Field(default=None, description="วันที่เติมล่าสุด")
    needs_restock: bool = Field(description="ต้องเติมสินค้าหรือไม่")


class SupplyOrder(BaseModel):
    """ใบสั่งซื้อสิ่งของ"""
    id: int = Field(description="รหัสใบสั่งซื้อ")
    items: list[str] = Field(description="รายการสิ่งของ")
    total_cost: float = Field(description="ราคารวม (บาท)")
    order_date: date = Field(description="วันที่สั่งซื้อ")
    status: str = Field(description="สถานะ")
    notes: Optional[str] = Field(default=None, description="หมายเหตุ")


# =============================================================================
# Lease Schemas
# =============================================================================

class LeaseInfo(BaseModel):
    """ข้อมูลสัญญาเช่า"""
    id: int = Field(description="รหัสสัญญา")
    room_number: str = Field(description="หมายเลขห้อง")
    tenant_name: str = Field(description="ชื่อผู้เช่า")
    start_date: date = Field(description="วันเริ่มสัญญา")
    end_date: date = Field(description="วันสิ้นสุดสัญญา")
    monthly_rent: float = Field(description="ค่าเช่ารายเดือน (บาท)")
    deposit: float = Field(description="เงินมัดจำ (บาท)")
    status: LeaseStatus = Field(description="สถานะสัญญา")
    days_remaining: Optional[int] = Field(default=None, description="จำนวนวันเหลือ")
    auto_renew: bool = Field(default=False, description="ต่อสัญญาอัตโนมัติ")


class LeaseRenewal(BaseModel):
    """ข้อมูลการต่อสัญญา"""
    lease_id: int = Field(description="รหัสสัญญาเดิม")
    room_number: str = Field(description="หมายเลขห้อง")
    tenant_name: str = Field(description="ชื่อผู้เช่า")
    old_end_date: date = Field(description="วันสิ้นสุดเดิม")
    new_end_date: date = Field(description="วันสิ้นสุดใหม่")
    new_monthly_rent: float = Field(description="ค่าเช่าใหม่ (บาท)")
    rent_change_percent: float = Field(description="การเปลี่ยนแปลงค่าเช่า (%)")


# =============================================================================
# Analytics Schemas
# =============================================================================

class OccupancyReport(BaseModel):
    """รายงานอัตราการเข้าพัก"""
    total_rooms: int = Field(description="จำนวนห้องทั้งหมด")
    occupied_rooms: int = Field(description="จำนวนห้องที่มีผู้เช่า")
    vacant_rooms: int = Field(description="จำนวนห้องว่าง")
    maintenance_rooms: int = Field(description="จำนวนห้องซ่อมบำรุง")
    occupancy_rate: float = Field(description="อัตราการเข้าพัก (%)")
    average_stay_months: Optional[float] = Field(default=None, description="ระยะเวลาเฉลี่ยที่พัก (เดือน)")


class RevenueReport(BaseModel):
    """รายงานรายได้"""
    month: str = Field(description="เดือน (YYYY-MM)")
    rent_income: float = Field(description="รายได้จากค่าเช่า (บาท)")
    utility_income: float = Field(description="รายได้จากค่าน้ำ/ไฟ (บาท)")
    other_income: float = Field(description="รายได้อื่นๆ (บาท)")
    total_income: float = Field(description="รายได้รวม (บาท)")
    expenses: float = Field(description="ค่าใช้จ่าย (บาท)")
    net_income: float = Field(description="กำไรสุทธิ (บาท)")
    growth_percent: Optional[float] = Field(default=None, description="อัตราเติบโต (%)")


class AnalyticsReport(BaseModel):
    """รายงานวิเคราะห์ภาพรวม"""
    generated_at: datetime = Field(description="เวลาที่สร้างรายงาน")
    occupancy: OccupancyReport = Field(description="ข้อมูลอัตราเข้าพัก")
    revenue: RevenueReport = Field(description="ข้อมูลรายได้")
    alerts: list[str] = Field(description="การแจ้งเตือนที่สำคัญ")
    recommendations: list[str] = Field(description="คำแนะนำจาก AI")


# =============================================================================
# Notification Schemas
# =============================================================================

class NotificationResult(BaseModel):
    """ผลลัพธ์การส่งแจ้งเตือน"""
    notification_type: NotificationType = Field(description="ประเภทการแจ้งเตือน")
    recipients: list[str] = Field(description="ผู้รับแจ้งเตือน")
    message: str = Field(description="ข้อความแจ้งเตือน")
    sent_at: datetime = Field(description="เวลาที่ส่ง")
    success: bool = Field(description="ส่งสำเร็จหรือไม่")
    channel: str = Field(description="ช่องทาง (line/sms/email)")


# =============================================================================
# Maintenance Schemas
# =============================================================================

class MaintenanceRequest(BaseModel):
    """คำร้องแจ้งซ่อม"""
    id: int = Field(description="รหัสคำร้อง")
    room_number: str = Field(description="หมายเลขห้อง")
    tenant_name: str = Field(description="ชื่อผู้แจ้ง")
    description: str = Field(description="รายละเอียดปัญหา")
    priority: str = Field(description="ความเร่งด่วน (low/medium/high/critical)")
    status: str = Field(description="สถานะ (pending/in_progress/completed)")
    created_at: datetime = Field(description="วันที่แจ้ง")
    resolved_at: Optional[datetime] = Field(default=None, description="วันที่แก้ไขเสร็จ")


# =============================================================================
# Daily Summary Schema
# =============================================================================

class DailySummary(BaseModel):
    """สรุปรายวัน"""
    date: date = Field(description="วันที่")
    rent_collected_today: float = Field(description="ค่าเช่าที่เก็บได้วันนี้ (บาท)")
    pending_payments: int = Field(description="จำนวนรายการรอชำระ")
    overdue_payments: int = Field(description="จำนวนรายการค้างชำระ")
    new_tenants: int = Field(description="ผู้เช่าใหม่วันนี้")
    move_outs: int = Field(description="ผู้เช่าย้ายออกวันนี้")
    maintenance_pending: int = Field(description="งานซ่อมรอดำเนินการ")
    low_stock_items: int = Field(description="สิ่งของที่ต้องเติม")
    leases_expiring_soon: int = Field(description="สัญญาใกล้หมดอายุ")
    occupancy_rate: float = Field(description="อัตราการเข้าพัก (%)")
    alerts: list[str] = Field(description="การแจ้งเตือนสำคัญ")
