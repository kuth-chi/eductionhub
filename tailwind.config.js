/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html', 
    './static/**/*.{js,jsx,ts,tsx,html}', 
    './node_modules/flowbite/**/*.js'
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {"50":"#eff6ff","100":"#dbeafe","200":"#bfdbfe","300":"#93c5fd","400":"#60a5fa","500":"#3b82f6","600":"#2563eb","700":"#1d4ed8","800":"#1e40af","900":"#1e3a8a","950":"#172554"}
      },
      backgroundImage: {
        'morning-gradient': 'linear-gradient(to right, #FFD700, #FF8C00)',
        'afternoon-gradient': 'linear-gradient(to right, #FF4500, #FF6347)',
        'evening-gradient': 'linear-gradient(to right, #FFA500, #DC143C)',
        'night-gradient': 'linear-gradient(to right, #000080, #191970)',
      },
      
    },
    fontFamily: {
      'localization': [
        'Battambang-Regular', 
        'Khmer-Regular', 
        'sans-serif', 
        'Inter', 
        'Monospace', 
        '-apple-system', 
        'Segoe UI', 'system-ui', 
        'Roboto', 'Arial', 
        'Noto Sans', 
        'FreeSans', 
        'Apple Color Emoji', 
        'Segoe UI Emoji', 
        'Segoe UI Symbol', 
        'Noto Color Emoji',

      ], 
      'body': [
        'Inter', 
        'ui-sans-serif', 
        'system-ui', 
        '-apple-system', 
        'system-ui', 
        'Segoe UI', 
        'Roboto', 
        'Helvetica Neue', 
        'Arial', 
        'Noto Sans', 
        'sans-serif', 
        'Apple Color Emoji', 
        'Segoe UI Emoji', 
        'Segoe UI Symbol', 
        'Noto Color Emoji',
        'Battambang-Regular',
        'Khmer-Regular',
      ],
      'sans': [
        'Inter', 
        'ui-sans-serif', 
        'system-ui', 
        '-apple-system', 
        'system-ui', 
        'Segoe UI', 
        'Roboto', 
        'Helvetica Neue', 
        'Arial', 
        'Noto Sans', 
        'sans-serif', 
        'Apple Color Emoji', 
        'Segoe UI Emoji', 
        'Segoe UI Symbol', 
        'Noto Color Emoji',
        'serif',
        'Khmer-Regular',
      ]
    },
  },
  plugins: [
    require('flowbite/plugin')({
      charts: true,
      datatables: true,
  }),
  ],
}

