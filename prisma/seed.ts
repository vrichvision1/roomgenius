import { PrismaClient, Plan, PropertyType, RoomType, RoomStatus, LeaseStatus, RentType, PaymentType, PaymentMethod, PaymentStatus, UtilityType, MaintenancePriority, MaintenanceStatus } from '@prisma/client';
import { PrismaPg } from '@prisma/adapter-pg';
import pg from 'pg';
import { addDays, subDays } from 'date-fns';

const connectionString = process.env.DATABASE_URL || 'postgresql://roomgenius:roomgenius_secret@localhost:5432/roomgenius_db';
const pool = new pg.Pool({ connectionString });
const adapter = new PrismaPg(pool);
const prisma = new PrismaClient({ adapter });

async function main() {
  console.log('กำลังเริ่มต้นเคลียร์ข้อมูลเก่า...');
  
  // ลบข้อมูลเก่าก่อนเพื่อป้องกันความซ้ำซ้อน
  await prisma.$executeRawUnsafe(`TRUNCATE TABLE tenants CASCADE;`);

  console.log('เริ่มสร้างข้อมูลสำหรับทดลองใช้งาน (Seed Data)...');

  // 1. สร้าง Tenant (SaaS Organization)
  const tenant = await prisma.tenant.create({
    data: {
      name: 'หอพักสุขใจ กรุ๊ป',
      slug: 'sukjai',
      plan: Plan.PROFESSIONAL,
      trialEndsAt: addDays(new Date(), 14),
      isActive: true,
    },
  });

  // 2. สร้าง User (Owner)
  const owner = await prisma.user.create({
    data: {
      email: 'owner@sukjai.com',
      name: 'สมศักดิ์ รักบริการ',
      role: 'OWNER',
      tenantId: tenant.id,
      isActive: true,
    },
  });

  // 3. สร้าง Property (โครงการหอพักและคอนโด)
  const hostel = await prisma.property.create({
    data: {
      name: 'แสนสุข อพาร์ทเม้นท์',
      type: PropertyType.APARTMENT,
      address: '123/45 ถนนพหลโยธิน แขวงสามเสนใน เขตพญาไท กรุงเทพฯ 10400',
      phone: '081-234-5678',
      totalRooms: 10,
      totalFloors: 3,
      waterRate: 18.0,
      electricRate: 8.0,
      commonAreaFee: 200.0,
      rentDueDay: 5,
      tenantId: tenant.id,
    },
  });

  // 4. สร้าง Rooms (ห้องพักประเภทต่างๆ)
  const roomData = [
    { number: '101', floor: 1, type: RoomType.STANDARD, status: RoomStatus.OCCUPIED, monthlyRate: 5000 },
    { number: '102', floor: 1, type: RoomType.STANDARD, status: RoomStatus.OCCUPIED, monthlyRate: 5000 },
    { number: '103', floor: 1, type: RoomType.STANDARD, status: RoomStatus.VACANT, monthlyRate: 5000 },
    { number: '201', floor: 2, type: RoomType.DELUXE, status: RoomStatus.OCCUPIED, monthlyRate: 6500 },
    { number: '202', floor: 2, type: RoomType.DELUXE, status: RoomStatus.OCCUPIED, monthlyRate: 6500 },
    { number: '203', floor: 2, type: RoomType.DELUXE, status: RoomStatus.OCCUPIED, monthlyRate: 6500 }, // เคสค้างชำระ
    { number: '204', floor: 2, type: RoomType.STANDARD, status: RoomStatus.VACANT, monthlyRate: 5000 },
    { number: '301', floor: 3, type: RoomType.SUITE, status: RoomStatus.OCCUPIED, monthlyRate: 8500 },
    { number: '302', floor: 3, type: RoomType.SUITE, status: RoomStatus.OCCUPIED, monthlyRate: 8500 }, // เคสรอชำระ
    { number: '303', floor: 3, type: RoomType.DELUXE, status: RoomStatus.MAINTENANCE, monthlyRate: 6500 }, // เคสแจ้งซ่อม
  ];

  const rooms = [];
  for (const r of roomData) {
    const room = await prisma.room.create({
      data: {
        number: r.number,
        floor: r.floor,
        type: r.type,
        status: r.status,
        monthlyRate: r.monthlyRate,
        dailyRate: r.monthlyRate / 20, // คำนวณรายวันคร่าวๆ
        amenities: { wifi: true, aircon: r.type !== RoomType.STANDARD, furniture: true },
        propertyId: hostel.id,
      },
    });
    rooms.push(room);
  }

  // ดึง references ของห้องบางส่วนเพื่อทำธุรกรรมเช่า
  const room101 = rooms.find(r => r.number === '101')!;
  const room201 = rooms.find(r => r.number === '201')!;
  const room203 = rooms.find(r => r.number === '203')!;
  const room302 = rooms.find(r => r.number === '302')!;

  // 5. สร้าง Leases (สัญญาเช่า)
  const lease101 = await prisma.lease.create({
    data: {
      startDate: subDays(new Date(), 90),
      endDate: addDays(new Date(), 270),
      rentType: RentType.MONTHLY,
      rentAmount: 5000,
      depositAmount: 10000,
      status: LeaseStatus.ACTIVE,
      tenantName: 'สมชาย มีสุข',
      tenantPhone: '089-111-2222',
      tenantEmail: 'somchai@gmail.com',
      tenantIdCard: '1234567890123',
      roomId: room101.id,
    },
  });

  const lease201 = await prisma.lease.create({
    data: {
      startDate: subDays(new Date(), 60),
      endDate: addDays(new Date(), 300),
      rentType: RentType.MONTHLY,
      rentAmount: 6500,
      depositAmount: 13000,
      status: LeaseStatus.ACTIVE,
      tenantName: 'วิภา แสงทอง',
      tenantPhone: '089-333-4444',
      tenantEmail: 'wipa@gmail.com',
      roomId: room201.id,
    },
  });

  const lease203 = await prisma.lease.create({
    data: {
      startDate: subDays(new Date(), 180),
      endDate: addDays(new Date(), 180),
      rentType: RentType.MONTHLY,
      rentAmount: 6500,
      depositAmount: 13000,
      status: LeaseStatus.ACTIVE,
      tenantName: 'ธนพล รักเรียน',
      tenantPhone: '089-555-6666',
      tenantEmail: 'thanapon@gmail.com',
      roomId: room203.id,
    },
  });

  const lease302 = await prisma.lease.create({
    data: {
      startDate: subDays(new Date(), 30),
      endDate: addDays(new Date(), 330),
      rentType: RentType.MONTHLY,
      rentAmount: 8500,
      depositAmount: 17000,
      status: LeaseStatus.ACTIVE,
      tenantName: 'จิราพร ใจดี',
      tenantPhone: '089-777-8888',
      tenantEmail: 'jiraporn@gmail.com',
      roomId: room302.id,
    },
  });

  // 6. สร้าง Payments (การจ่ายเงิน)
  // ห้อง 101: จ่ายของเดือน ก.ค. แล้ว
  await prisma.payment.create({
    data: {
      amount: 5500, // ค่าห้อง + ค่าน้ำไฟ
      type: PaymentType.RENT,
      method: PaymentMethod.PROMPTPAY,
      status: PaymentStatus.PAID,
      dueDate: subDays(new Date(), 1),
      paidDate: subDays(new Date(), 1),
      leaseId: lease101.id,
    },
  });

  // ห้อง 201: จ่ายแล้ว
  await prisma.payment.create({
    data: {
      amount: 7200,
      type: PaymentType.RENT,
      method: PaymentMethod.TRANSFER,
      status: PaymentStatus.PAID,
      dueDate: subDays(new Date(), 1),
      paidDate: subDays(new Date(), 2),
      leaseId: lease201.id,
    },
  });

  // ห้อง 203: ค้างชำระ (Overdue)
  await prisma.payment.create({
    data: {
      amount: 7300,
      type: PaymentType.RENT,
      status: PaymentStatus.OVERDUE,
      dueDate: subDays(new Date(), 3), // เกินกำหนดมา 3 วัน
      leaseId: lease203.id,
    },
  });

  // ห้อง 302: รอชำระ (Pending)
  await prisma.payment.create({
    data: {
      amount: 9200,
      type: PaymentType.RENT,
      status: PaymentStatus.PENDING,
      dueDate: addDays(new Date(), 2), // เหลือเวลา 2 วัน
      leaseId: lease302.id,
    },
  });

  // 7. สร้าง UtilityReadings (มิเตอร์น้ำ/ไฟ)
  await prisma.utilityReading.create({
    data: {
      type: UtilityType.ELECTRIC,
      previousReading: 1200,
      currentReading: 1350,
      unitsUsed: 150,
      ratePerUnit: 8.0,
      totalAmount: 1200,
      readingDate: subDays(new Date(), 5),
      billingPeriod: '2026-07',
      roomId: room101.id,
    },
  });

  await prisma.utilityReading.create({
    data: {
      type: UtilityType.WATER,
      previousReading: 320,
      currentReading: 335,
      unitsUsed: 15,
      ratePerUnit: 18.0,
      totalAmount: 270,
      readingDate: subDays(new Date(), 5),
      billingPeriod: '2026-07',
      roomId: room101.id,
    },
  });

  // 8. สร้าง SupplyItems (วัสดุสิ้นเปลือง)
  await prisma.supplyItem.create({
    data: {
      name: 'กระดาษทิชชู่ม้วนใหญ่',
      category: 'ห้องน้ำ',
      unit: 'ม้วน',
      currentStock: 2, // ต่ำกว่าขั้นต่ำ
      minimumStock: 5,
      costPerUnit: 25.0,
      supplier: 'ร้านค้าส่งพญาไท',
      autoReorder: true,
      reorderQuantity: 10,
      propertyId: hostel.id,
    },
  });

  await prisma.supplyItem.create({
    data: {
      name: 'สบู่อาบน้ำเหลว (แกลลอน)',
      category: 'ห้องน้ำ',
      unit: 'แกลลอน',
      currentStock: 6, // ปกติ
      minimumStock: 3,
      costPerUnit: 120.0,
      supplier: 'ร้านค้าส่งพญาไท',
      autoReorder: false,
      propertyId: hostel.id,
    },
  });

  // 9. สร้าง MaintenanceRequests (แจ้งซ่อม)
  await prisma.maintenanceRequest.create({
    data: {
      title: 'น้ำรั่วซึมจากก๊อกฝักบัว',
      description: 'ก๊อกฝักบัวในห้องน้ำปิดไม่สนิท มีน้ำหยดซึมตลอดเวลา ทำให้พื้นเปียกตลอดเวลาและสิ้นเปลืองน้ำ',
      priority: MaintenancePriority.MEDIUM,
      status: MaintenanceStatus.OPEN,
      category: 'ประปา',
      roomNumber: '303',
      propertyId: hostel.id,
    },
  });

  console.log('Seeding ข้อมูลตัวอย่างทดลองใช้เสร็จเรียบร้อย! 🎉');
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
