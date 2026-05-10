import { MiniKitConfig } from "@coinbase/minikit";
const config: MiniKitConfig = {
  appName: "Base Scout",
  appUrl: process.env.NEXT_PUBLIC_APP_URL || "https://base-scout.vercel.app",
};
export default config;
