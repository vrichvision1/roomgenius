"""
เครื่องมือจัดการค่าน้ำค่าไฟสำหรับ RoomGenius AI (ปรับปรุงตาม Schema จริง)
"""

import json
import logging
import uuid
from datetime import date, datetime
from typing import Optional

from db import execute_query, execute_one, execute_command

logger = logging.getLogger(__name__)


async def record_meter_reading(
    room_number: str,
    utility_type: str,
    current_reading: float,
    reading_date: str,
) -> str:
    """บันทึกเลขมิเตอร์น้ำหรือไฟของห้องที่ระบุ ระบบจะคำนวณหน่วยที่ใช้โดยอัตโนมัติ

    Args:
        room_number: หมายเลขห้อง เช่น "101"
        utility_type: ประเภทมิเตอร์ ได้แก่ "water" (น้ำ) หรือ "electric" (ไฟ)
        current_reading: เลขมิเตอร์ปัจจุบัน
        reading_date: วันที่จดมิเตอร์ ในรูปแบบ YYYY-MM-DD
    """
    try:
        # ค้นหาห้อง
        room = await execute_one(
            "SELECT id, \"propertyId\" FROM rooms WHERE number = $1", room_number
        )
        if not room:
            return json.dumps({"error": f"ไม่พบห้อง {room_number}"}, ensure_ascii=False)

        type_db = utility_type.upper()  # WATER หรือ ELECTRIC

        # ดึงเลขมิเตอร์ครั้งก่อน
        previous = await execute_one(
            """
            SELECT "currentReading", "readingDate"
            FROM utility_readings
            WHERE "roomId" = $1 AND type = $2
            ORDER BY "readingDate" DESC
            LIMIT 1
            """,
            room["id"],
            type_db,
        )

        previous_reading = previous["currentReading"] if previous else 0

        # ดึงอัตราค่าน้ำ/ไฟจาก Property
        rates = await execute_one(
            """
            SELECT "waterRate", "electricRate"
            FROM properties
            WHERE id = $1
            """,
            room["propertyId"],
        )
        
        if rates:
            rate_per_unit = rates["waterRate"] if utility_type == "water" else rates["electricRate"]
        else:
            rate_per_unit = 18.0 if utility_type == "water" else 8.0

        units_used = current_reading - previous_reading
        if units_used < 0:
            return json.dumps({
                "error": f"เลขมิเตอร์ปัจจุบัน ({current_reading}) น้อยกว่าครั้งก่อน ({previous_reading}) "
                         f"กรุณาตรวจสอบอีกครั้ง"
            }, ensure_ascii=False)

        total_amount = units_used * rate_per_unit
        read_date = datetime.strptime(reading_date, "%Y-%m-%d").date()
        billing_period = reading_date[:7]  # YYYY-MM

        # ตรวจสอบรายการซ้ำของเดือนนี้
        existing = await execute_one(
            """
            SELECT id FROM utility_readings
            WHERE "roomId" = $1 AND type = $2 AND "billingPeriod" = $3
            """,
            room["id"],
            type_db,
            billing_period,
        )

        new_id = f"utr_{uuid.uuid4().hex[:16]}"

        if existing:
            # อัปเดตข้อมูล
            await execute_command(
                """
                UPDATE utility_readings
                SET "previousReading" = $1, "currentReading" = $2,
                    "unitsUsed" = $3, "ratePerUnit" = $4, "totalAmount" = $5,
                    "readingDate" = $6, "createdAt" = NOW()
                WHERE id = $7
                """,
                previous_reading,
                current_reading,
                units_used,
                rate_per_unit,
                total_amount,
                read_date,
                existing["id"],
            )
        else:
            # บันทึกลงฐานข้อมูล
            await execute_command(
                """
                INSERT INTO utility_readings
                    (id, type, "previousReading", "currentReading", "unitsUsed",
                     "ratePerUnit", "totalAmount", "readingDate", "billingPeriod", "roomId", "createdAt")
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, NOW())
                """,
                new_id,
                type_db,
                previous_reading,
                current_reading,
                units_used,
                rate_per_unit,
                total_amount,
                read_date,
                billing_period,
                room["id"],
            )

        type_label = "ค่าน้ำ" if utility_type == "water" else "ค่าไฟ"
        return json.dumps({
            "status": "success",
            "message": f"บันทึก{type_label}ห้อง {room_number} สำเร็จ",
            "room_number": room_number,
            "utility_type": utility_type,
            "previous_reading": previous_reading,
            "current_reading": current_reading,
            "units_used": units_used,
            "rate_per_unit": rate_per_unit,
            "total_cost": total_amount,
            "reading_date": reading_date,
        }, ensure_ascii=False)

    except Exception as e:
        logger.error(f"บันทึกมิเตอร์ล้มเหลว: {e}")
        return json.dumps({"error": f"เกิดข้อผิดพลาด: {str(e)}"}, ensure_ascii=False)


async def get_utility_bills(month: str) -> str:
    """ดึงสรุปค่าน้ำค่าไฟทุกห้องของเดือนที่ระบุ พร้อมยอดรวม

    Args:
        month: เดือนที่ต้องการดู ในรูปแบบ YYYY-MM เช่น 2026-07
    """
    try:
        bills = await execute_query(
            """
            SELECT
                r.number as room_number,
                l."tenantName" as tenant_name,
                COALESCE(SUM(CASE WHEN ur.type = 'WATER' THEN ur."totalAmount" END), 0) as water_cost,
                COALESCE(SUM(CASE WHEN ur.type = 'ELECTRIC' THEN ur."totalAmount" END), 0) as electric_cost,
                COALESCE(SUM(ur."totalAmount"), 0) as total_cost
            FROM rooms r
            LEFT JOIN leases l ON l."roomId" = r.id AND l.status = 'ACTIVE'
            LEFT JOIN utility_readings ur ON ur."roomId" = r.id AND ur."billingPeriod" = $1
            WHERE r.status = 'OCCUPIED'
            GROUP BY r.number, l."tenantName"
            ORDER BY r.number
            """,
            month,
        )

        if not bills:
            return json.dumps({
                "message": f"ไม่พบข้อมูลค่าน้ำค่าไฟสำหรับเดือน {month}",
                "bills": []
            }, ensure_ascii=False)

        total_water = sum(b["water_cost"] for b in bills)
        total_electric = sum(b["electric_cost"] for b in bills)
        grand_total = sum(b["total_cost"] for b in bills)

        result = {
            "month": month,
            "total_rooms": len(bills),
            "total_water_cost": total_water,
            "total_electric_cost": total_electric,
            "grand_total": grand_total,
            "bills": [
                {
                    "room_number": b["room_number"],
                    "tenant_name": b["tenant_name"] or "ว่าง",
                    "water_cost": float(b["water_cost"]),
                    "electric_cost": float(b["electric_cost"]),
                    "total_cost": float(b["total_cost"]),
                }
                for b in bills
            ],
        }
        return json.dumps(result, ensure_ascii=False, default=str)

    except Exception as e:
        logger.error(f"ดึงค่าน้ำค่าไฟล้มเหลว: {e}")
        return json.dumps({"error": f"เกิดข้อผิดพลาด: {str(e)}"}, ensure_ascii=False)


async def get_utility_usage_by_room(room_number: str, months: int = 6) -> str:
    """ดึงข้อมูลการใช้น้ำและไฟของห้องที่ระบุ ย้อนหลังตามจำนวนเดือน สำหรับวิเคราะห์แนวโน้มการใช้งาน

    Args:
        room_number: หมายเลขห้อง เช่น "101"
        months: จำนวนเดือนย้อนหลัง (ค่าเริ่มต้น 6 เดือน)
    """
    try:
        readings = await execute_query(
            """
            SELECT
                ur.type as utility_type, ur."billingPeriod" as month,
                ur."previousReading" as previous_reading, ur."currentReading" as current_reading,
                ur."unitsUsed" as units_used, ur."ratePerUnit" as rate_per_unit, ur."totalAmount" as total_cost,
                ur."readingDate" as reading_date
            FROM utility_readings ur
            JOIN rooms r ON ur."roomId" = r.id
            WHERE r.number = $1
            ORDER BY ur."readingDate" DESC
            LIMIT $2
            """,
            room_number,
            months * 2,  # น้ำ + ไฟ ต่อเดือน
        )

        if not readings:
            return json.dumps({
                "message": f"ไม่พบข้อมูลการใช้น้ำ/ไฟของห้อง {room_number}",
                "readings": []
            }, ensure_ascii=False)

        # แยกข้อมูลน้ำกับไฟ
        water_readings = [r for r in readings if r["utility_type"] == "WATER"]
        electric_readings = [r for r in readings if r["utility_type"] == "ELECTRIC"]

        avg_water = (
            sum(r["units_used"] for r in water_readings) / len(water_readings)
            if water_readings else 0
        )
        avg_electric = (
            sum(r["units_used"] for r in electric_readings) / len(electric_readings)
            if electric_readings else 0
        )

        result = {
            "room_number": room_number,
            "average_water_units": round(avg_water, 2),
            "average_electric_units": round(avg_electric, 2),
            "readings": [
                {
                    "utility_type": "water" if r["utility_type"] == "WATER" else "electric",
                    "month": r["month"],
                    "units_used": float(r["units_used"]),
                    "total_cost": float(r["total_cost"]),
                    "reading_date": str(r["reading_date"]),
                }
                for r in readings
            ],
        }
        return json.dumps(result, ensure_ascii=False, default=str)

    except Exception as e:
        logger.error(f"ดึงข้อมูลการใช้น้ำ/ไฟล้มเหลว: {e}")
        return json.dumps({"error": f"เกิดข้อผิดพลาด: {str(e)}"}, ensure_ascii=False)


async def get_high_usage_alerts(month: str, threshold_percent: float = 50.0) -> str:
    """ตรวจสอบห้องที่มีการใช้น้ำ/ไฟผิดปกติสูงกว่าค่าเฉลี่ย ใช้สำหรับตรวจจับการรั่วไหลหรือใช้งานมากเกินไป

    Args:
        month: เดือนที่ต้องการตรวจสอบ ในรูปแบบ YYYY-MM
        threshold_percent: เปอร์เซ็นต์ที่เกินค่าเฉลี่ยถือว่าสูงผิดปกติ (ค่าเริ่มต้น 50%)
    """
    try:
        alerts = await execute_query(
            """
            WITH avg_usage AS (
                SELECT
                    type,
                    AVG("unitsUsed") as avg_units
                FROM utility_readings
                WHERE "billingPeriod" >= to_char(CURRENT_DATE - interval '6 months', 'YYYY-MM')
                GROUP BY type
            )
            SELECT
                r.number as room_number, l."tenantName" as tenant_name,
                ur.type as utility_type, ur."unitsUsed" as units_used,
                au.avg_units,
                ROUND(((ur."unitsUsed" - au.avg_units) / NULLIF(au.avg_units, 0) * 100)::numeric, 2) as percent_above_avg
            FROM utility_readings ur
            JOIN rooms r ON ur."roomId" = r.id
            LEFT JOIN leases l ON l."roomId" = r.id AND l.status = 'ACTIVE'
            JOIN avg_usage au ON au.type = ur.type
            WHERE ur."billingPeriod" = $1
                AND ur."unitsUsed" > au.avg_units * (1 + $2 / 100.0)
            ORDER BY percent_above_avg DESC
            """,
            month,
            threshold_percent,
        )

        if not alerts:
            return json.dumps({
                "status": "normal",
                "message": f"ไม่พบการใช้น้ำ/ไฟผิดปกติในเดือน {month}",
                "alerts": []
            }, ensure_ascii=False)

        result = {
            "status": "warning",
            "month": month,
            "threshold_percent": threshold_percent,
            "alert_count": len(alerts),
            "alerts": [
                {
                    "room_number": a["room_number"],
                    "tenant_name": a["tenant_name"] or "ไม่ทราบ",
                    "utility_type": "ค่าน้ำ" if a["utility_type"] == "WATER" else "ค่าไฟ",
                    "units_used": float(a["units_used"]),
                    "average_units": float(a["avg_units"]),
                    "percent_above_avg": float(a["percent_above_avg"]),
                }
                for a in alerts
            ],
        }
        return json.dumps(result, ensure_ascii=False, default=str)

    except Exception as e:
        logger.error(f"ตรวจสอบการใช้น้ำ/ไฟผิดปกติล้มเหลว: {e}")
        return json.dumps({"error": f"เกิดข้อผิดพลาด: {str(e)}"}, ensure_ascii=False)


# รวมเครื่องมือทั้งหมดเพื่อ export
UTILITY_TOOLS = [
    record_meter_reading,
    get_utility_bills,
    get_utility_usage_by_room,
    get_high_usage_alerts,
]
