import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        paper: "#F4F5F3",
        ink: "#14231F",
        rule: "#D8D4C8",
        accent: {
          DEFAULT: "#3D6B52",
          soft: "#E4ECE7",
        },
        watch: {
          DEFAULT: "#B8863B",
          soft: "#F5EBD9",
        },
        concern: {
          DEFAULT: "#A8432F",
          soft: "#F3E1DB",
        },
      },
      fontFamily: {
        display: ["'Fraunces'", "serif"],
        body: ["'Inter'", "sans-serif"],
        mono: ["'IBM Plex Mono'", "monospace"],
      },
    },
  },
  plugins: [],
};
export default config;