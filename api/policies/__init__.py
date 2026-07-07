"""
นโยบายความปลอดภัย (Safety Policies) สำหรับควบคุมการทำงานของ AI Agent
"""

from google.antigravity import policy

# นโยบายความปลอดภัยสำหรับสภาพแวดล้อม Production
production_policies = [
    # ห้ามรันคำสั่ง Shell โดยเด็ดขาด
    policy.deny("run_command"),
    
    # อนุญาตเครื่องมืออ่านข้อมูลทั่วไป
    policy.allow("get_rent_summary"),
    policy.allow("get_overdue_payments"),
    policy.allow("get_payment_history"),
    policy.allow("get_inventory_list"),
    policy.allow("get_low_stock_items"),
    policy.allow("get_supply_usage_report"),
    policy.allow("get_lease_info"),
    policy.allow("get_expiring_leases"),
    policy.allow("get_all_active_leases"),
    policy.allow("get_utility_bills"),
    policy.allow("get_utility_usage_by_room"),
    policy.allow("get_high_usage_alerts"),
    policy.allow("get_occupancy_report"),
    policy.allow("get_revenue_report"),
    policy.allow("get_monthly_trends"),
    policy.allow("get_tenant_analytics"),
    policy.allow("get_room_list"),
    policy.allow("get_daily_summary_data"),
    policy.allow("get_notification_history"),
    
    # อนุญาตเครื่องมือทำงานที่มีผลกระทบต่อข้อมูล (เปลี่ยนจาก ask_user เป็น allow เพื่อความสะดวกในการใช้งานบนเว็บแอป)
    policy.allow("record_rent_payment"),
    policy.allow("generate_rent_invoices"),
    policy.allow("renew_lease"),
    policy.allow("terminate_lease"),
    policy.allow("record_meter_reading"),
    policy.allow("add_supply_item"),
    policy.allow("update_supply_quantity"),
    policy.allow("send_rent_reminder"),
    policy.allow("send_lease_expiry_notification"),
    policy.allow("send_custom_notification"),
]
