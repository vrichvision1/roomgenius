import { defineConfig } from 'prisma/config';

export default defineConfig({
  schema: 'prisma/schema.prisma',
  datasource: {
    url: process.env.DATABASE_URL || 'postgresql://roomgenius:roomgenius_secret@localhost:5432/roomgenius_db',
  },
});
