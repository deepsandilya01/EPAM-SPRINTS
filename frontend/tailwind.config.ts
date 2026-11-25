import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/features/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ["var(--font-geist-sans)", "Inter", "system-ui", "sans-serif"],
        mono: ["var(--font-geist-mono)", "ui-monospace", "SFMono-Regular", "monospace"],
      },
      colors: {
        canvas: "#F5F5F5",
        surface: "#FFFFFF",
        ink: {
          DEFAULT: "#171717",
          muted: "#777777",
        },
        carbon: {
          950: "#111111",
          900: "#181818",
          800: "#222222",
        },
        hairline: "#E5E5E5",
        status: {
          feasible: "#166534",
          "feasible-bg": "#F0FDF4",
          "feasible-border": "#BBF7D0",
          breached: "#991B1B",
          "breached-bg": "#FEF2F2",
          "breached-border": "#FECACA",
          critical: "#3F3F46",
          "critical-bg": "#F4F4F5",
          "critical-border": "#D4D4D8",
        },
      },
    },
  },
  plugins: [],
};

export default config;
