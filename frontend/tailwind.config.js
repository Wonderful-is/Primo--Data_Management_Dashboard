/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,jsx}",
    "./components/**/*.{js,jsx}",
  ],
  theme: {
    extend: {
      colors: {
        primo: {
          900: "#0B2545",
          700: "#13315C",
          500: "#1F4E79",
          100: "#E8EEF7",
        },
      },
    },
  },
  plugins: [],
};
