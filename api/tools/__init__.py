"""
โมดูลรวบรวมเครื่องมือ (Tools) ทั้งหมดสำหรับ RoomGenius AI Engine
"""

from .analytics_tools import (
    get_occupancy_report,
    get_revenue_report,
    get_monthly_trends,
    get_tenant_analytics,
    get_room_list,
    get_daily_summary_data,
)
from .notification_tools import (
    send_rent_reminder,
    send_lease_expiry_notification,
    send_custom_notification,
    get_notification_history,
)
from .rent_tools import (
    get_rent_summary,
    get_overdue_payments,
    record_rent_payment,
    get_payment_history,
    generate_rent_invoices,
)
from .supply_tools import (
    get_inventory_list,
    get_low_stock_items,
    add_supply_item,
    update_supply_quantity,
    get_supply_usage_report,
)
from .lease_tools import (
    get_lease_info,
    get_expiring_leases,
    renew_lease,
    terminate_lease,
    get_all_active_leases,
)
from .utility_tools import (
    record_meter_reading,
    get_utility_bills,
    get_utility_usage_by_room,
    get_high_usage_alerts,
)

all_tools = [
    get_occupancy_report,
    get_revenue_report,
    get_monthly_trends,
    get_tenant_analytics,
    get_room_list,
    get_daily_summary_data,
    send_rent_reminder,
    send_lease_expiry_notification,
    send_custom_notification,
    get_notification_history,
    get_rent_summary,
    get_overdue_payments,
    record_rent_payment,
    get_payment_history,
    generate_rent_invoices,
    get_inventory_list,
    get_low_stock_items,
    add_supply_item,
    update_supply_quantity,
    get_supply_usage_report,
    get_lease_info,
    get_expiring_leases,
    renew_lease,
    terminate_lease,
    get_all_active_leases,
    record_meter_reading,
    get_utility_bills,
    get_utility_usage_by_room,
    get_high_usage_alerts,
]
