import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import {
    FileText, Zap, Users, Shield, ArrowRight,
    CheckCircle, Sparkles, Database, GitBranch
} from 'lucide-react';

export default function Landing() {
    const navigate = useNavigate();

    const features = [
        {
            icon: Database,
            title: 'Multi-Source Ingestion',
            description: 'Import requirements from files, emails, meetings, and collaboration tools.'
        },
        {
            icon: Sparkles,
            title: 'AI-Powered Extraction',
            description: 'Automatically extract and classify requirements using advanced NLP.'
        },
        {
            icon: GitBranch,
            title: 'Conflict Detection',
            description: 'Identify contradictions and duplicates before they become problems.'
        },
        {
            icon: FileText,
            title: 'Professional BRDs',
            description: 'Generate polished, structured documents ready for stakeholder review.'
        },
        {
            icon: Users,
            title: 'Team Collaboration',
            description: 'Role-based access control for seamless team workflows.'
        },
        {
            icon: Shield,
            title: 'Enterprise Security',
            description: 'JWT authentication, data encryption, and audit logging.'
        }
    ];

    const steps = [
        { number: '01', title: 'Upload Data', description: 'Import requirements from any source' },
        { number: '02', title: 'Extract Requirements', description: 'AI processes and classifies content' },
        { number: '03', title: 'Review & Refine', description: 'Validate and organize requirements' },
        { number: '04', title: 'Generate BRD', description: 'Export professional documentation' }
    ];

    return (
        <div className="min-h-screen bg-white text-gray-900">
            {/* Background Gradient */}
            <div className="fixed inset-0 bg-gradient-to-br from-blue-50 via-white to-purple-50 -z-10" />

            {/* Navigation */}
            <nav className="fixed top-0 w-full bg-white/80 backdrop-blur-xl border-b border-gray-200 z-50">
                <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                        <FileText className="w-6 h-6 text-blue-600" />
                        <span className="text-xl font-semibold text-gray-900">BRD Platform</span>
                    </div>
                    <div className="flex items-center space-x-4">
                        <button
                            onClick={() => navigate('/login')}
                            className="px-4 py-2 text-sm text-gray-600 hover:text-gray-900 transition-colors"
                        >
                            Sign In
                        </button>
                        <button
                            onClick={() => navigate('/register')}
                            className="px-4 py-2 text-sm bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
                        >
                            Get Started
                        </button>
                    </div>
                </div>
            </nav>

            {/* Hero Section */}
            <section className="pt-32 pb-20 px-6 relative">
                {/* Soft Gradient Glow */}
                <div className="absolute top-20 left-1/2 -translate-x-1/2 w-[600px] h-[600px] bg-gradient-to-r from-blue-400/20 to-purple-400/20 rounded-full blur-3xl -z-10" />

                <div className="max-w-7xl mx-auto text-center">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.5 }}
                    >
                        <div className="inline-flex items-center space-x-2 px-4 py-2 bg-blue-50 border border-blue-200 rounded-full mb-6">
                            <Zap className="w-4 h-4 text-blue-600" />
                            <span className="text-sm text-blue-600 font-medium">AI-Powered Requirements Management</span>
                        </div>
                        <h1 className="text-5xl md:text-7xl font-bold mb-6 leading-tight text-gray-900">
                            Transform Requirements
                            <br />
                            <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600">
                                Into Professional BRDs
                            </span>
                        </h1>
                        <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
                            Automate requirement extraction, conflict detection, and document generation.
                            Save weeks of manual work with AI-powered analysis.
                        </p>
                        <div className="flex items-center justify-center space-x-4">
                            <button
                                onClick={() => navigate('/register')}
                                className="px-8 py-4 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors flex items-center space-x-2 shadow-lg shadow-blue-500/25"
                            >
                                <span>Start Free Trial</span>
                                <ArrowRight className="w-5 h-5" />
                            </button>
                            <button
                                onClick={() => navigate('/login')}
                                className="px-8 py-4 bg-white hover:bg-gray-50 border border-gray-200 text-gray-900 rounded-lg font-medium transition-colors shadow-sm"
                            >
                                View Demo
                            </button>
                        </div>
                    </motion.div>
                </div>
            </section>

            {/* Features Grid */}
            <section className="py-20 px-6 bg-gray-50">
                <div className="max-w-7xl mx-auto">
                    <div className="text-center mb-16">
                        <h2 className="text-3xl md:text-4xl font-bold mb-4 text-gray-900">
                            Everything you need to manage requirements
                        </h2>
                        <p className="text-gray-600 text-lg">
                            Built for product managers, business analysts, and development teams
                        </p>
                    </div>
                    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {features.map((feature, index) => (
                            <motion.div
                                key={index}
                                initial={{ opacity: 0, y: 20 }}
                                whileInView={{ opacity: 1, y: 0 }}
                                transition={{ duration: 0.5, delay: index * 0.1 }}
                                viewport={{ once: true }}
                                className="p-6 bg-white border border-gray-200 rounded-xl hover:border-gray-300 hover:shadow-lg transition-all"
                            >
                                <feature.icon className="w-10 h-10 text-blue-600 mb-4" />
                                <h3 className="text-xl font-semibold mb-2 text-gray-900">{feature.title}</h3>
                                <p className="text-gray-600">{feature.description}</p>
                            </motion.div>
                        ))}
                    </div>
                </div>
            </section>

            {/* How It Works */}
            <section className="py-20 px-6 bg-white">
                <div className="max-w-7xl mx-auto">
                    <div className="text-center mb-16">
                        <h2 className="text-3xl md:text-4xl font-bold mb-4 text-gray-900">
                            Simple, powerful workflow
                        </h2>
                        <p className="text-gray-600 text-lg">
                            From raw data to polished documentation in minutes
                        </p>
                    </div>
                    <div className="grid md:grid-cols-4 gap-8">
                        {steps.map((step, index) => (
                            <motion.div
                                key={index}
                                initial={{ opacity: 0, y: 20 }}
                                whileInView={{ opacity: 1, y: 0 }}
                                transition={{ duration: 0.5, delay: index * 0.1 }}
                                viewport={{ once: true }}
                                className="relative"
                            >
                                <div className="text-6xl font-bold text-gray-100 mb-4">{step.number}</div>
                                <h3 className="text-xl font-semibold mb-2 text-gray-900">{step.title}</h3>
                                <p className="text-gray-600">{step.description}</p>
                                {index < steps.length - 1 && (
                                    <div className="hidden md:block absolute top-8 left-full w-full h-px bg-gradient-to-r from-gray-300 to-transparent" />
                                )}
                            </motion.div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Target Users */}
            <section className="py-20 px-6 bg-gray-50">
                <div className="max-w-7xl mx-auto">
                    <div className="text-center mb-16">
                        <h2 className="text-3xl md:text-4xl font-bold mb-4 text-gray-900">
                            Built for modern teams
                        </h2>
                    </div>
                    <div className="grid md:grid-cols-3 gap-8">
                        {[
                            {
                                role: 'Product Managers',
                                benefits: ['Faster requirement gathering', 'Automated documentation', 'Stakeholder alignment']
                            },
                            {
                                role: 'Business Analysts',
                                benefits: ['Conflict detection', 'Traceability matrix', 'Version control']
                            },
                            {
                                role: 'Development Teams',
                                benefits: ['Clear specifications', 'Reduced ambiguity', 'Better estimates']
                            }
                        ].map((user, index) => (
                            <motion.div
                                key={index}
                                initial={{ opacity: 0, y: 20 }}
                                whileInView={{ opacity: 1, y: 0 }}
                                transition={{ duration: 0.5, delay: index * 0.1 }}
                                viewport={{ once: true }}
                                className="p-8 bg-white border border-gray-200 rounded-xl hover:shadow-lg transition-shadow"
                            >
                                <h3 className="text-2xl font-semibold mb-6 text-gray-900">{user.role}</h3>
                                <ul className="space-y-3">
                                    {user.benefits.map((benefit, i) => (
                                        <li key={i} className="flex items-start space-x-3">
                                            <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                                            <span className="text-gray-600">{benefit}</span>
                                        </li>
                                    ))}
                                </ul>
                            </motion.div>
                        ))}
                    </div>
                </div>
            </section>

            {/* CTA Section */}
            <section className="py-20 px-6 bg-white">
                <div className="max-w-4xl mx-auto text-center">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.5 }}
                        viewport={{ once: true }}
                        className="p-12 bg-gradient-to-br from-blue-50 to-purple-50 border border-blue-200 rounded-2xl"
                    >
                        <h2 className="text-3xl md:text-4xl font-bold mb-4 text-gray-900">
                            Ready to streamline your requirements?
                        </h2>
                        <p className="text-gray-600 text-lg mb-8">
                            Join teams already using BRD Platform to deliver better products faster.
                        </p>
                        <button
                            onClick={() => navigate('/register')}
                            className="px-8 py-4 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors inline-flex items-center space-x-2 shadow-lg shadow-blue-500/25"
                        >
                            <span>Get Started Free</span>
                            <ArrowRight className="w-5 h-5" />
                        </button>
                    </motion.div>
                </div>
            </section>

            {/* Footer */}
            <footer className="py-12 px-6 border-t border-gray-200 bg-white">
                <div className="max-w-7xl mx-auto">
                    <div className="flex flex-col md:flex-row items-center justify-between">
                        <div className="flex items-center space-x-2 mb-4 md:mb-0">
                            <FileText className="w-5 h-5 text-blue-600" />
                            <span className="font-semibold text-gray-900">BRD Platform</span>
                        </div>
                        <div className="text-sm text-gray-600">
                            © 2024 BRD Platform. All rights reserved.
                        </div>
                    </div>
                </div>
            </footer>
        </div>
    );
}
