"""
เครื่องมือจัดการสิ่งของและคลังพัสดุสำหรับ RoomGenius AI (ปรับปรุงตาม Schema จริง)
"""

import json
import logging
import uuid
from datetime import date, datetime
from typing import Optional

from db import execute_query, execute_one, execute_command

logger = logging.getLogger(__name__)


async def get_inventory_list(category: Optional[str] = None) -> str:
    """ดึงรายการสิ่งของทั้งหมดในคลังพัสดุ สามารถกรองตามหมวดหมู่ได้

    Args:
        category: หมวดหมู่ที่ต้องการกรอง เช่น cleaning, toiletries, electrical, plumbing, furniture, kitchen หรือ None เพื่อดูทั้งหมด
    """
    try:
        if category:
            items = await execute_query(
                """
                SELECT
                    id, name, category, "currentStock" as quantity, "minimumStock" as min_quantity,
                    unit, "costPerUnit" as unit_cost, "lastRestocked" as last_restocked,
                    ("currentStock" <= "minimumStock") as needs_restock
                FROM supply_items
                WHERE category = $1
                ORDER BY name
                """,
                category,
            )
        else:
            items = await execute_query(
                """
                SELECT
                    id, name, category, "currentStock" as quantity, "minimumStock" as min_quantity,
                    unit, "costPerUnit" as unit_cost, "lastRestocked" as last_restocked,
                    ("currentStock" <= "minimumStock") as needs_restock
                FROM supply_items
                ORDER BY category, name
                """
            )

        if not items:
            msg = f"ไม่พบสิ่งของในหมวด {category}" if category else "ไม่พบสิ่งของในคลัง"
            return json.dumps({"message": msg, "items": []}, ensure_ascii=False)

        needs_restock = [i for i in items if i["needs_restock"]]

        result = {
            "total_items": len(items),
            "needs_restock_count": len(needs_restock),
            "items": [
                {
                    "id": i["id"],
                    "name": i["name"],
                    "category": i["category"],
                    "quantity": i["quantity"],
                    "min_quantity": i["min_quantity"],
                    "unit": i["unit"],
                    "unit_cost": float(i["unit_cost"]),
                    "last_restocked": str(i["last_restocked"]) if i["last_restocked"] else None,
                    "needs_restock": i["needs_restock"],
                }
                for i in items
            ],
        }
        return json.dumps(result, ensure_ascii=False, default=str)

    except Exception as e:
        logger.error(f"ดึงรายการสิ่งของล้มเหลว: {e}")
        return json.dumps({"error": f"เกิดข้อผิดพลาด: {str(e)}"}, ensure_ascii=False)


async def get_low_stock_items() -> str:
    """ดึงรายการสิ่งของที่จำนวนคงเหลือน้อยกว่าหรือเท่ากับจำนวนขั้นต่ำ ต้องเติมสต็อกด่วน"""
    try:
        items = await execute_query(
            """
            SELECT
                id, name, category, "currentStock" as quantity, "minimumStock" as min_quantity,
                unit, "costPerUnit" as unit_cost,
                ("minimumStock" - "currentStock") as deficit
            FROM supply_items
            WHERE "currentStock" <= "minimumStock"
            ORDER BY ("minimumStock" - "currentStock") DESC
            """
        )

        if not items:
            return json.dumps({
                "status": "ok",
                "message": "สิ่งของทุกรายการมีเพียงพอ ไม่ต้องเติมสต็อก 🎉",
                "items": []
            }, ensure_ascii=False)

        total_restock_cost = sum(
            (i["min_quantity"] * 2 - i["quantity"]) * float(i["unit_cost"])
            for i in items
        )

        result = {
            "status": "warning",
            "message": f"มี {len(items)} รายการที่ต้องเติมสต็อก",
            "estimated_restock_cost": round(total_restock_cost, 2),
            "items": [
                {
                    "id": i["id"],
                    "name": i["name"],
                    "category": i["category"],
                    "quantity": i["quantity"],
                    "min_quantity": i["min_quantity"],
                    "unit": i["unit"],
                    "deficit": i["deficit"],
                    "unit_cost": float(i["unit_cost"]),
                }
                for i in items
            ],
        }
        return json.dumps(result, ensure_ascii=False, default=str)

    except Exception as e:
        logger.error(f"ดึงสิ่งของใกล้หมดล้มเหลว: {e}")
        return json.dumps({"error": f"เกิดข้อผิดพลาด: {str(e)}"}, ensure_ascii=False)


async def add_supply_item(
    name: str,
    category: str,
    quantity: int,
    min_quantity: int,
    unit: str,
    unit_cost: float,
) -> str:
    """เพิ่มรายการสิ่งของใหม่เข้าคลังพัสดุ

    Args:
        name: ชื่อสิ่งของ เช่น "น้ำยาถูพื้น"
        category: หมวดหมู่ ได้แก่ cleaning, toiletries, electrical, plumbing, furniture, kitchen, other
        quantity: จำนวนเริ่มต้น
        min_quantity: จำนวนขั้นต่ำที่ต้องมี (ถ้าน้อยกว่านี้จะแจ้งเตือน)
        unit: หน่วยนับ เช่น "ขวด", "แพ็ค", "ชิ้น"
        unit_cost: ราคาต่อหน่วย (บาท)
    """
    try:
        # ค้นหาว่ามีอยู่แล้วหรือไม่
        existing = await execute_one(
            "SELECT id FROM supply_items WHERE LOWER(name) = LOWER($1)", name
        )
        if existing:
            return json.dumps({
                "status": "exists",
                "message": f"มี \"{name}\" อยู่ในคลังแล้ว (ID: {existing['id']})"
            }, ensure_ascii=False)

        # ค้นหา propertyId แรกในระบบเพื่อตั้งค่า
        prop = await execute_one("SELECT id FROM properties LIMIT 1")
        if not prop:
            return json.dumps({"error": "ไม่พบข้อมูลโครงการ/อาคารเช่าในระบบ"}, ensure_ascii=False)

        new_id = f"sup_{uuid.uuid4().hex[:16]}"
        await execute_command(
            """
            INSERT INTO supply_items 
                (id, name, category, "currentStock", "minimumStock", unit, "costPerUnit",
                 "lastRestocked", "propertyId", "createdAt", "updatedAt")
            VALUES ($1, $2, $3, $4, $5, $6, $7, CURRENT_DATE, $8, NOW(), NOW())
            """,
            new_id, name, category, quantity, min_quantity, unit, unit_cost, prop["id"]
        )

        return json.dumps({
            "status": "success",
            "message": f"เพิ่ม \"{name}\" เข้าคลังสำเร็จ จำนวน {quantity} {unit}",
            "name": name,
            "category": category,
            "quantity": quantity,
        }, ensure_ascii=False)

    except Exception as e:
        logger.error(f"เพิ่มสิ่งของล้มเหลว: {e}")
        return json.dumps({"error": f"เกิดข้อผิดพลาด: {str(e)}"}, ensure_ascii=False)


async def update_supply_quantity(
    item_name: str,
    quantity_change: int,
    reason: str = "",
) -> str:
    """อัปเดตจำนวนสิ่งของในคลัง (เพิ่มหรือลดจำนวน) ใช้ค่าบวกเมื่อเติมสต็อก ค่าลบเมื่อใช้ไป

    Args:
        item_name: ชื่อสิ่งของที่ต้องการอัปเดต
        quantity_change: จำนวนที่เปลี่ยนแปลง (บวก = เพิ่ม, ลบ = ลด)
        reason: เหตุผลที่เปลี่ยนแปลง เช่น "ซื้อเพิ่ม" หรือ "ใช้ทำความสะอาดห้อง 101"
    """
    try:
        item = await execute_one(
            "SELECT id, name, \"currentStock\" as quantity, unit FROM supply_items WHERE LOWER(name) LIKE LOWER($1)",
            f"%{item_name}%",
        )
        if not item:
            return json.dumps({"error": f"ไม่พบสิ่งของ \"{item_name}\""}, ensure_ascii=False)

        new_quantity = item["quantity"] + quantity_change
        if new_quantity < 0:
            return json.dumps({
                "error": f"จำนวนไม่เพียงพอ คงเหลือ {item['quantity']} {item['unit']} "
                         f"แต่ต้องการใช้ {abs(quantity_change)} {item['unit']}"
            }, ensure_ascii=False)

        # อัปเดตจำนวน
        last_restocked_clause = ', "lastRestocked" = CURRENT_DATE' if quantity_change > 0 else ""
        await execute_command(
            f"""
            UPDATE supply_items
            SET "currentStock" = $1, "updatedAt" = NOW() {last_restocked_clause}
            WHERE id = $2
            """,
            new_quantity,
            item["id"],
        )

        action = "เพิ่ม" if quantity_change > 0 else "ใช้"
        return json.dumps({
            "status": "success",
            "message": f"{action} \"{item['name']}\" {abs(quantity_change)} {item['unit']} "
                       f"คงเหลือ {new_quantity} {item['unit']}",
            "item_name": item["name"],
            "quantity_change": quantity_change,
            "new_quantity": new_quantity,
            "reason": reason,
        }, ensure_ascii=False)

    except Exception as e:
        logger.error(f"อัปเดตจำนวนสิ่งของล้มเหลว: {e}")
        return json.dumps({"error": f"เกิดข้อผิดพลาด: {str(e)}"}, ensure_ascii=False)


async def get_supply_usage_report(months: int = 3) -> str:
    """สร้างรายงานการใช้สิ่งของย้อนหลัง เพื่อวิเคราะห์แนวโน้มและวางแผนงบประมาณ

    Args:
        months: จำนวนเดือนย้อนหลังที่ต้องการดู (ค่าเริ่มต้น 3 เดือน)
    """
    return json.dumps({
        "status": "ok",
        "message": "ระบบเก็บประวัติการใช้พัสดุแบบย่อ ปัจจุบันไม่มีประวัติประมวลผลย้อนหลัง",
        "usage": []
    }, ensure_ascii=False)


# รวมเครื่องมือทั้งหมดเพื่อ export
SUPPLY_TOOLS = [
    get_inventory_list,
    get_low_stock_items,
    add_supply_item,
    update_supply_quantity,
    get_supply_usage_report,
]
