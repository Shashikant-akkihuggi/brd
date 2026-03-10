import { motion } from 'framer-motion';

export default function GlassCard({ children, className = '', hover = true, ...props }) {
    return (
        <motion.div
            className={`glass rounded-2xl p-6 ${hover ? 'glass-hover' : ''} ${className}`}
            whileHover={hover ? { scale: 1.02, rotateX: 2, rotateY: 2 } : {}}
            transition={{ duration: 0.3 }}
            style={{
                transformStyle: 'preserve-3d',
                perspective: '1000px',
            }}
            {...props}
        >
            {children}
        </motion.div>
    );
}
