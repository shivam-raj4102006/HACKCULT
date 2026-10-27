/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        heritage: {
          50: '#fbf8f3',
          100: '#f5efe4',
          200: '#ebdeca',
          300: '#dec7a9',
          400: '#cfab84',
          500: '#c29265',
          600: '#b47e55',
          700: '#966445',
          800: '#7a513b',
          900: '#644332',
        }
      }
    },
  },
  plugins: [],
}
