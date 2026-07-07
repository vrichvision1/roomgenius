"""
เครื่องมือวิเคราะห์และรายงานสำหรับ RoomGenius AI (ปรับปรุงตาม Schema จริง)
"""

import json
import logging
from datetime import date, datetime
from typing import Optional

from db import execute_query, execute_one

logger = logging.getLogger(__name__)


async def get_occupancy_report() -> str:
    """สร้างรายงานอัตราการเข้าพักทั้งหมด รวมถึงจำนวนห้องว่าง ห้องมีผู้เช่า ห้องซ่อมบำรุง"""
    try:
        rooms = await execute_query(
            """
            SELECT
                status,
                COUNT(*) as count
            FROM rooms
            GROUP BY status
            """
        )

        if not rooms:
            return json.dumps({"message": "ไม่พบข้อมูลห้องพัก"}, ensure_ascii=False)

        status_map = {r["status"]: r["count"] for r in rooms}
        total = sum(r["count"] for r in rooms)
        occupied = status_map.get("OCCUPIED", 0)
        vacant = status_map.get("VACANT", 0)
        maintenance = status_map.get("MAINTENANCE", 0)

        # ระยะเวลาเฉลี่ยที่พัก คำนวณจาก Leases
        avg_stay = await execute_one(
            """
            SELECT AVG(
                EXTRACT(EPOCH FROM (COALESCE("endDate", CURRENT_DATE) - "startDate")) / 2592000
            ) as avg_months
            FROM leases
            WHERE "startDate" IS NOT NULL
            """
        )

        result = {
            "total_rooms": total,
            "occupied_rooms": occupied,
            "vacant_rooms": vacant,
            "maintenance_rooms": maintenance,
            "reserved_rooms": status_map.get("RESERVED", 0),
            "occupancy_rate": round((occupied / total * 100) if total > 0 else 0, 2),
            "average_stay_months": round(float(avg_stay["avg_months"]), 1) if avg_stay and avg_stay["avg_months"] else None,
        }
        return json.dumps(result, ensure_ascii=False, default=str)

    except Exception as e:
        logger.error(f"สร้างรายงานอัตราเข้าพักล้มเหลว: {e}")
        return json.dumps({"error": f"เกิดข้อผิดพลาด: {str(e)}"}, ensure_ascii=False)


async def get_revenue_report(month: str) -> str:
    """สร้างรายงานรายได้ประจำเดือน รวมค่าเช่า ค่าน้ำค่าไฟ ค่าใช้จ่าย และกำไรสุทธิ

    Args:
        month: เดือนที่ต้องการ ในรูปแบบ YYYY-MM เช่น 2026-07
    """
    try:
        # รายได้จากค่าเช่า
        rent_income = await execute_one(
            """
            SELECT COALESCE(SUM(amount), 0) as total
            FROM payments
            WHERE status = 'PAID'
                AND to_char("dueDate", 'YYYY-MM') = $1 AND type = 'RENT'
            """,
            month,
        )

        # รายได้จากค่าน้ำค่าไฟ
        utility_income = await execute_one(
            """
            SELECT COALESCE(SUM("totalAmount"), 0) as total
            FROM utility_readings
            WHERE "billingPeriod" = $1
            """,
            month,
        )

        # ค่าใช้จ่าย (จำลองจากคลังพัสดุ เนื่องจากไม่มี supply_log)
        expenses = await execute_one(
            """
            SELECT COALESCE(SUM("currentStock" * "costPerUnit"), 0) * 0.15 as total
            FROM supply_items
            """
        )

        # เปรียบเทียบกับเดือนก่อน
        prev_month_parts = month.split("-")
        prev_year = int(prev_month_parts[0])
        prev_month_num = int(prev_month_parts[1]) - 1
        if prev_month_num == 0:
            prev_month_num = 12
            prev_year -= 1
        prev_month = f"{prev_year:04d}-{prev_month_num:02d}"

        prev_rent = await execute_one(
            """
            SELECT COALESCE(SUM(amount), 0) as total
            FROM payments
            WHERE status = 'PAID'
                AND to_char("dueDate", 'YYYY-MM') = $1 AND type = 'RENT'
            """,
            prev_month,
        )

        rent = float(rent_income["total"]) if rent_income else 0
        utility = float(utility_income["total"]) if utility_income else 0
        expense = float(expenses["total"]) if expenses else 0
        total_income = rent + utility
        net_income = total_income - expense

        prev_total = float(prev_rent["total"]) if prev_rent else 0
        growth = round(((rent - prev_total) / prev_total * 100) if prev_total > 0 else 0, 2)

        result = {
            "month": month,
            "rent_income": rent,
            "utility_income": utility,
            "other_income": 0,
            "total_income": total_income,
            "expenses": expense,
            "net_income": net_income,
            "growth_percent": growth,
            "previous_month_rent": prev_total,
        }
        return json.dumps(result, ensure_ascii=False, default=str)

    except Exception as e:
        logger.error(f"สร้างรายงานรายได้ล้มเหลว: {e}")
        return json.dumps({"error": f"เกิดข้อผิดพลาด: {str(e)}"}, ensure_ascii=False)


async def get_monthly_trends(months: int = 6) -> str:
    """วิเคราะห์แนวโน้มรายได้และอัตราเข้าพักย้อนหลังหลายเดือน สำหรับดูภาพรวมธุรกิจ

    Args:
        months: จำนวนเดือนย้อนหลัง (ค่าเริ่มต้น 6 เดือน)
    """
    try:
        trends = await execute_query(
            """
            SELECT
                to_char("dueDate", 'YYYY-MM') as month,
                COUNT(*) as total_invoices,
                SUM(CASE WHEN status = 'PAID' THEN 1 ELSE 0 END) as paid_count,
                COALESCE(SUM(CASE WHEN status = 'PAID' THEN amount ELSE 0 END), 0) as collected,
                COALESCE(SUM(amount), 0) as expected
            FROM payments
            WHERE "dueDate" >= CURRENT_DATE - ($1 || ' months')::interval AND type = 'RENT'
            GROUP BY to_char("dueDate", 'YYYY-MM')
            ORDER BY month DESC
            """,
            str(months),
        )

        if not trends:
            return json.dumps({
                "message": f"ไม่พบข้อมูลแนวโน้มในช่วง {months} เดือน",
                "trends": []
            }, ensure_ascii=False)

        result = {
            "period_months": months,
            "trends": [
                {
                    "month": t["month"],
                    "total_invoices": t["total_invoices"],
                    "paid_count": t["paid_count"],
                    "collected": float(t["collected"]),
                    "expected": float(t["expected"]),
                    "collection_rate": round(
                        float(t["collected"]) / float(t["expected"]) * 100
                        if float(t["expected"]) > 0 else 0, 2
                    ),
                }
                for t in trends
            ],
        }
        return json.dumps(result, ensure_ascii=False, default=str)

    except Exception as e:
        logger.error(f"วิเคราะห์แนวโน้มล้มเหลว: {e}")
        return json.dumps({"error": f"เกิดข้อผิดพลาด: {str(e)}"}, ensure_ascii=False)


async def get_tenant_analytics() -> str:
    """วิเคราะห์ข้อมูลผู้เช่า รวมถึงจำนวนผู้เช่าทั้งหมด ผู้เช่าใหม่ ย้ายออก และอัตราการคงอยู่"""
    try:
        # สรุปผู้เช่าจาก Leases
        summary = await execute_one(
            """
            SELECT
                COUNT(*) FILTER (WHERE status = 'ACTIVE') as active_tenants,
                COUNT(*) FILTER (WHERE status = 'TERMINATED') as moved_out,
                COUNT(*) FILTER (
                    WHERE status = 'ACTIVE'
                    AND "startDate" >= CURRENT_DATE - interval '30 days'
                ) as new_this_month,
                COUNT(*) FILTER (
                    WHERE status = 'TERMINATED'
                    AND "endDate" >= CURRENT_DATE - interval '30 days'
                ) as left_this_month
            FROM leases
            """
        )

        # อายุเฉลี่ยการเช่า
        avg_tenure = await execute_one(
            """
            SELECT AVG(
                EXTRACT(EPOCH FROM (CURRENT_DATE - "startDate")) / 2592000
            ) as avg_months
            FROM leases
            WHERE status = 'ACTIVE' AND "startDate" IS NOT NULL
            """
        )

        # ผู้เช่าที่ค้างชำระบ่อย
        problem_tenants = await execute_query(
            """
            SELECT
                l."tenantName" as name, r.number as room_number,
                COUNT(*) as overdue_count
            FROM payments p
            JOIN leases l ON p."leaseId" = l.id
            JOIN rooms r ON l."roomId" = r.id
            WHERE p.status = 'OVERDUE'
            GROUP BY l."tenantName", r.number
            HAVING COUNT(*) >= 1
            ORDER BY overdue_count DESC
            LIMIT 10
            """
        )

        result = {
            "active_tenants": summary["active_tenants"] if summary else 0,
            "moved_out_total": summary["moved_out"] if summary else 0,
            "new_this_month": summary["new_this_month"] if summary else 0,
            "left_this_month": summary["left_this_month"] if summary else 0,
            "average_tenure_months": round(
                float(avg_tenure["avg_months"]), 1
            ) if avg_tenure and avg_tenure["avg_months"] else 0,
            "problem_tenants": [
                {
                    "name": p["name"],
                    "room_number": p["room_number"],
                    "overdue_count": p["overdue_count"],
                }
                for p in problem_tenants
            ] if problem_tenants else [],
        }
        return json.dumps(result, ensure_ascii=False, default=str)

    except Exception as e:
        logger.error(f"วิเคราะห์ผู้เช่าล้มเหลว: {e}")
        return json.dumps({"error": f"เกิดข้อผิดพลาด: {str(e)}"}, ensure_ascii=False)


async def get_room_list(status: Optional[str] = None) -> str:
    """ดึงรายการห้องพักทั้งหมด สามารถกรองตามสถานะได้

    Args:
        status: สถานะห้องที่ต้องการกรอง เช่น OCCUPIED, VACANT, MAINTENANCE หรือ None เพื่อดูทั้งหมด
    """
    try:
        status_db = status.upper() if status else None
        if status_db:
            rooms = await execute_query(
                """
                SELECT
                    r.id, r.number as room_number, r.floor, r.type as room_type,
                    r."monthlyRate" as monthly_rent, r.status,
                    l."tenantName" as tenant_name
                FROM rooms r
                LEFT JOIN leases l ON l."roomId" = r.id AND l.status = 'ACTIVE'
                WHERE r.status = $1
                ORDER BY r.number
                """,
                status_db,
            )
        else:
            rooms = await execute_query(
                """
                SELECT
                    r.id, r.number as room_number, r.floor, r.type as room_type,
                    r."monthlyRate" as monthly_rent, r.status,
                    l."tenantName" as tenant_name
                FROM rooms r
                LEFT JOIN leases l ON l."roomId" = r.id AND l.status = 'ACTIVE'
                ORDER BY r.number
                """
            )

        if not rooms:
            return json.dumps({"message": "ไม่พบข้อมูลห้องพัก", "rooms": []}, ensure_ascii=False)

        result = {
            "total_rooms": len(rooms),
            "rooms": [
                {
                    "id": r["id"],
                    "room_number": r["room_number"],
                    "floor": r["floor"],
                    "room_type": r.get("room_type"),
                    "monthly_rent": float(r["monthly_rent"]) if r["monthly_rent"] else 0.0,
                    "status": r["status"],
                    "tenant_name": r["tenant_name"],
                }
                for r in rooms
            ],
        }
        return json.dumps(result, ensure_ascii=False, default=str)

    except Exception as e:
        logger.error(f"ดึงรายการห้องพักล้มเหลว: {e}")
        return json.dumps({"error": f"เกิดข้อผิดพลาด: {str(e)}"}, ensure_ascii=False)


async def get_daily_summary_data() -> str:
    """สร้างสรุปข้อมูลประจำวัน รวมค่าเช่าที่เก็บได้ รายการค้างชำระ สัญญาใกล้หมด สิ่งของใกล้หมด"""
    try:
        # ค่าเช่าที่เก็บได้วันนี้
        today_rent = await execute_one(
            """
            SELECT COALESCE(SUM(amount), 0) as total
            FROM payments
            WHERE "paidDate"::date = CURRENT_DATE AND status = 'PAID'
            """
        )

        # รายการรอชำระ
        pending = await execute_one(
            "SELECT COUNT(*) as cnt FROM payments WHERE status = 'PENDING'"
        )

        # รายการค้างชำระ
        overdue = await execute_one(
            """
            SELECT COUNT(*) as cnt FROM payments
            WHERE status = 'OVERDUE'
                OR (status = 'PENDING' AND "dueDate" < CURRENT_DATE)
            """
        )

        # ผู้เช่าใหม่วันนี้ (Lease เริ่มต้นวันนี้)
        new_tenants = await execute_one(
            """
            SELECT COUNT(*) as cnt FROM leases
            WHERE "startDate"::date = CURRENT_DATE AND status = 'ACTIVE'
            """
        )

        # ย้ายออกวันนี้
        move_outs = await execute_one(
            """
            SELECT COUNT(*) as cnt FROM leases
            WHERE "endDate"::date = CURRENT_DATE AND status = 'TERMINATED'
            """
        )

        # งานซ่อมรอดำเนินการ
        maintenance = await execute_one(
            """
            SELECT COUNT(*) as cnt FROM maintenance_requests
            WHERE status IN ('OPEN', 'IN_PROGRESS')
            """
        )

        # สิ่งของใกล้หมด
        low_stock = await execute_one(
            "SELECT COUNT(*) as cnt FROM supply_items WHERE \"currentStock\" <= \"minimumStock\""
        )

        # สัญญาใกล้หมด (30 วัน)
        expiring = await execute_one(
            """
            SELECT COUNT(*) as cnt FROM leases
            WHERE status = 'ACTIVE'
                AND "endDate" <= CURRENT_DATE + interval '30 days'
                AND "endDate" >= CURRENT_DATE
            """
        )

        # อัตราเข้าพัก
        occupancy = await execute_one(
            """
            SELECT
                COUNT(*) as total,
                COUNT(*) FILTER (WHERE status = 'OCCUPIED') as occupied
            FROM rooms
            """
        )

        total_rooms = occupancy["total"] if occupancy else 1
        occupied = occupancy["occupied"] if occupancy else 0

        # สร้าง alerts
        alerts = []
        if overdue and overdue["cnt"] > 0:
            alerts.append(f"⚠️ มี {overdue['cnt']} ห้องค้างชำระค่าเช่า")
        if expiring and expiring["cnt"] > 0:
            alerts.append(f"📋 มี {expiring['cnt']} สัญญาใกล้หมดอายุ")
        if low_stock and low_stock["cnt"] > 0:
            alerts.append(f"📦 มี {low_stock['cnt']} รายการสิ่งของใกล้หมด")
        if maintenance and maintenance["cnt"] > 0:
            alerts.append(f"🔧 มี {maintenance['cnt']} งานซ่อมรอดำเนินการ")

        result = {
            "date": str(date.today()),
            "rent_collected_today": float(today_rent["total"]) if today_rent else 0,
            "pending_payments": pending["cnt"] if pending else 0,
            "overdue_payments": overdue["cnt"] if overdue else 0,
            "new_tenants": new_tenants["cnt"] if new_tenants else 0,
            "move_outs": move_outs["cnt"] if move_outs else 0,
            "maintenance_pending": maintenance["cnt"] if maintenance else 0,
            "low_stock_items": low_stock["cnt"] if low_stock else 0,
            "leases_expiring_soon": expiring["cnt"] if expiring else 0,
            "occupancy_rate": round((occupied / total_rooms * 100) if total_rooms > 0 else 0, 2),
            "alerts": alerts,
        }
        return json.dumps(result, ensure_ascii=False, default=str)

    except Exception as e:
        logger.error(f"สร้างสรุปรายวันล้มเหลว: {e}")
        return json.dumps({"error": f"เกิดข้อผิดพลาด: {str(e)}"}, ensure_ascii=False)


# รวมเครื่องมือทั้งหมดเพื่อ export
ANALYTICS_TOOLS = [
    get_occupancy_report,
    get_revenue_report,
    get_monthly_trends,
    get_tenant_analytics,
    get_room_list,
    get_daily_summary_data,
]
