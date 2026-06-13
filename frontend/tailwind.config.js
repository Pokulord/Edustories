export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,html}",
  ],
  theme: {
    extend: {
      fontFamily: {
        medieval: ['"Cormorant Garamond"', 'serif'],
      },
      boxShadow: {
        gold: "0 0 25px rgba(212,175,55,0.35)",
      },
      backgroundImage: {
        hero: "url('/images/hero-bg.jpg')",
      },
    },
  },
  plugins: [],
}