import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Plus, FolderOpen, Calendar, Trash2 } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { projectsAPI } from '../services/api';
import Layout from '../components/Layout';

export default function Dashboard() {
    const navigate = useNavigate();
    const [projects, setProjects] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showModal, setShowModal] = useState(false);
    const [newProject, setNewProject] = useState({
        name: '',
        description: '',
        keywords: '',
    });

    useEffect(() => {
        loadProjects();
    }, []);

    const loadProjects = async () => {
        try {
            const response = await projectsAPI.list();
            setProjects(response.data || []);
        } catch (error) {
            console.error('Error loading projects:', error);
            setProjects([]);
        } finally {
            setLoading(false);
        }
    };

    const handleCreateProject = async (e) => {
        e.preventDefault();
        try {
            const keywords = newProject.keywords.split(',').map(k => k.trim()).filter(k => k);
            await projectsAPI.create({
                ...newProject,
                keywords: keywords.length > 0 ? keywords : null,
            });
            toast.success('Project created successfully!');
            setShowModal(false);
            setNewProject({ name: '', description: '', keywords: '' });
            loadProjects();
        } catch (error) {
            console.error('Error creating project:', error);
        }
    };

    const handleDeleteProject = async (id) => {
        if (!confirm('Are you sure you want to delete this project?')) return;

        try {
            await projectsAPI.delete(id);
            toast.success('Project deleted successfully!');
            loadProjects();
        } catch (error) {
            console.error('Error deleting project:', error);
        }
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
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="flex justify-between items-center"
                >
                    <div>
                        <h1 className="text-3xl font-bold text-gray-900 mb-2">Projects</h1>
                        <p className="text-gray-600">Manage your BRD projects</p>
                    </div>

                    <button
                        onClick={() => setShowModal(true)}
                        className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg font-medium text-white transition-colors flex items-center space-x-2 shadow-lg shadow-blue-500/25"
                    >
                        <Plus className="w-5 h-5" />
                        <span>New Project</span>
                    </button>
                </motion.div>

                {(projects && projects.length === 0) ? (
                    <motion.div
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="text-center py-20 bg-white border border-gray-200 rounded-xl"
                    >
                        <FolderOpen className="w-20 h-20 text-gray-400 mx-auto mb-4" />
                        <h3 className="text-2xl font-semibold text-gray-900 mb-2">No projects yet</h3>
                        <p className="text-gray-600 mb-6">Create your first project to get started</p>
                        <button
                            onClick={() => setShowModal(true)}
                            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg font-medium text-white transition-colors inline-flex items-center space-x-2 shadow-lg shadow-blue-500/25"
                        >
                            <Plus className="w-5 h-5" />
                            <span>Create Project</span>
                        </button>
                    </motion.div>
                ) : (
                    <motion.div
                        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
                        initial="hidden"
                        animate="visible"
                        variants={{
                            visible: {
                                transition: {
                                    staggerChildren: 0.1,
                                },
                            },
                        }}
                    >
                        {projects.map((project) => (
                            <motion.div
                                key={project.id}
                                variants={{
                                    hidden: { opacity: 0, y: 20 },
                                    visible: { opacity: 1, y: 0 },
                                }}
                            >
                                <div
                                    className="bg-white border border-gray-200 rounded-xl p-6 hover:border-gray-300 hover:shadow-lg transition-all cursor-pointer group relative"
                                    onClick={() => navigate(`/project/${project.id}`)}
                                >
                                    <div className="absolute top-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity">
                                        <motion.button
                                            whileHover={{ scale: 1.1 }}
                                            whileTap={{ scale: 0.9 }}
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                handleDeleteProject(project.id);
                                            }}
                                            className="p-2 bg-red-50 rounded-lg hover:bg-red-100 transition-colors"
                                        >
                                            <Trash2 className="w-4 h-4 text-red-600" />
                                        </motion.button>
                                    </div>

                                    <h3 className="text-xl font-semibold mb-2 text-gray-900 group-hover:text-blue-600 transition-colors">
                                        {project.name}
                                    </h3>
                                    <p className="text-gray-600 text-sm mb-4 line-clamp-2">
                                        {project.description || 'No description'}
                                    </p>

                                    {project.keywords && project.keywords.length > 0 && (
                                        <div className="flex flex-wrap gap-2 mb-4">
                                            {project.keywords.slice(0, 3).map((keyword, idx) => (
                                                <span
                                                    key={idx}
                                                    className="px-3 py-1 bg-blue-50 text-blue-600 rounded-full text-xs border border-blue-200"
                                                >
                                                    {keyword}
                                                </span>
                                            ))}
                                            {project.keywords.length > 3 && (
                                                <span className="px-3 py-1 bg-gray-100 text-gray-600 rounded-full text-xs border border-gray-200">
                                                    +{project.keywords.length - 3}
                                                </span>
                                            )}
                                        </div>
                                    )}

                                    <div className="flex items-center text-xs text-gray-500">
                                        <Calendar className="w-3 h-3 mr-1" />
                                        {new Date(project.created_at).toLocaleDateString()}
                                    </div>
                                </div>
                            </motion.div>
                        ))}
                    </motion.div>
                )}
            </div>

            {/* Create Project Modal */}
            {showModal && (
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="fixed inset-0 bg-gray-900/20 backdrop-blur-sm flex items-center justify-center p-4 z-50"
                    onClick={() => setShowModal(false)}
                >
                    <motion.div
                        initial={{ scale: 0.9, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        exit={{ scale: 0.9, opacity: 0 }}
                        onClick={(e) => e.stopPropagation()}
                        className="w-full max-w-md bg-white rounded-xl shadow-xl border border-gray-200"
                    >
                        <div className="px-6 py-4 border-b border-gray-200">
                            <h2 className="text-2xl font-bold text-gray-900">Create New Project</h2>
                        </div>

                        <form onSubmit={handleCreateProject} className="px-6 py-4 space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Project Name *
                                </label>
                                <input
                                    type="text"
                                    required
                                    value={newProject.name}
                                    onChange={(e) => setNewProject({ ...newProject, name: e.target.value })}
                                    className="w-full px-4 py-3 bg-white border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                                    placeholder="My Awesome Project"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Description
                                </label>
                                <textarea
                                    value={newProject.description}
                                    onChange={(e) => setNewProject({ ...newProject, description: e.target.value })}
                                    className="w-full px-4 py-3 bg-white border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all resize-none"
                                    rows="3"
                                    placeholder="Brief description of your project"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Keywords (comma-separated)
                                </label>
                                <input
                                    type="text"
                                    value={newProject.keywords}
                                    onChange={(e) => setNewProject({ ...newProject, keywords: e.target.value })}
                                    className="w-full px-4 py-3 bg-white border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                                    placeholder="authentication, payment, dashboard"
                                />
                            </div>

                            <div className="flex space-x-3 pt-4">
                                <button
                                    type="submit"
                                    className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg font-medium text-white transition-colors shadow-lg shadow-blue-500/25"
                                >
                                    Create Project
                                </button>
                                <button
                                    type="button"
                                    onClick={() => setShowModal(false)}
                                    className="flex-1 px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg font-medium text-gray-900 transition-colors"
                                >
                                    Cancel
                                </button>
                            </div>
                        </form>
                    </motion.div>
                </motion.div>
            )}
        </Layout>
    );
}
