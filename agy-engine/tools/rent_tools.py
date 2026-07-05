"""
เครื่องมือจัดการค่าเช่าสำหรับ RoomGenius AI (ปรับปรุงตาม Schema จริง)
"""

import json
import logging
import uuid
from datetime import date, datetime
from typing import Optional

from db import execute_query, execute_one, execute_command

logger = logging.getLogger(__name__)


async def get_rent_summary(month: str) -> str:
    """ดึงข้อมูลสรุปค่าเช่าของเดือนที่ระบุ รวมถึงยอดรวมที่คาดหวัง ยอดที่เก็บได้ ยอดค้างชำระ และอัตราการเก็บค่าเช่า

    Args:
        month: เดือนที่ต้องการดูสรุป ในรูปแบบ YYYY-MM เช่น 2026-07
    """
    try:
        # ดึงข้อมูลค่าเช่าทั้งหมดของเดือน
        payments = await execute_query(
            """
            SELECT
                p.id, r.number as room_number, l."tenantName" as tenant_name,
                p.amount, p."dueDate" as due_date, p."paidDate" as paid_date, p.status
            FROM payments p
            JOIN leases l ON p."leaseId" = l.id
            JOIN rooms r ON l."roomId" = r.id
            WHERE to_char(p."dueDate", 'YYYY-MM') = $1 AND p.type = 'RENT'
            ORDER BY r.number
            """,
            month,
        )

        if not payments:
            return json.dumps({
                "status": "no_data",
                "message": f"ไม่พบข้อมูลค่าเช่าสำหรับเดือน {month}"
            }, ensure_ascii=False)

        total_expected = sum(p["amount"] for p in payments)
        paid = [p for p in payments if p["status"] == "PAID"]
        unpaid = [p for p in payments if p["status"] == "PENDING"]
        overdue = [p for p in payments if p["status"] == "OVERDUE"]
        total_collected = sum(p["amount"] for p in paid)

        summary = {
            "month": month,
            "total_rooms": len(payments),
            "total_expected": total_expected,
            "total_collected": total_collected,
            "total_outstanding": total_expected - total_collected,
            "paid_count": len(paid),
            "unpaid_count": len(unpaid),
            "overdue_count": len(overdue),
            "collection_rate": round(
                (total_collected / total_expected * 100) if total_expected > 0 else 0, 2
            ),
        }
        return json.dumps(summary, ensure_ascii=False, default=str)

    except Exception as e:
        logger.error(f"ดึงสรุปค่าเช่าล้มเหลว: {e}")
        return json.dumps({"error": f"เกิดข้อผิดพลาด: {str(e)}"}, ensure_ascii=False)


async def get_overdue_payments() -> str:
    """ดึงรายการค่าเช่าที่ค้างชำระทั้งหมด (เลยกำหนดแล้ว) พร้อมรายละเอียดห้องและผู้เช่า"""
    try:
        overdue = await execute_query(
            """
            SELECT
                p.id, r.number as room_number, l."tenantName" as tenant_name,
                l."tenantPhone" as phone, p.amount, p."dueDate" as due_date,
                CURRENT_DATE - p."dueDate"::date as days_overdue
            FROM payments p
            JOIN leases l ON p."leaseId" = l.id
            JOIN rooms r ON l."roomId" = r.id
            WHERE p.status = 'OVERDUE'
                OR (p.status = 'PENDING' AND p."dueDate" < CURRENT_DATE)
            ORDER BY p."dueDate" ASC
            """
        )

        if not overdue:
            return json.dumps({
                "status": "success",
                "message": "ไม่มีค่าเช่าค้างชำระ 🎉",
                "overdue_count": 0,
                "records": []
            }, ensure_ascii=False)

        total_overdue = sum(r["amount"] for r in overdue)
        result = {
            "status": "warning",
            "overdue_count": len(overdue),
            "total_overdue_amount": total_overdue,
            "records": [
                {
                    "id": r["id"],
                    "room_number": r["room_number"],
                    "tenant_name": r["tenant_name"],
                    "phone": r["phone"],
                    "amount": r["amount"],
                    "due_date": str(r["due_date"]),
                    "days_overdue": r["days_overdue"],
                }
                for r in overdue
            ],
        }
        return json.dumps(result, ensure_ascii=False, default=str)

    except Exception as e:
        logger.error(f"ดึงรายการค้างชำระล้มเหลว: {e}")
        return json.dumps({"error": f"เกิดข้อผิดพลาด: {str(e)}"}, ensure_ascii=False)


async def record_rent_payment(
    room_number: str,
    amount: float,
    payment_date: str,
    month: str,
    payment_method: str = "CASH",
) -> str:
    """บันทึกการชำระค่าเช่าของห้องที่ระบุ ใช้เมื่อผู้เช่าจ่ายค่าเช่า

    Args:
        room_number: หมายเลขห้อง เช่น "101", "A201"
        amount: จำนวนเงินที่ชำระ (บาท)
        payment_date: วันที่ชำระในรูปแบบ YYYY-MM-DD
        month: เดือนที่ชำระค่าเช่า ในรูปแบบ YYYY-MM
        payment_method: วิธีการชำระ เช่น CASH, TRANSFER, PROMPTPAY
    """
    try:
        # ค้นหาห้อง
        room = await execute_one(
            "SELECT id FROM rooms WHERE number = $1", room_number
        )
        if not room:
            return json.dumps({
                "error": f"ไม่พบห้อง {room_number}"
            }, ensure_ascii=False)

        # ดึงสัญญาปัจจุบัน
        lease = await execute_one(
            'SELECT id FROM leases WHERE "roomId" = $1 AND status = \'ACTIVE\' LIMIT 1',
            room["id"]
        )
        if not lease:
            return json.dumps({
                "error": f"ไม่พบสัญญาเช่าที่ทำงานอยู่สำหรับห้อง {room_number}"
            }, ensure_ascii=False)

        # ค้นหารายการค่าเช่าของเดือนนั้น
        payment_record = await execute_one(
            """
            SELECT id, amount, status FROM payments
            WHERE "leaseId" = $1 AND to_char("dueDate", 'YYYY-MM') = $2 AND type = 'RENT'
            """,
            lease["id"],
            month,
        )

        if payment_record and payment_record["status"] == "PAID":
            return json.dumps({
                "status": "already_paid",
                "message": f"ห้อง {room_number} ชำระค่าเช่าเดือน {month} แล้ว"
            }, ensure_ascii=False)

        pay_date = datetime.strptime(payment_date, "%Y-%m-%d").date()
        method_db = payment_method.upper()

        if payment_record:
            # อัปเดตรายการที่มีอยู่
            await execute_command(
                """
                UPDATE payments
                SET status = 'PAID', "paidDate" = $1, method = $2, "updatedAt" = NOW()
                WHERE id = $3
                """,
                pay_date,
                method_db,
                payment_record["id"],
            )
            return json.dumps({
                "status": "success",
                "message": f"บันทึกชำระค่าเช่าห้อง {room_number} เดือน {month} "
                           f"จำนวน {amount:,.2f} บาท สำเร็จ",
                "room_number": room_number,
                "amount": amount,
                "payment_date": payment_date,
                "payment_method": payment_method,
            }, ensure_ascii=False)
        else:
            # สร้างรายการใหม่
            new_id = f"pay_{uuid.uuid4().hex[:16]}"
            await execute_command(
                """
                INSERT INTO payments
                    (id, amount, type, method, status, "dueDate", "paidDate", "leaseId", "createdAt", "updatedAt")
                VALUES ($1, $2, 'RENT', $3, 'PAID', $4::date, $5::date, $6, NOW(), NOW())
                """,
                new_id,
                amount,
                method_db,
                f"{month}-01",
                payment_date,
                lease["id"],
            )
            return json.dumps({
                "status": "success",
                "message": f"สร้างและบันทึกชำระค่าเช่าห้อง {room_number} เดือน {month} "
                           f"จำนวน {amount:,.2f} บาท สำเร็จ",
                "room_number": room_number,
                "amount": amount,
                "payment_date": payment_date,
            }, ensure_ascii=False)

    except Exception as e:
        logger.error(f"บันทึกการชำระค่าเช่าล้มเหลว: {e}")
        return json.dumps({"error": f"เกิดข้อผิดพลาด: {str(e)}"}, ensure_ascii=False)


async def get_payment_history(room_number: str, limit: int = 12) -> str:
    """ดึงประวัติการชำระค่าเช่าของห้องที่ระบุ แสดงผลย้อนหลัง

    Args:
        room_number: หมายเลขห้อง เช่น "101"
        limit: จำนวนเดือนที่ต้องการดูย้อนหลัง (ค่าเริ่มต้น 12 เดือน)
    """
    try:
        records = await execute_query(
            """
            SELECT
                p.id, r.number as room_number, l."tenantName" as tenant_name,
                p.amount, p."dueDate" as due_date,
                p."paidDate" as paid_date, p.status, p.method as payment_method,
                to_char(p."dueDate", 'YYYY-MM') as month
            FROM payments p
            JOIN leases l ON p."leaseId" = l.id
            JOIN rooms r ON l."roomId" = r.id
            WHERE r.number = $1 AND p.type = 'RENT'
            ORDER BY p."dueDate" DESC
            LIMIT $2
            """,
            room_number,
            limit,
        )

        if not records:
            return json.dumps({
                "message": f"ไม่พบประวัติการชำระค่าเช่าของห้อง {room_number}",
                "records": []
            }, ensure_ascii=False)

        result = {
            "room_number": room_number,
            "total_records": len(records),
            "records": [
                {
                    "month": r["month"],
                    "amount": r["amount"],
                    "paid_amount": r["amount"] if r["status"] == "PAID" else 0,
                    "due_date": str(r["due_date"]),
                    "paid_date": str(r["paid_date"]) if r["paid_date"] else None,
                    "status": r["status"],
                    "payment_method": r.get("payment_method"),
                }
                for r in records
            ],
        }
        return json.dumps(result, ensure_ascii=False, default=str)

    except Exception as e:
        logger.error(f"ดึงประวัติชำระค่าเช่าล้มเหลว: {e}")
        return json.dumps({"error": f"เกิดข้อผิดพลาด: {str(e)}"}, ensure_ascii=False)


async def generate_rent_invoices(month: str) -> str:
    """สร้างใบแจ้งค่าเช่าสำหรับทุกห้องในเดือนที่ระบุ ใช้สำหรับสร้างรายการเรียกเก็บเงินรอบใหม่

    Args:
        month: เดือนที่ต้องการสร้างใบแจ้ง ในรูปแบบ YYYY-MM
    """
    try:
        # ตรวจสอบว่ามีใบแจ้งของเดือนนี้หรือยัง
        existing = await execute_query(
            """
            SELECT COUNT(*) as cnt FROM payments
            WHERE to_char("dueDate", 'YYYY-MM') = $1 AND type = 'RENT'
            """,
            month,
        )

        if existing and existing[0]["cnt"] > 0:
            return json.dumps({
                "status": "exists",
                "message": f"มีใบแจ้งค่าเช่าเดือน {month} แล้ว จำนวน {existing[0]['cnt']} รายการ",
                "count": existing[0]["cnt"],
            }, ensure_ascii=False)

        # สร้างใบแจ้งสำหรับห้องที่มีผู้เช่า
        result = await execute_command(
            """
            INSERT INTO payments (id, amount, type, status, "dueDate", "leaseId", "createdAt", "updatedAt")
            SELECT
                'inv_' || substr(md5(random()::text), 1, 16),
                l."rentAmount",
                'RENT',
                'PENDING',
                ($1 || '-05')::date,
                l.id,
                NOW(),
                NOW()
            FROM rooms r
            JOIN leases l ON l."roomId" = r.id
            WHERE r.status = 'OCCUPIED'
                AND l.status = 'ACTIVE'
            """,
            month,
        )

        return json.dumps({
            "status": "success",
            "message": f"สร้างใบแจ้งค่าเช่าเดือน {month} สำเร็จ",
            "month": month,
            "result": result,
        }, ensure_ascii=False)

    except Exception as e:
        logger.error(f"สร้างใบแจ้งค่าเช่าล้มเหลว: {e}")
        return json.dumps({"error": f"เกิดข้อผิดพลาด: {str(e)}"}, ensure_ascii=False)


# รวมเครื่องมือทั้งหมดเพื่อ export
RENT_TOOLS = [
    get_rent_summary,
    get_overdue_payments,
    record_rent_payment,
    get_payment_history,
    generate_rent_invoices,
]
