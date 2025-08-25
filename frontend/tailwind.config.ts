import type { Config } from "tailwindcss";

export default {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: 'class', // Enable class-based dark mode
  theme: {
    extend: {
      colors: {
        background: "#F9FAFB", // Light gray background
        foreground: "#111827", // Dark charcoal text
        card: "#FFFFFF", // Pure white for cards/panels
        border: "#E5E7EB", // Subtle borders
        accent: "#4F46E5", // Strong indigo accent
        "accent-hover": "#4338CA", // Darker indigo for hover
        muted: "#6B7280", // Muted text
        "muted-foreground": "#9CA3AF", // Even more muted text
        // Dark mode colors
        dark: {
          background: "#0F172A", // Dark slate background
          foreground: "#F8FAFC", // Light text
          card: "#1E293B", // Dark card background
          border: "#334155", // Dark borders
          muted: "#94A3B8", // Muted text in dark mode
        }
      },
      fontFamily: {
        sans: [
          "Inter",
          "-apple-system",
          "BlinkMacSystemFont",
          "Segoe UI",
          "Roboto",
          "sans-serif",
        ],
        mono: [
          "Fira Code",
          "JetBrains Mono",
          "Monaco",
          "Consolas",
          "monospace",
        ],
      },
      boxShadow: {
        soft: "0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)",
        medium: "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
      },
    },
  },
  plugins: [require('@tailwindcss/typography')],
} satisfies Config; 