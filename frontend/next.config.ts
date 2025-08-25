import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  // Disable the Next.js development indicator
  devIndicators: {
    buildActivity: false,
    position: 'bottom-right',
  },
};

export default nextConfig;
