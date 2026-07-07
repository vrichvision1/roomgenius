"""
เครื่องมือส่งแจ้งเตือนสำหรับ RoomGenius AI

รวมฟังก์ชันสำหรับส่งแจ้งเตือนผ่านช่องทางต่างๆ
ได้แก่ LINE, SMS, อีเมล และแจ้งเตือนในระบบ
"""

import json
import logging
from datetime import datetime
from typing import Optional

from db import execute_query, execute_one, execute_command

logger = logging.getLogger(__name__)


async def send_rent_reminder(room_number: Optional[str] = None) -> str:
    """ส่งแจ้งเตือนค่าเช่าให้ผู้เช่าที่ยังไม่ชำระ ระบุห้องเพื่อแจ้งเฉพาะห้อง หรือไม่ระบุเพื่อแจ้งทุกห้อง

    Args:
        room_number: หมายเลขห้อง (ถ้าไม่ระบุจะแจ้งทุกห้องที่ค้างชำระ)
    """
    try:
        if room_number:
            unpaid = await execute_query(
                """
                SELECT
                    r.room_number, t.name, t.phone, t.email,
                    rp.amount, rp.due_date,
                    CURRENT_DATE - rp.due_date as days_overdue
                FROM rent_payments rp
                JOIN rooms r ON rp.room_id = r.id
                JOIN tenants t ON rp.tenant_id = t.id
                WHERE r.room_number = $1
                    AND rp.status IN ('unpaid', 'overdue')
                ORDER BY rp.due_date
                """,
                room_number,
            )
        else:
            unpaid = await execute_query(
                """
                SELECT
                    r.room_number, t.name, t.phone, t.email,
                    rp.amount, rp.due_date,
                    CURRENT_DATE - rp.due_date as days_overdue
                FROM rent_payments rp
                JOIN rooms r ON rp.room_id = r.id
                JOIN tenants t ON rp.tenant_id = t.id
                WHERE rp.status IN ('unpaid', 'overdue')
                ORDER BY rp.due_date
                """
            )

        if not unpaid:
            return json.dumps({
                "status": "ok",
                "message": "ไม่มีผู้เช่าที่ต้องแจ้งเตือน ทุกห้องชำระครบแล้ว"
            }, ensure_ascii=False)

        # บันทึกการแจ้งเตือนลงฐานข้อมูล
        notifications_sent = []
        for tenant in unpaid:
            days = tenant["days_overdue"] if tenant["days_overdue"] else 0
            if days > 0:
                msg = (
                    f"แจ้งเตือน: ห้อง {tenant['room_number']} "
                    f"คุณ{tenant['name']} ค้างชำระค่าเช่า {tenant['amount']:,.2f} บาท "
                    f"เกินกำหนด {days} วัน กรุณาชำระโดยด่วน"
                )
                notif_type = "rent_overdue"
            else:
                msg = (
                    f"แจ้งเตือน: ห้อง {tenant['room_number']} "
                    f"คุณ{tenant['name']} ค่าเช่า {tenant['amount']:,.2f} บาท "
                    f"ครบกำหนดวันที่ {tenant['due_date']} กรุณาชำระภายในกำหนด"
                )
                notif_type = "rent_due"

            await execute_command(
                """
                INSERT INTO notifications (type, recipient_name, room_number,
                    message, channel, sent_at, created_at)
                VALUES ($1, $2, $3, $4, 'system', NOW(), NOW())
                """,
                notif_type,
                tenant["name"],
                tenant["room_number"],
                msg,
            )

            notifications_sent.append({
                "room_number": tenant["room_number"],
                "tenant_name": tenant["name"],
                "message": msg,
                "type": notif_type,
            })

        result = {
            "status": "success",
            "message": f"ส่งแจ้งเตือนค่าเช่าให้ {len(notifications_sent)} ห้อง",
            "notifications_count": len(notifications_sent),
            "notifications": notifications_sent,
        }
        return json.dumps(result, ensure_ascii=False, default=str)

    except Exception as e:
        logger.error(f"ส่งแจ้งเตือนค่าเช่าล้มเหลว: {e}")
        return json.dumps({"error": f"เกิดข้อผิดพลาด: {str(e)}"}, ensure_ascii=False)


async def send_lease_expiry_notification(days_before: int = 30) -> str:
    """ส่งแจ้งเตือนให้ผู้เช่าที่สัญญาเช่าใกล้หมดอายุ

    Args:
        days_before: จำนวนวันก่อนหมดอายุที่ต้องการแจ้งเตือน (ค่าเริ่มต้น 30 วัน)
    """
    try:
        expiring = await execute_query(
            """
            SELECT
                r.room_number, t.name, t.phone, t.email,
                l.end_date, l.monthly_rent,
                (l.end_date - CURRENT_DATE) as days_remaining
            FROM leases l
            JOIN rooms r ON l.room_id = r.id
            JOIN tenants t ON l.tenant_id = t.id
            WHERE l.status = 'active'
                AND l.end_date <= CURRENT_DATE + ($1 || ' days')::interval
                AND l.end_date >= CURRENT_DATE
            ORDER BY l.end_date ASC
            """,
            str(days_before),
        )

        if not expiring:
            return json.dumps({
                "status": "ok",
                "message": f"ไม่มีสัญญาเช่าที่จะหมดอายุภายใน {days_before} วัน"
            }, ensure_ascii=False)

        notifications_sent = []
        for tenant in expiring:
            msg = (
                f"แจ้งเตือน: สัญญาเช่าห้อง {tenant['room_number']} "
                f"ของคุณ{tenant['name']} จะหมดอายุในวันที่ {tenant['end_date']} "
                f"(อีก {tenant['days_remaining']} วัน) "
                f"กรุณาติดต่อเพื่อต่อสัญญา"
            )

            await execute_command(
                """
                INSERT INTO notifications (type, recipient_name, room_number,
                    message, channel, sent_at, created_at)
                VALUES ('lease_expiring', $1, $2, $3, 'system', NOW(), NOW())
                """,
                tenant["name"],
                tenant["room_number"],
                msg,
            )

            notifications_sent.append({
                "room_number": tenant["room_number"],
                "tenant_name": tenant["name"],
                "days_remaining": tenant["days_remaining"],
                "message": msg,
            })

        result = {
            "status": "success",
            "message": f"ส่งแจ้งเตือนสัญญาใกล้หมดให้ {len(notifications_sent)} ห้อง",
            "notifications_count": len(notifications_sent),
            "notifications": notifications_sent,
        }
        return json.dumps(result, ensure_ascii=False, default=str)

    except Exception as e:
        logger.error(f"ส่งแจ้งเตือนสัญญาหมดอายุล้มเหลว: {e}")
        return json.dumps({"error": f"เกิดข้อผิดพลาด: {str(e)}"}, ensure_ascii=False)


async def send_custom_notification(
    room_number: str,
    message: str,
    notification_type: str = "general",
) -> str:
    """ส่งข้อความแจ้งเตือนที่กำหนดเองให้ผู้เช่าห้องที่ระบุ

    Args:
        room_number: หมายเลขห้องที่ต้องการส่ง
        message: ข้อความที่ต้องการส่ง
        notification_type: ประเภทแจ้งเตือน เช่น general, maintenance, utility_high
    """
    try:
        tenant = await execute_one(
            """
            SELECT t.name, t.phone, t.email
            FROM tenants t
            JOIN rooms r ON t.room_id = r.id
            WHERE r.room_number = $1 AND t.status = 'active'
            """,
            room_number,
        )

        if not tenant:
            return json.dumps({
                "error": f"ไม่พบผู้เช่าห้อง {room_number}"
            }, ensure_ascii=False)

        full_message = f"ถึงคุณ{tenant['name']} (ห้อง {room_number}): {message}"

        await execute_command(
            """
            INSERT INTO notifications (type, recipient_name, room_number,
                message, channel, sent_at, created_at)
            VALUES ($1, $2, $3, $4, 'system', NOW(), NOW())
            """,
            notification_type,
            tenant["name"],
            room_number,
            full_message,
        )

        result = {
            "status": "success",
            "message": f"ส่งแจ้งเตือนให้คุณ{tenant['name']} ห้อง {room_number} สำเร็จ",
            "notification_type": notification_type,
            "recipient": tenant["name"],
            "room_number": room_number,
            "full_message": full_message,
        }
        return json.dumps(result, ensure_ascii=False, default=str)

    except Exception as e:
        logger.error(f"ส่งแจ้งเตือนล้มเหลว: {e}")
        return json.dumps({"error": f"เกิดข้อผิดพลาด: {str(e)}"}, ensure_ascii=False)


async def get_notification_history(
    room_number: Optional[str] = None,
    limit: int = 20,
) -> str:
    """ดึงประวัติการแจ้งเตือนทั้งหมด สามารถกรองตามห้องได้

    Args:
        room_number: หมายเลขห้อง (ถ้าไม่ระบุจะดูทั้งหมด)
        limit: จำนวนรายการสูงสุดที่ต้องการ (ค่าเริ่มต้น 20)
    """
    try:
        if room_number:
            notifications = await execute_query(
                """
                SELECT type, recipient_name, room_number, message,
                       channel, sent_at
                FROM notifications
                WHERE room_number = $1
                ORDER BY sent_at DESC
                LIMIT $2
                """,
                room_number,
                limit,
            )
        else:
            notifications = await execute_query(
                """
                SELECT type, recipient_name, room_number, message,
                       channel, sent_at
                FROM notifications
                ORDER BY sent_at DESC
                LIMIT $1
                """,
                limit,
            )

        if not notifications:
            return json.dumps({
                "message": "ไม่พบประวัติการแจ้งเตือน",
                "notifications": []
            }, ensure_ascii=False)

        result = {
            "total": len(notifications),
            "notifications": [
                {
                    "type": n["type"],
                    "recipient_name": n["recipient_name"],
                    "room_number": n["room_number"],
                    "message": n["message"],
                    "channel": n["channel"],
                    "sent_at": str(n["sent_at"]),
                }
                for n in notifications
            ],
        }
        return json.dumps(result, ensure_ascii=False, default=str)

    except Exception as e:
        logger.error(f"ดึงประวัติแจ้งเตือนล้มเหลว: {e}")
        return json.dumps({"error": f"เกิดข้อผิดพลาด: {str(e)}"}, ensure_ascii=False)


# รวมเครื่องมือทั้งหมดเพื่อ export
NOTIFICATION_TOOLS = [
    send_rent_reminder,
    send_lease_expiry_notification,
    send_custom_notification,
    get_notification_history,
]
