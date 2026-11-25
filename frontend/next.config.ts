import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  async rewrites() {
    return [
      { source: "/dashboard", destination: "/" },
      { source: "/simulation", destination: "/" },
      { source: "/overview", destination: "/" },
      { source: "/settings", destination: "/" },
    ];
  },
};

export default nextConfig;
