export default {
  darkMode: "class",
  content: [
    "./*.html",
    "./src/**/*.{js,ts,html}",
  ],
  theme: {
    extend: {
      fontFamily: {
        // Вариант 1: Классический фэнтези
        "heading-classic": ['"Cormorant"', 'serif'],
        "body-classic":    ['"PT Serif"', 'serif'],

        // Вариант 2: Летописный
        "heading-chronicle": ['"Ruslan Display"', 'cursive'],
        "quote-chronicle":   ['"Neucha"', 'cursive'],
        "body-chronicle":    ['"Alegreya"', 'serif'],

        // Вариант 3: Строгий
        "heading-noble": ['"Playfair Display"', 'serif'],
        "body-noble":    ['"Lora"', 'serif'],
      },
      boxShadow: {
        gold: "0 0 25px rgba(212,175,55,0.35)",
      },
      backgroundImage: {
        hero: "url('/images/hero-bg.jpg')",
      },
      colors: {
        'gold': '#c5a67c',
        'gold-bright': '#d4b483',
        'gold-muted': 'rgba(197, 166, 124, 0.12)',
        'dark': '#050a0a',
      },
    },
  },
  plugins: [],
}