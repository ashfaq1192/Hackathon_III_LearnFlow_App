import { betterAuth } from "better-auth";
import { Pool } from "pg";

// Strip sslmode from connection string - we configure SSL explicitly below
const dbUrl = (process.env.DATABASE_URL || "").replace(/[?&]sslmode=[^&]*/g, "").replace(/\?$/, "");

export const auth = betterAuth({
  database: new Pool({
    connectionString: dbUrl,
    ssl: { rejectUnauthorized: false },
  }),
  secret: process.env.AUTH_SECRET,
  baseURL: process.env.BETTER_AUTH_URL || "http://localhost:3000",
  trustedOrigins: [
    "http://localhost:3000",
    "http://localhost:8080",
    "http://127.0.0.1:3000",
  ],
  emailAndPassword: {
    enabled: true,
  },
  user: {
    additionalFields: {
      role: {
        type: "string",
        defaultValue: "student",
        input: true,
      },
    },
  },
});
