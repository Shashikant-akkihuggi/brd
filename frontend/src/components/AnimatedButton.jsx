import { motion } from 'framer-motion';

export default function AnimatedButton({
    children,
    onClick,
    variant = 'primary',
    className = '',
    disabled = false,
    type = 'button',
    ...props
}) {
    const variants = {
        primary: 'bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-500 hover:to-blue-400 text-white shadow-lg',
        secondary: 'bg-gray-200 hover:bg-gray-300 text-gray-800 border border-gray-300',
        danger: 'bg-gradient-to-r from-red-600 to-red-500 hover:from-red-500 hover:to-red-400 text-white shadow-lg',
        success: 'bg-gradient-to-r from-green-600 to-green-500 hover:from-green-500 hover:to-green-400 text-white shadow-lg',
    };

    return (
        <motion.button
            type={type}
            onClick={onClick}
            disabled={disabled}
            className={`px-6 py-3 rounded-xl font-medium transition-all duration-300 ${variants[variant]} ${disabled ? 'opacity-50 cursor-not-allowed' : ''} ${className}`}
            whileHover={!disabled ? { scale: 1.05, rotateX: 5 } : {}}
            whileTap={!disabled ? { scale: 0.95 } : {}}
            transition={{ duration: 0.2 }}
            {...props}
        >
            {children}
        </motion.button>
    );
}
