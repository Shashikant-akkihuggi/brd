import { useState } from 'react';
import { motion } from 'framer-motion';
import { useNavigate, Link } from 'react-router-dom';
import { Mail, Lock, User, UserPlus } from 'lucide-react';
import toast from 'react-hot-toast';
import api from '../api/axios';
import AnimatedButton from '../components/AnimatedButton';
import GlassCard from '../components/GlassCard';

export default function Register() {
    const navigate = useNavigate();
    const [formData, setFormData] = useState({
        email: '',
        username: '',
        password: '',
        full_name: '',
    });
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);

        try {
            console.log('Attempting registration to:', 'http://127.0.0.1:8000/api/auth/register');
            console.log('Form data:', formData);

            const response = await api.post('/api/auth/register', formData);

            console.log('Registration successful:', response.data);

            localStorage.setItem('token', response.data.access_token);
            localStorage.setItem('refreshToken', response.data.refresh_token);
            localStorage.setItem('user', JSON.stringify(response.data.user));

            toast.success('Account created successfully!');
            navigate('/dashboard');
        } catch (error) {
            console.error('Register error:', error);

            if (error.message) {
                toast.error(error.message);
            } else {
                toast.error('Registration failed. Please try again.');
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen animated-bg flex items-center justify-center p-4 relative overflow-hidden">
            {/* Animated Blobs */}
            <div className="blob blob-1" />
            <div className="blob blob-2" />
            <div className="blob blob-3" />

            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
                className="w-full max-w-md relative z-10"
            >
                <GlassCard hover={false} className="p-8">
                    <motion.div
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        transition={{ delay: 0.2, type: 'spring' }}
                        className="w-16 h-16 bg-gradient-to-br from-primary-500 to-cyan-500 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg shadow-primary-500/50"
                    >
                        <UserPlus className="w-8 h-8 text-white" />
                    </motion.div>

                    <h1 className="text-3xl font-bold text-center mb-2 text-gradient">
                        Create Account
                    </h1>
                    <p className="text-gray-400 text-center mb-8">
                        Join BRD Platform today
                    </p>

                    <form onSubmit={handleSubmit} className="space-y-5">
                        <div>
                            <label className="block text-sm font-medium text-gray-300 mb-2">
                                Full Name
                            </label>
                            <div className="relative">
                                <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                                <input
                                    type="text"
                                    required
                                    value={formData.full_name}
                                    onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                                    className="w-full pl-12 pr-4 py-3 glass rounded-xl focus:glow-border outline-none transition-all"
                                    placeholder="John Doe"
                                />
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-300 mb-2">
                                Username
                            </label>
                            <div className="relative">
                                <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                                <input
                                    type="text"
                                    required
                                    value={formData.username}
                                    onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                                    className="w-full pl-12 pr-4 py-3 glass rounded-xl focus:glow-border outline-none transition-all"
                                    placeholder="johndoe"
                                />
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-300 mb-2">
                                Email Address
                            </label>
                            <div className="relative">
                                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                                <input
                                    type="email"
                                    required
                                    value={formData.email}
                                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                                    className="w-full pl-12 pr-4 py-3 glass rounded-xl focus:glow-border outline-none transition-all"
                                    placeholder="you@example.com"
                                />
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-300 mb-2">
                                Password
                            </label>
                            <div className="relative">
                                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                                <input
                                    type="password"
                                    required
                                    value={formData.password}
                                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                                    className="w-full pl-12 pr-4 py-3 glass rounded-xl focus:glow-border outline-none transition-all"
                                    placeholder="••••••••"
                                />
                            </div>
                        </div>

                        <AnimatedButton
                            type="submit"
                            disabled={loading}
                            className="w-full"
                        >
                            {loading ? 'Creating account...' : 'Create Account'}
                        </AnimatedButton>
                    </form>

                    <p className="text-center text-gray-400 mt-6">
                        Already have an account?{' '}
                        <Link to="/login" className="text-primary-400 hover:text-primary-300 transition-colors">
                            Sign in
                        </Link>
                    </p>
                </GlassCard>
            </motion.div>
        </div>
    );
}
