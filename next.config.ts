import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/python/:path*",
        destination:
          process.env.NODE_ENV === "development"
            ? "http://127.0.0.1:8765/api/python/:path*"
            : "/api/python/:path*",
      },
    ];
  },
};

export default nextConfig;
