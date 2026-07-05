import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "RoomGenius AI — ระบบจัดการห้องเช่าอัจฉริยะ",
  description: "ระบบจัดการอสังหาริมทรัพย์ขับเคลื่อนด้วย AI หลายค่าย (Gemini, ChatGPT, Claude) พร้อมแจ้งเตือนอัตโนมัติ วิเคราะห์ข้อมูล จัดการสัญญา ค่าน้ำ ค่าไฟ วัสดุสิ้นเปลือง",
  keywords: ["property management", "AI", "hostel", "condo", "apartment", "rental", "จัดการห้องเช่า", "ระบบหอพัก"],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="th" data-theme="dark">
      <body>{children}</body>
    </html>
  );
}
