import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
    FolderOpen, FileText, TrendingUp, Clock,
    Plus, ArrowRight, Activity
} from 'lucide-react';
import { projectsAPI } from '../services/api';
import Layout from '../components/Layout';

export default function DashboardNew() {
    const navigate = useNavigate();
    const [projects, setProjects] = useState([]);
    const [loading, setLoading] = useState(true);
    const [stats, setStats] = useState({
        totalProjects: 0,
        activeProjects: 0,
        totalRequirements: 0,
        documentsGenerated: 0
    });

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        try {
            const response = await projectsAPI.list();
            const projectList = response.data || [];
            setProjects(projectList.slice(0, 5)); // Show recent 5

            setStats({
                totalProjects: projectList.length,
                activeProjects: projectList.length,
                totalRequirements: 0,
                documentsGenerated: 0
            });
        } catch (error) {
            console.error('Error loading data:', error);
            setProjects([]);
        } finally {
            setLoading(false);
        }
    };

    const statCards = [
        {
            label: 'Total Projects',
            value: stats.totalProjects,
            icon: FolderOpen,
            color: 'blue',
            trend: null
        },
        {
            label: 'Active Projects',
            value: stats.activeProjects,
            icon: Activity,
            color: 'green',
            trend: null
        },
        {
            label: 'Requirements',
            value: stats.totalRequirements,
            icon: FileText,
            color: 'purple',
            trend: null
        },
        {
            label: 'Documents',
            value: stats.documentsGenerated,
            icon: TrendingUp,
            color: 'orange',
            trend: null
        }
    ];

    const colorClasses = {
        blue: 'text-blue-600 bg-blue-50 border-blue-200',
        green: 'text-green-600 bg-green-50 border-green-200',
        purple: 'text-purple-600 bg-purple-50 border-purple-200',
        orange: 'text-orange-600 bg-orange-50 border-orange-200'
    };

    if (loading) {
        return (
            <Layout>
                <div className="flex items-center justify-center h-64">
                    <div className="w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
                </div>
            </Layout>
        );
    }

    return (
        <Layout>
            <div className="max-w-7xl mx-auto space-y-8">
                {/* Header */}
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-3xl font-bold text-gray-900 mb-2">Dashboard</h1>
                        <p className="text-gray-600">Welcome back! Here's your project overview.</p>
                    </div>
                    <button
                        onClick={() => navigate('/projects')}
                        className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg font-medium text-white transition-colors flex items-center space-x-2 shadow-lg shadow-blue-500/25"
                    >
                        <Plus className="w-5 h-5" />
                        <span>New Project</span>
                    </button>
                </div>

                {/* Stats Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    {statCards.map((stat, index) => (
                        <motion.div
                            key={stat.label}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.3, delay: index * 0.1 }}
                            className="bg-white border border-gray-200 rounded-xl p-6 hover:border-gray-300 hover:shadow-lg transition-all"
                        >
                            <div className="flex items-center justify-between mb-4">
                                <div className={`p-3 rounded-lg border ${colorClasses[stat.color]}`}>
                                    <stat.icon className="w-5 h-5" />
                                </div>
                                {stat.trend && (
                                    <span className="text-sm text-green-600">+{stat.trend}%</span>
                                )}
                            </div>
                            <div className="text-3xl font-bold text-gray-900 mb-1">{stat.value}</div>
                            <div className="text-sm text-gray-600">{stat.label}</div>
                        </motion.div>
                    ))}
                </div>

                {/* Recent Projects */}
                <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
                    <div className="flex items-center justify-between mb-6">
                        <h2 className="text-xl font-semibold text-gray-900">Recent Projects</h2>
                        <button
                            onClick={() => navigate('/projects')}
                            className="text-sm text-blue-600 hover:text-blue-700 transition-colors flex items-center space-x-1"
                        >
                            <span>View all</span>
                            <ArrowRight className="w-4 h-4" />
                        </button>
                    </div>

                    {(projects && projects.length === 0) ? (
                        <div className="text-center py-12">
                            <FolderOpen className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                            <p className="text-gray-600 mb-4">No projects yet</p>
                            <button
                                onClick={() => navigate('/projects')}
                                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg font-medium text-white transition-colors inline-flex items-center space-x-2 shadow-lg shadow-blue-500/25"
                            >
                                <Plus className="w-5 h-5" />
                                <span>Create your first project</span>
                            </button>
                        </div>
                    ) : (
                        <div className="space-y-3">
                            {projects && projects.map((project) => (
                                <motion.div
                                    key={project.id}
                                    whileHover={{ scale: 1.01 }}
                                    onClick={() => navigate(`/project/${project.id}`)}
                                    className="p-4 bg-gray-50 border border-gray-200 rounded-lg hover:border-gray-300 hover:shadow-md cursor-pointer transition-all"
                                >
                                    <div className="flex items-center justify-between">
                                        <div className="flex-1">
                                            <h3 className="font-semibold text-gray-900 mb-1">{project.name}</h3>
                                            <p className="text-sm text-gray-600 line-clamp-1">
                                                {project.description || 'No description'}
                                            </p>
                                        </div>
                                        <div className="flex items-center space-x-4 ml-4">
                                            <div className="flex items-center space-x-2 text-sm text-gray-600">
                                                <Clock className="w-4 h-4" />
                                                <span>{new Date(project.created_at).toLocaleDateString()}</span>
                                            </div>
                                            <ArrowRight className="w-5 h-5 text-gray-400" />
                                        </div>
                                    </div>
                                </motion.div>
                            ))}
                        </div>
                    )}
                </div>

                {/* Quick Actions */}
                <div className="grid md:grid-cols-2 gap-6">
                    <div className="bg-gradient-to-br from-blue-50 to-purple-50 border border-blue-200 rounded-xl p-6">
                        <h3 className="text-lg font-semibold text-gray-900 mb-2">Getting Started</h3>
                        <p className="text-gray-600 text-sm mb-4">
                            Create your first project and start extracting requirements
                        </p>
                        <button
                            onClick={() => navigate('/projects')}
                            className="text-blue-600 hover:text-blue-700 transition-colors text-sm font-medium flex items-center space-x-1"
                        >
                            <span>Create Project</span>
                            <ArrowRight className="w-4 h-4" />
                        </button>
                    </div>

                    <div className="bg-gradient-to-br from-green-50 to-blue-50 border border-green-200 rounded-xl p-6">
                        <h3 className="text-lg font-semibold text-gray-900 mb-2">Need Help?</h3>
                        <p className="text-gray-600 text-sm mb-4">
                            Check out our documentation and guides
                        </p>
                        <button className="text-green-600 hover:text-green-700 transition-colors text-sm font-medium flex items-center space-x-1">
                            <span>View Documentation</span>
                            <ArrowRight className="w-4 h-4" />
                        </button>
                    </div>
                </div>
            </div>
        </Layout>
    );
}
