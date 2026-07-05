"""
เครื่องมือจัดการสัญญาเช่าสำหรับ RoomGenius AI (ปรับปรุงตาม Schema จริง)
"""

import json
import logging
from datetime import date, datetime, timedelta
from typing import Optional

from db import execute_query, execute_one, execute_command

logger = logging.getLogger(__name__)


async def get_lease_info(room_number: str) -> str:
    """ดึงข้อมูลสัญญาเช่าปัจจุบันของห้องที่ระบุ พร้อมรายละเอียดวันเริ่ม วันสิ้นสุด ค่าเช่า เงินมัดจำ

    Args:
        room_number: หมายเลขห้อง เช่น "101", "A201"
    """
    try:
        lease = await execute_one(
            """
            SELECT
                l.id, r.number as room_number, l."tenantName" as tenant_name,
                l."tenantPhone" as phone, l."tenantEmail" as email,
                l."startDate" as start_date, l."endDate" as end_date, l."rentAmount" as monthly_rent,
                l."depositAmount" as deposit, l.status,
                (l."endDate"::date - CURRENT_DATE) as days_remaining,
                l.terms, l.notes
            FROM leases l
            JOIN rooms r ON l."roomId" = r.id
            WHERE r.number = $1
                AND l.status IN ('ACTIVE', 'PENDING')
            ORDER BY l."startDate" DESC
            LIMIT 1
            """,
            room_number,
        )

        if not lease:
            return json.dumps({
                "message": f"ไม่พบสัญญาเช่าที่มีผลบังคับใช้สำหรับห้อง {room_number}"
            }, ensure_ascii=False)

        result = {
            "id": lease["id"],
            "room_number": lease["room_number"],
            "tenant_name": lease["tenant_name"],
            "phone": lease["phone"],
            "email": lease["email"],
            "start_date": str(lease["start_date"]),
            "end_date": str(lease["end_date"]),
            "monthly_rent": float(lease["monthly_rent"]),
            "deposit": float(lease["deposit"]),
            "status": lease["status"],
            "days_remaining": lease["days_remaining"],
            "auto_renew": False,
            "terms": lease.get("terms"),
            "notes": lease.get("notes"),
        }
        return json.dumps(result, ensure_ascii=False, default=str)

    except Exception as e:
        logger.error(f"ดึงข้อมูลสัญญาเช่าล้มเหลว: {e}")
        return json.dumps({"error": f"เกิดข้อผิดพลาด: {str(e)}"}, ensure_ascii=False)


async def get_expiring_leases(days: int = 30) -> str:
    """ดึงรายการสัญญาเช่าที่จะหมดอายุภายในจำนวนวันที่ระบุ ใช้สำหรับวางแผนต่อสัญญา

    Args:
        days: จำนวนวันข้างหน้าที่ต้องการตรวจสอบ (ค่าเริ่มต้น 30 วัน)
    """
    try:
        leases = await execute_query(
            """
            SELECT
                l.id, r.number as room_number, l."tenantName" as tenant_name,
                l."tenantPhone" as phone, l."endDate" as end_date, l."rentAmount" as monthly_rent,
                (l."endDate"::date - CURRENT_DATE) as days_remaining
            FROM leases l
            JOIN rooms r ON l."roomId" = r.id
            WHERE l.status = 'ACTIVE'
                AND l."endDate" <= CURRENT_DATE + ($1 || ' days')::interval
                AND l."endDate" >= CURRENT_DATE
            ORDER BY l."endDate" ASC
            """,
            str(days),
        )

        if not leases:
            return json.dumps({
                "status": "ok",
                "message": f"ไม่มีสัญญาเช่าที่จะหมดอายุภายใน {days} วัน",
                "leases": []
            }, ensure_ascii=False)

        result = {
            "status": "attention",
            "message": f"มี {len(leases)} สัญญาที่จะหมดอายุภายใน {days} วัน",
            "leases": [
                {
                    "id": l["id"],
                    "room_number": l["room_number"],
                    "tenant_name": l["tenant_name"],
                    "phone": l["phone"],
                    "end_date": str(l["end_date"]),
                    "monthly_rent": float(l["monthly_rent"]),
                    "days_remaining": l["days_remaining"],
                    "auto_renew": False,
                }
                for l in leases
            ],
        }
        return json.dumps(result, ensure_ascii=False, default=str)

    except Exception as e:
        logger.error(f"ดึงสัญญาใกล้หมดอายุล้มเหลว: {e}")
        return json.dumps({"error": f"เกิดข้อผิดพลาด: {str(e)}"}, ensure_ascii=False)


async def renew_lease(
    room_number: str,
    new_end_date: str,
    new_monthly_rent: Optional[float] = None,
) -> str:
    """ต่อสัญญาเช่าของห้องที่ระบุ โดยขยายวันสิ้นสุดและอัปเดตค่าเช่าใหม่ (ถ้ามี)

    Args:
        room_number: หมายเลขห้อง เช่น "101"
        new_end_date: วันสิ้นสุดสัญญาใหม่ ในรูปแบบ YYYY-MM-DD
        new_monthly_rent: ค่าเช่ารายเดือนใหม่ (บาท) ถ้าไม่ระบุจะใช้ค่าเดิม
    """
    try:
        # ค้นหาสัญญาปัจจุบัน
        current = await execute_one(
            """
            SELECT l.id, l."rentAmount" as monthly_rent, l."endDate" as end_date, l."tenantName" as tenant_name
            FROM leases l
            JOIN rooms r ON l."roomId" = r.id
            WHERE r.number = $1 AND l.status = 'ACTIVE'
            ORDER BY l."endDate" DESC
            LIMIT 1
            """,
            room_number,
        )

        if not current:
            return json.dumps({
                "error": f"ไม่พบสัญญาเช่าที่มีผลบังคับใช้ของห้อง {room_number}"
            }, ensure_ascii=False)

        rent = new_monthly_rent if new_monthly_rent else float(current["monthly_rent"])
        old_rent = float(current["monthly_rent"])
        rent_change = round(((rent - old_rent) / old_rent * 100) if old_rent > 0 else 0, 2)
        new_end = datetime.strptime(new_end_date, "%Y-%m-%d").date()

        # อัปเดตสัญญา
        await execute_command(
            """
            UPDATE leases
            SET "endDate" = $1, "rentAmount" = $2, "updatedAt" = NOW()
            WHERE id = $3
            """,
            new_end,
            rent,
            current["id"],
        )

        # อัปเดตค่าเช่าในตารางห้อง
        if new_monthly_rent:
            await execute_command(
                """
                UPDATE rooms SET "monthlyRate" = $1
                WHERE number = $2
                """,
                rent,
                room_number,
            )

        result = {
            "status": "success",
            "message": f"ต่อสัญญาห้อง {room_number} สำเร็จ",
            "lease_id": current["id"],
            "room_number": room_number,
            "tenant_name": current["tenant_name"],
            "old_end_date": str(current["end_date"]),
            "new_end_date": new_end_date,
            "new_monthly_rent": rent,
            "rent_change_percent": rent_change,
        }
        return json.dumps(result, ensure_ascii=False, default=str)

    except Exception as e:
        logger.error(f"ต่อสัญญาเช่าล้มเหลว: {e}")
        return json.dumps({"error": f"เกิดข้อผิดพลาด: {str(e)}"}, ensure_ascii=False)


async def terminate_lease(room_number: str, reason: str, move_out_date: str) -> str:
    """ยกเลิกสัญญาเช่าของห้องที่ระบุ พร้อมบันทึกเหตุผลและวันที่ย้ายออก

    Args:
        room_number: หมายเลขห้อง
        reason: เหตุผลในการยกเลิก
        move_out_date: วันที่ย้ายออก ในรูปแบบ YYYY-MM-DD
    """
    try:
        lease = await execute_one(
            """
            SELECT l.id, l."depositAmount" as deposit, l."tenantName" as tenant_name
            FROM leases l
            JOIN rooms r ON l."roomId" = r.id
            WHERE r.number = $1 AND l.status = 'ACTIVE'
            LIMIT 1
            """,
            room_number,
        )

        if not lease:
            return json.dumps({
                "error": f"ไม่พบสัญญาเช่าที่มีผลบังคับใช้ของห้อง {room_number}"
            }, ensure_ascii=False)

        move_date = datetime.strptime(move_out_date, "%Y-%m-%d").date()

        # ยกเลิกสัญญา
        await execute_command(
            """
            UPDATE leases
            SET status = 'TERMINATED', notes = COALESCE(notes, '') || '\nTermination Reason: ' || $1,
                "updatedAt" = NOW()
            WHERE id = $2
            """,
            reason,
            lease["id"],
        )

        # อัปเดตสถานะห้อง
        await execute_command(
            """
            UPDATE rooms SET status = 'VACANT', "updatedAt" = NOW()
            WHERE number = $1
            """,
            room_number,
        )

        result = {
            "status": "success",
            "message": f"ยกเลิกสัญญาห้อง {room_number} สำเร็จ",
            "room_number": room_number,
            "tenant_name": lease["tenant_name"],
            "move_out_date": move_out_date,
            "reason": reason,
            "deposit_to_refund": float(lease["deposit"]),
        }
        return json.dumps(result, ensure_ascii=False, default=str)

    except Exception as e:
        logger.error(f"ยกเลิกสัญญาเช่าล้มเหลว: {e}")
        return json.dumps({"error": f"เกิดข้อผิดพลาด: {str(e)}"}, ensure_ascii=False)


async def get_all_active_leases() -> str:
    """ดึงรายการสัญญาเช่าที่มีผลบังคับใช้ทั้งหมด พร้อมรายละเอียดห้อง ผู้เช่า และวันหมดอายุ"""
    try:
        leases = await execute_query(
            """
            SELECT
                l.id, r.number as room_number, l."tenantName" as tenant_name,
                l."startDate" as start_date, l."endDate" as end_date, l."rentAmount" as monthly_rent,
                l."depositAmount" as deposit, l.status,
                (l."endDate"::date - CURRENT_DATE) as days_remaining
            FROM leases l
            JOIN rooms r ON l."roomId" = r.id
            WHERE l.status = 'ACTIVE'
            ORDER BY r.number
            """
        )

        if not leases:
            return json.dumps({
                "message": "ไม่พบสัญญาเช่าที่มีผลบังคับใช้",
                "leases": []
            }, ensure_ascii=False)

        total_rent = sum(float(l["monthly_rent"]) for l in leases)
        expiring_soon = [l for l in leases if l["days_remaining"] and l["days_remaining"] <= 30]

        result = {
            "total_active": len(leases),
            "total_monthly_rent": total_rent,
            "expiring_within_30_days": len(expiring_soon),
            "leases": [
                {
                    "id": l["id"],
                    "room_number": l["room_number"],
                    "tenant_name": l["tenant_name"],
                    "start_date": str(l["start_date"]),
                    "end_date": str(l["end_date"]),
                    "monthly_rent": float(l["monthly_rent"]),
                    "days_remaining": l["days_remaining"],
                    "auto_renew": False,
                }
                for l in leases
            ],
        }
        return json.dumps(result, ensure_ascii=False, default=str)

    except Exception as e:
        logger.error(f"ดึงสัญญาเช่าล้มเหลว: {e}")
        return json.dumps({"error": f"เกิดข้อผิดพลาด: {str(e)}"}, ensure_ascii=False)


# รวมเครื่องมือทั้งหมดเพื่อ export
LEASE_TOOLS = [
    get_lease_info,
    get_expiring_leases,
    renew_lease,
    terminate_lease,
    get_all_active_leases,
]
