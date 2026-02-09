import { betterAuth } from "better-auth";
import { Pool } from "pg";

export const auth = betterAuth({
  database: new Pool({
    connectionString: process.env.DATABASE_URL,
  }),
  secret: process.env.AUTH_SECRET,
  baseURL: process.env.BETTER_AUTH_URL || "http://localhost:8080",
  trustedOrigins: [
    "http://localhost:8080",
    "http://localhost:3000",
    "http://127.0.0.1:8080",
  ],
  emailAndPassword: {
    enabled: true,
  },
  // OAuth providers - uncomment when credentials are available:
  // socialProviders: {
  //   google: {
  //     clientId: process.env.GOOGLE_CLIENT_ID!,
  //     clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
  //   },
  //   github: {
  //     clientId: process.env.GITHUB_CLIENT_ID!,
  //     clientSecret: process.env.GITHUB_CLIENT_SECRET!,
  //   },
  // },
});
