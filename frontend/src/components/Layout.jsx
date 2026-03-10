import { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import {
    FileText, LayoutDashboard, FolderOpen, LogOut,
    Menu, X, ChevronRight, User
} from 'lucide-react';
import toast from 'react-hot-toast';

export default function Layout({ children }) {
    const location = useLocation();
    const navigate = useNavigate();
    const [sidebarOpen, setSidebarOpen] = useState(false);

    const user = JSON.parse(localStorage.getItem('user') || '{}');

    const navigation = [
        { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
        { name: 'Projects', href: '/projects', icon: FolderOpen }
    ];

    const handleLogout = () => {
        localStorage.clear();
        toast.success('Logged out successfully');
        navigate('/login');
    };

    const getBreadcrumbs = () => {
        const paths = location.pathname.split('/').filter(Boolean);
        return paths.map((path, index) => ({
            name: path.charAt(0).toUpperCase() + path.slice(1),
            href: '/' + paths.slice(0, index + 1).join('/')
        }));
    };

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Top Navbar */}
            <nav className="fixed top-0 left-0 right-0 h-16 bg-white/80 backdrop-blur-xl border-b border-gray-200 z-50">
                <div className="h-full px-6 flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                        <button
                            onClick={() => setSidebarOpen(!sidebarOpen)}
                            className="lg:hidden p-2 hover:bg-gray-100 rounded-lg transition-colors"
                        >
                            {sidebarOpen ? <X className="w-5 h-5 text-gray-900" /> : <Menu className="w-5 h-5 text-gray-900" />}
                        </button>

                        <Link to="/dashboard" className="flex items-center space-x-2">
                            <FileText className="w-6 h-6 text-blue-600" />
                            <span className="text-lg font-semibold text-gray-900">BRD Platform</span>
                        </Link>
                    </div>

                    <div className="flex items-center space-x-4">
                        <div className="hidden md:flex items-center space-x-2 px-3 py-2 bg-gray-100 rounded-lg">
                            <User className="w-4 h-4 text-gray-600" />
                            <span className="text-sm text-gray-900">{user.username || 'User'}</span>
                        </div>
                        <button
                            onClick={handleLogout}
                            className="p-2 hover:bg-gray-100 rounded-lg transition-colors text-gray-600 hover:text-gray-900"
                            title="Logout"
                        >
                            <LogOut className="w-5 h-5" />
                        </button>
                    </div>
                </div>
            </nav>

            {/* Sidebar */}
            <aside className={`
                fixed top-16 left-0 bottom-0 w-64 bg-white/80 backdrop-blur-xl border-r border-gray-200 z-40
                transition-transform duration-300 lg:translate-x-0
                ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
            `}>
                <nav className="p-4 space-y-1">
                    {navigation.map((item) => {
                        const isActive = location.pathname === item.href ||
                            location.pathname.startsWith(item.href + '/');
                        return (
                            <Link
                                key={item.name}
                                to={item.href}
                                onClick={() => setSidebarOpen(false)}
                                className={`
                                    flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors
                                    ${isActive
                                        ? 'bg-blue-50 text-blue-600 border border-blue-200'
                                        : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                                    }
                                `}
                            >
                                <item.icon className="w-5 h-5" />
                                <span className="font-medium">{item.name}</span>
                            </Link>
                        );
                    })}
                </nav>
            </aside>

            {/* Mobile Sidebar Overlay */}
            {sidebarOpen && (
                <div
                    className="fixed inset-0 bg-gray-900/20 backdrop-blur-sm z-30 lg:hidden"
                    onClick={() => setSidebarOpen(false)}
                />
            )}

            {/* Main Content */}
            <main className="pt-16 lg:pl-64">
                {/* Breadcrumbs */}
                {getBreadcrumbs().length > 0 && (
                    <div className="px-6 py-4 border-b border-gray-200 bg-white">
                        <div className="flex items-center space-x-2 text-sm">
                            {getBreadcrumbs().map((crumb, index) => (
                                <div key={crumb.href} className="flex items-center space-x-2">
                                    {index > 0 && <ChevronRight className="w-4 h-4 text-gray-400" />}
                                    <Link
                                        to={crumb.href}
                                        className={`
                                            ${index === getBreadcrumbs().length - 1
                                                ? 'text-gray-900 font-medium'
                                                : 'text-gray-600 hover:text-gray-900'
                                            }
                                        `}
                                    >
                                        {crumb.name}
                                    </Link>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Page Content */}
                <div className="p-6">
                    {children}
                </div>
            </main>
        </div>
    );
}
