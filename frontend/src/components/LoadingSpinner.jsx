import { motion } from 'framer-motion';

export default function LoadingSpinner({ size = 'md' }) {
    const sizes = {
        sm: 'w-6 h-6',
        md: 'w-12 h-12',
        lg: 'w-16 h-16',
    };

    return (
        <div className="flex items-center justify-center">
            <motion.div
                className={`${sizes[size]} border-4 border-primary-500/30 border-t-primary-500 rounded-full`}
                animate={{ rotate: 360 }}
                transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
            />
        </div>
    );
}
