module.exports = {
  darkMode: 'class', 
  content: [
    '../templates/**/*.html',
    '../../templates/**/*.html',
    '../../core/**/templates/**/*.html',
    '../../assets/**/*.js',
  ],
  theme: {
    extend: {
      fontFamily: {
        medieval: ['"Cormorant Garamond"', 'serif'],
      },
      boxShadow: {
        gold: '0 0 25px rgba(212,175,55,0.35)',
      },
      backgroundImage: {
        hero: "url('/static/images/hero-bg.png')",
        wedya: "url('/static/images/wedya.jpg')",
      },
    },
  },
  plugins: [],
}