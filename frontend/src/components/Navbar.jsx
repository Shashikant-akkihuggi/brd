import { motion } from 'framer-motion';
import { LogOut, User } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { authAPI } from '../services/api';

export default function Navbar() {
    const navigate = useNavigate();
    const user = JSON.parse(localStorage.getItem('user') || '{}');

    const handleLogout = async () => {
        try {
            const refreshToken = localStorage.getItem('refreshToken');

            if (refreshToken) {
                // Call logout endpoint to revoke refresh token
                await authAPI.logout(refreshToken);
            }
        } catch (error) {
            console.error('Logout error:', error);
            // Continue with local logout even if API call fails
        } finally {
            // Clear local storage
            localStorage.removeItem('token');
            localStorage.removeItem('refreshToken');
            localStorage.removeItem('user');
            toast.success('Logged out successfully');
            navigate('/login');
        }
    };

    return (
        <motion.nav
            initial={{ y: -100 }}
            animate={{ y: 0 }}
            className="glass border-b border-white/10 sticky top-0 z-50 backdrop-blur-xl"
        >
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between items-center h-16">
                    <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-cyan-500 rounded-xl flex items-center justify-center shadow-lg shadow-primary-500/50">
                            <span className="text-white font-bold text-xl">B</span>
                        </div>
                        <span className="text-xl font-bold text-gradient">BRD Platform</span>
                    </div>

                    <div className="flex items-center space-x-4">
                        <div className="glass px-4 py-2 rounded-xl flex items-center space-x-2">
                            <User className="w-4 h-4 text-primary-400" />
                            <span className="text-sm text-gray-300">{user.username || 'User'}</span>
                        </div>

                        <motion.button
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            onClick={handleLogout}
                            className="glass glass-hover px-4 py-2 rounded-xl flex items-center space-x-2 text-red-400"
                        >
                            <LogOut className="w-4 h-4" />
                            <span className="text-sm">Logout</span>
                        </motion.button>
                    </div>
                </div>
            </div>
        </motion.nav>
    );
}
