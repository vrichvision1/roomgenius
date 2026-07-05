"""
โมดูลเชื่อมต่อฐานข้อมูล PostgreSQL สำหรับ RoomGenius AI Engine

ใช้ asyncpg เพื่อสร้าง connection pool แบบ async
สำหรับการเข้าถึงฐานข้อมูลจากทุก tool function
"""

import os
import asyncpg
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Singleton pool instance
_pool: Optional[asyncpg.Pool] = None


async def get_db_pool() -> asyncpg.Pool:
    """
    สร้างหรือคืนค่า connection pool สำหรับฐานข้อมูล PostgreSQL

    ใช้ environment variable DATABASE_URL เป็น connection string
    Pool จะถูกสร้างครั้งเดียวและใช้ซ้ำตลอดอายุของแอปพลิเคชัน

    Returns:
        asyncpg.Pool: Connection pool สำหรับ PostgreSQL

    Raises:
        ValueError: ถ้าไม่ได้ตั้งค่า DATABASE_URL
        asyncpg.PostgresError: ถ้าเชื่อมต่อฐานข้อมูลไม่ได้
    """
    global _pool
    if _pool is None:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise ValueError(
                "ไม่พบ DATABASE_URL ใน environment variables "
                "กรุณาตั้งค่า DATABASE_URL ก่อนเริ่มใช้งาน"
            )
        try:
            _pool = await asyncpg.create_pool(
                database_url,
                min_size=2,
                max_size=10,
                command_timeout=30,
            )
            logger.info("เชื่อมต่อฐานข้อมูลสำเร็จ")
        except Exception as e:
            logger.error(f"เชื่อมต่อฐานข้อมูลล้มเหลว: {e}")
            raise
    return _pool


async def close_db_pool() -> None:
    """
    ปิด connection pool อย่างปลอดภัย

    ควรเรียกใช้ตอนปิดแอปพลิเคชัน
    """
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None
        logger.info("ปิดการเชื่อมต่อฐานข้อมูลแล้ว")


async def execute_query(query: str, *args) -> list[dict]:
    """
    รันคำสั่ง SQL และคืนผลลัพธ์เป็น list of dict

    Args:
        query: คำสั่ง SQL ที่ต้องการรัน
        *args: พารามิเตอร์สำหรับ parameterized query

    Returns:
        list[dict]: ผลลัพธ์จากคำสั่ง SQL
    """
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(query, *args)
        return [dict(row) for row in rows]


async def execute_one(query: str, *args) -> Optional[dict]:
    """
    รันคำสั่ง SQL และคืนผลลัพธ์แถวเดียว

    Args:
        query: คำสั่ง SQL ที่ต้องการรัน
        *args: พารามิเตอร์สำหรับ parameterized query

    Returns:
        Optional[dict]: ผลลัพธ์แถวเดียว หรือ None ถ้าไม่พบ
    """
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(query, *args)
        return dict(row) if row else None


async def execute_command(query: str, *args) -> str:
    """
    รันคำสั่ง SQL ที่ไม่ต้องการผลลัพธ์ (INSERT, UPDATE, DELETE)

    Args:
        query: คำสั่ง SQL ที่ต้องการรัน
        *args: พารามิเตอร์สำหรับ parameterized query

    Returns:
        str: สถานะการรันคำสั่ง
    """
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        result = await conn.execute(query, *args)
        return result
