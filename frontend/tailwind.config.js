/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        ink: '#0A0A0A',
        paper: '#FFFFFF',
        mist: '#F7F7F5',
        smoke: '#E8E8E6',
        ash: '#6B6B6B',
        silver: '#999999',
      },
      fontFamily: {
        serif: ['"Noto Sans SC"', '"DM Sans"', 'system-ui', 'sans-serif'],
        sans: ['"Noto Sans SC"', '"DM Sans"', 'system-ui', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      boxShadow: {
        line: '0 1px 0 0 #0A0A0A',
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-out forwards',
        'slide-up': 'slideUp 0.5s ease-out forwards',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(12px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
    },
  },
  plugins: [],
}
