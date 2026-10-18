/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./pages/**/*.{js,ts,jsx,tsx}', './components/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: { midnight: '#111e35', stone: '#efede8', crimson: '#b52943', paper: '#faf9f6' },
      fontFamily: { sans: ['Arial', 'Helvetica', 'sans-serif'] }
    }
  },
  plugins: []
};
