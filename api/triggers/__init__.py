"""
โมดูลสำหรับตั้งค่า Background Triggers คอยกระตุ้น AI Agent ให้ตรวจเช็คตามช่วงเวลา
"""

import logging
from google.antigravity.triggers import every, TriggerContext

logger = logging.getLogger(__name__)

async def daily_rent_check(ctx: TriggerContext):
    """
    กระตุ้น AI ให้ตรวจหาผู้เช่าที่ครบกำหนดชำระเงินวันนี้ หรือใกล้กำหนดชำระ
    """
    logger.info("Trigger: daily_rent_check ทำงาน")
    await ctx.send(
        "ช่วยตรวจสอบรายการค่าเช่าที่ครบกำหนดในวันนี้ และรายการที่เกินกำหนดจ่าย "
        "หากพบให้ใช้ tool get_overdue_payments และส่งแจ้งเตือนด้วย send_rent_reminder"
    )

async def hourly_utility_monitor(ctx: TriggerContext):
    """
    กระตุ้น AI ให้ตรวจเช็คค่ามิเตอร์น้ำไฟที่ผิดปกติ
    """
    logger.info("Trigger: hourly_utility_monitor ทำงาน")
    await ctx.send(
        "ช่วยตรวจสอบค่าน้ำและค่าไฟของรอบบิลปัจจุบัน โดยตรวจเช็คความผิดปกติจากเครื่องมือ get_high_usage_alerts"
    )

async def weekly_supply_check(ctx: TriggerContext):
    """
    กระตุ้น AI ให้ตรวจเช็คสต็อกวัสดุสิ้นเปลือง
    """
    logger.info("Trigger: weekly_supply_check ทำงาน")
    await ctx.send(
        "ช่วยตรวจสอบรายการวัสดุสิ้นเปลืองที่ระดับคงคลังต่ำกว่าจุดวิกฤต โดยใช้ get_low_stock_items และรายงานความคืบหน้า"
    )

async def monthly_lease_review(ctx: TriggerContext):
    """
    กระตุ้น AI ให้ตรวจสอบสัญญาเช่าที่ใกล้หมดอายุในอีก 30 วันข้างหน้า
    """
    logger.info("Trigger: monthly_lease_review ทำงาน")
    await ctx.send(
        "ช่วยตรวจสอบสัญญาเช่าที่กำลังจะหมดอายุในอีก 30 วันข้างหน้า โดยใช้ get_expiring_leases เพื่อแจ้งเตือนและเตรียมส่งข้อมูลต่อสัญญา"
    )

async def daily_summary_report(ctx: TriggerContext):
    """
    กระตุ้น AI ให้สร้างรายงานสรุปประจำวันส่งให้เจ้าของ (Owner)
    """
    logger.info("Trigger: daily_summary_report ทำงาน")
    await ctx.send(
        "ช่วยทำรายงานสรุปประจำวันของหอพัก/คอนโด โดยใช้ get_daily_summary_data แล้วส่งข้อมูลสรุปนี้ผ่าน send_custom_notification ไปยัง Owner"
    )

# รวม triggers ทั้งหมดเพื่อนำไปใช้งาน
all_triggers = [
    every(86400, daily_rent_check),       # ทุก 24 ชั่วโมง
    every(3600, hourly_utility_monitor),   # ทุก 1 ชั่วโมง
    every(604800, weekly_supply_check),    # ทุก 7 วัน
    every(2592000, monthly_lease_review),  # ทุก 30 วัน
    every(86400, daily_summary_report),    # ทุก 24 ชั่วโมง
]
