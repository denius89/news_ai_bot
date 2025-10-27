/** @type {import('tailwindcss').Config} */
module.exports = {
    darkMode: ['class'],
    content: [
        './pages/**/*.{ts,tsx}',
        './components/**/*.{ts,tsx}',
        './app/**/*.{ts,tsx}',
        './src/**/*.{ts,tsx}',
    ],
    theme: {
        container: {
            center: true,
            padding: '2rem',
            screens: {
                '2xl': '1400px',
            },
        },
        extend: {
            screens: {
                'xs': '390px',    // iPhone 15 Pro и меньше
            },
            fontSize: {
                'xxs': '0.625rem',   // 10px - для очень мелких элементов
                'xxxs': '0.6875rem', // 11px - для метаданных
            },
            fontFamily: {
                sans: ['Inter', 'system-ui', 'sans-serif'],
            },
            colors: {
                // PulseAI v2 NeoGlass Design Tokens
                bg: 'var(--color-bg)',
                surface: 'var(--color-surface)',
                surfaceAlt: 'var(--color-surface-alt)',
                text: 'var(--color-text)',
                muted: 'var(--color-text-muted)',
                border: 'var(--color-border)',
                primary: {
                    DEFAULT: 'var(--color-primary)',
                    700: 'var(--color-primary-700)',
                    900: 'var(--color-primary-900)',
                },
                accent: {
                    DEFAULT: 'var(--color-accent)',
                    soft: 'var(--color-accent-soft)',
                },
                success: 'var(--color-success)',
                warning: 'var(--color-warning)',
                error: 'var(--color-error)',

                // Legacy support (deprecated)
                'surface-alt': 'var(--color-surface-alt)',
                background: '#F8FAFC',
                foreground: '#1E293B',
                card: '#FFFFFF',
                'card-foreground': '#1E293B',
                popover: '#FFFFFF',
                'popover-foreground': '#1E293B',
                secondary: '#F2F5F8',
                'secondary-foreground': '#1E293B',
                destructive: {
                    DEFAULT: '#F87171',
                    foreground: '#FFFFFF',
                },
                ring: 'var(--color-primary)',
                input: '#E2E8F0',
            },
            boxShadow: {
                card: 'var(--shadow-card)',
                'card-hover': 'var(--shadow-card-hover)',
                'soft': '0 1px 3px rgba(0, 0, 0, 0.1)',
                // Legacy shadows (deprecated)
                'card-dark': '0 2px 8px rgba(0, 0, 0, 0.3)',
                'card-hover-dark': '0 4px 16px rgba(0, 0, 0, 0.4)',
                'soft-dark': '0 1px 3px rgba(0, 0, 0, 0.2)',
            },
            backgroundImage: {
                'ai-flow': 'var(--grad-ai-flow)',
                'ai-holo': 'var(--grad-ai-holo)',
                'ai-mist-light': 'linear-gradient(180deg, rgba(248,252,255,0.9) 0%, rgba(240,245,250,0.9) 100%)',
                'ai-mist-dark': 'linear-gradient(180deg, rgba(26,28,33,0.85) 0%, rgba(18,20,25,0.85) 100%)',
            },
            ringColor: {
                DEFAULT: 'var(--color-primary)',
            },
            borderRadius: {
                lg: '1rem',
                md: '0.75rem',
                sm: '0.5rem',
                xl: '1.5rem',
                '2xl': '2rem',
            },
            keyframes: {
                'accordion-down': {
                    from: { height: 0 },
                    to: { height: 'var(--radix-accordion-content-height)' },
                },
                'accordion-up': {
                    from: { height: 'var(--radix-accordion-content-height)' },
                    to: { height: 0 },
                },
                'fade-in': {
                    '0%': { opacity: '0' },
                    '100%': { opacity: '1' },
                },
                'slide-up': {
                    '0%': { opacity: '0', transform: 'translateY(10px)' },
                    '100%': { opacity: '1', transform: 'translateY(0)' },
                },
                'pulse-soft': {
                    '0%, 100%': { opacity: '1' },
                    '50%': { opacity: '0.8' },
                },
            },
            animation: {
                'accordion-down': 'accordion-down 0.2s ease-out',
                'accordion-up': 'accordion-up 0.2s ease-out',
                'fade-in': 'fade-in 0.25s ease-out',
                'slide-up': 'slide-up 0.3s ease-out',
                'pulse-soft': 'pulse-soft 2s ease-in-out infinite',
            },
            spacing: {
                'safe-area-inset-bottom': 'env(safe-area-inset-bottom)',
            },
            backdropBlur: {
                'xs': '2px',
            },
        },
    },
    plugins: [require('tailwindcss-animate')],
}
