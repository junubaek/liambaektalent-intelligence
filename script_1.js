
        tailwind.config = {
            theme: {
                extend: {
                    fontFamily: { sans: ['Inter', 'sans-serif'] },
                    animation: {
                        'fade-in': 'fadeIn 0.2s ease-out forwards',
                        'slide-up': 'slideUp 0.3s cubic-bezier(0, 0, 0.2, 1) forwards',
                        'pulse-subtle': 'pulseSubtle 2s infinite ease-in-out',
                    },
                    keyframes: {
                        fadeIn: { 'from': { opacity: '0' }, 'to': { opacity: '1' } },
                        slideUp: { 'from': { transform: 'translateY(8px)', opacity: '0' }, 'to': { transform: 'translateY(0)', opacity: '1' } },
                        pulseSubtle: { '0%, 100%': { opacity: '1' }, '50%': { opacity: '0.5' } }
                    }
                }
            }
        }
    