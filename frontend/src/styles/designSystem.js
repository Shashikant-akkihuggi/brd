// BRD Platform Design System - White/Light Theme
// This is the MASTER design system extracted from DashboardNew.jsx and Layout.jsx

export const colors = {
    // Background colors
    background: '#f9fafb',        // bg-gray-50
    backgroundAlt: '#ffffff',     // bg-white

    // Card colors
    card: '#ffffff',              // bg-white
    cardHover: '#f9fafb',         // bg-gray-50
    cardBorder: '#e5e7eb',        // border-gray-200
    cardBorderHover: '#d1d5db',   // border-gray-300

    // Primary colors (Blue)
    primary: '#2563eb',           // bg-blue-600
    primaryHover: '#1d4ed8',      // bg-blue-700
    primaryLight: '#eff6ff',      // bg-blue-50
    primaryBorder: '#bfdbfe',     // border-blue-200

    // Text colors
    textPrimary: '#111827',       // text-gray-900
    textSecondary: '#6b7280',     // text-gray-600
    textTertiary: '#9ca3af',      // text-gray-400

    // Border colors
    border: '#e5e7eb',            // border-gray-200
    borderLight: '#f3f4f6',       // border-gray-100

    // Status colors
    success: '#10b981',           // text-green-600
    successLight: '#d1fae5',      // bg-green-50
    successBorder: '#a7f3d0',     // border-green-200

    warning: '#f59e0b',           // text-orange-600
    warningLight: '#ffedd5',      // bg-orange-50
    warningBorder: '#fed7aa',     // border-orange-200

    purple: '#9333ea',            // text-purple-600
    purpleLight: '#f3e8ff',       // bg-purple-50
    purpleBorder: '#e9d5ff',      // border-purple-200

    // Overlay
    overlay: 'rgba(17, 24, 39, 0.2)',  // bg-gray-900/20
};

export const spacing = {
    xs: '0.25rem',    // 1
    sm: '0.5rem',     // 2
    md: '0.75rem',    // 3
    lg: '1rem',       // 4
    xl: '1.5rem',     // 6
    '2xl': '2rem',    // 8
    '3xl': '3rem',    // 12
    '4xl': '4rem',    // 16
};

export const borderRadius = {
    sm: '0.375rem',   // rounded-md
    md: '0.5rem',     // rounded-lg
    lg: '0.75rem',    // rounded-xl
    xl: '1rem',       // rounded-2xl
    full: '9999px',   // rounded-full
};

export const shadows = {
    sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    md: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
    lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
    xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1)',
    blue: '0 10px 15px -3px rgba(37, 99, 235, 0.25)',  // shadow-blue-500/25
};

export const typography = {
    // Headings
    h1: 'text-3xl font-bold text-gray-900',
    h2: 'text-xl font-semibold text-gray-900',
    h3: 'text-lg font-semibold text-gray-900',

    // Body text
    body: 'text-base text-gray-600',
    bodySmall: 'text-sm text-gray-600',
    bodyLarge: 'text-lg text-gray-600',

    // Labels
    label: 'text-sm font-medium text-gray-700',
};

export const buttonVariants = {
    primary: 'px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg font-medium text-white transition-colors shadow-lg shadow-blue-500/25',
    secondary: 'px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg font-medium text-gray-900 transition-colors',
    ghost: 'px-4 py-2 hover:bg-gray-100 rounded-lg font-medium text-gray-600 hover:text-gray-900 transition-colors',
    danger: 'px-4 py-2 bg-red-600 hover:bg-red-700 rounded-lg font-medium text-white transition-colors',
    link: 'text-blue-600 hover:text-blue-700 transition-colors font-medium',
};

export const cardVariants = {
    default: 'bg-white border border-gray-200 rounded-xl p-6 shadow-sm',
    hover: 'bg-white border border-gray-200 rounded-xl p-6 hover:border-gray-300 hover:shadow-lg transition-all cursor-pointer',
    stat: 'bg-white border border-gray-200 rounded-xl p-6 hover:border-gray-300 hover:shadow-lg transition-all',
    project: 'p-4 bg-gray-50 border border-gray-200 rounded-lg hover:border-gray-300 hover:shadow-md cursor-pointer transition-all',
};

export const layout = {
    maxWidth: 'max-w-7xl',
    containerPadding: 'px-4 sm:px-6 lg:px-8',
    sectionSpacing: 'space-y-8',
};

export const navbar = {
    height: 'h-16',
    background: 'bg-white/80 backdrop-blur-xl',
    border: 'border-b border-gray-200',
    padding: 'px-6',
};

export const sidebar = {
    width: 'w-64',
    background: 'bg-white/80 backdrop-blur-xl',
    border: 'border-r border-gray-200',
    padding: 'p-4',
    itemActive: 'bg-blue-50 text-blue-600 border border-blue-200',
    itemInactive: 'text-gray-600 hover:bg-gray-100 hover:text-gray-900',
};

export const input = {
    default: 'w-full px-4 py-3 bg-white border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all',
    error: 'w-full px-4 py-3 bg-white border border-red-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent transition-all',
};

export const modal = {
    overlay: 'fixed inset-0 bg-gray-900/20 backdrop-blur-sm flex items-center justify-center p-4 z-50',
    container: 'w-full max-w-md bg-white rounded-xl shadow-xl border border-gray-200',
    header: 'px-6 py-4 border-b border-gray-200',
    body: 'px-6 py-4',
    footer: 'px-6 py-4 border-t border-gray-200 flex justify-end space-x-3',
};
