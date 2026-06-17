/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        "surface-variant": "#e1e2e4",
        "primary-fixed-dim": "#b6c4ff",
        "on-surface": "#191c1e",
        "on-primary": "#ffffff",
        "primary": "#00236f",
        "surface-container-low": "#f3f4f6",
        "background": "#f8f9fb",
        "on-surface-variant": "#444651",
        "outline-variant": "#c5c5d3",
        "secondary-container": "#6cf8bb",
        "secondary": "#006c49",
        "outline": "#757682",
        "surface-container-lowest": "#ffffff",
      },
      spacing: {
        "section-gap": "5rem",
        "container-max": "1280px",
        "margin-desktop": "2.5rem",
        "gutter": "1.5rem"
      },
      fontFamily: {
        "body-md": ["Inter", "sans-serif"],
        "headline-md": ["Inter", "sans-serif"],
      }
    },
  },
  plugins: [],
}