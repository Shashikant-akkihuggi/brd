import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
    ArrowLeft, FileText, Upload, Sparkles, Download,
    CheckCircle, Circle, AlertCircle, Database, FileSearch
} from 'lucide-react';
import toast from 'react-hot-toast';
import { projectsAPI, documentsAPI, requirementsAPI, ingestionAPI } from '../services/api';
import Navbar from '../components/Navbar';
import GlassCard from '../components/GlassCard';
import AnimatedButton from '../components/AnimatedButton';
import LoadingSpinner from '../components/LoadingSpinner';

export default function ProjectDetails() {
    const { projectId } = useParams();
    const navigate = useNavigate();
    const [project, setProject] = useState(null);
    const [loading, setLoading] = useState(true);
    const [documents, setDocuments] = useState([]);
    const [requirements, setRequirements] = useState([]);
    const [requirementsCount, setRequirementsCount] = useState(0);
    const [uploadFile, setUploadFile] = useState(null);
    const [showUploadModal, setShowUploadModal] = useState(false);

    // Workflow steps state
    const [workflowSteps, setWorkflowSteps] = useState({
        ingest: { completed: false, label: 'Ingest Data' },
        extract: { completed: false, label: 'Extract Requirements' },
        generate: { completed: false, label: 'Generate BRD' },
        export: { completed: false, label: 'Export Document' }
    });

    useEffect(() => {
        loadProject();
        loadDocuments();
        loadRequirements();
    }, [projectId]);

    const loadProject = async () => {
        try {
            const response = await projectsAPI.get(projectId);
            setProject(response.data);
        } catch (error) {
            console.error('Error loading project:', error);
            toast.error('Failed to load project');
        } finally {
            setLoading(false);
        }
    };

    const loadDocuments = async () => {
        try {
            const response = await documentsAPI.list(projectId);
            setDocuments(response.data);

            // Update workflow: if documents exist, generate step is complete
            if (response.data.length > 0) {
                setWorkflowSteps(prev => ({
                    ...prev,
                    generate: { ...prev.generate, completed: true }
                }));
            }
        } catch (error) {
            console.error('Error loading documents:', error);
        }
    };

    const loadRequirements = async () => {
        try {
            const response = await requirementsAPI.list(projectId);
            setRequirements(response.data.items || []);
            setRequirementsCount(response.data.total || 0);

            // Update workflow: if requirements exist, extract step is complete
            if (response.data.total > 0) {
                setWorkflowSteps(prev => ({
                    ...prev,
                    extract: { ...prev.extract, completed: true }
                }));
            }
        } catch (error) {
            console.error('Error loading requirements:', error);
        }
    };

    const handleFileUpload = async (e) => {
        e.preventDefault();
        if (!uploadFile) {
            toast.error('Please select a file');
            return;
        }

        try {
            toast.loading('Uploading file...', { id: 'upload' });
            await ingestionAPI.uploadFile(projectId, uploadFile);
            toast.success('File uploaded successfully!', { id: 'upload' });

            setShowUploadModal(false);
            setUploadFile(null);

            // Mark ingest step as complete
            setWorkflowSteps(prev => ({
                ...prev,
                ingest: { ...prev.ingest, completed: true }
            }));

            // DO NOT reload requirements after upload - they need to be extracted first
            // User must click "Extract Requirements" button next
        } catch (error) {
            console.error('Error uploading file:', error);
            const errorMsg = error.response?.data?.detail || 'Failed to upload file';
            toast.error(errorMsg, { id: 'upload' });
        }
    };

    const handleExtractRequirements = async () => {
        try {
            toast.loading('Extracting requirements...', { id: 'extract' });
            await ingestionAPI.extractRequirements(projectId);
            toast.success('Requirements extracted successfully!', { id: 'extract' });

            setWorkflowSteps(prev => ({
                ...prev,
                extract: { ...prev.extract, completed: true }
            }));

            loadRequirements();
        } catch (error) {
            console.error('Error extracting requirements:', error);
            const errorMsg = error.response?.data?.detail || 'Failed to extract requirements';
            toast.error(errorMsg, { id: 'extract' });
        }
    };

    const handleGenerateBRD = async () => {
        // Check if requirements exist
        if (requirementsCount === 0) {
            toast.error('No requirements found. Please ingest and extract data first.');
            return;
        }

        try {
            toast.loading('Generating BRD...', { id: 'generate' });
            await documentsAPI.generate(projectId);
            toast.success('BRD generated successfully!', { id: 'generate' });

            setWorkflowSteps(prev => ({
                ...prev,
                generate: { ...prev.generate, completed: true }
            }));

            loadDocuments();
        } catch (error) {
            console.error('Error generating BRD:', error);
            const errorMsg = error.response?.data?.detail || 'Failed to generate BRD';
            toast.error(errorMsg, { id: 'generate' });
        }
    };

    const handleExport = async (format) => {
        if (documents.length === 0) {
            toast.error('No documents to export. Generate a BRD first.');
            return;
        }

        try {
            toast.loading(`Exporting as ${format.toUpperCase()}...`, { id: 'export' });

            let response;
            let filename;

            if (format === 'pdf') {
                response = await documentsAPI.exportPdf(projectId);
                filename = `BRD_${project.name.replace(/\s+/g, '_')}.pdf`;
            } else if (format === 'word') {
                response = await documentsAPI.exportWord(projectId);
                filename = `BRD_${project.name.replace(/\s+/g, '_')}.docx`;
            } else if (format === 'excel') {
                response = await documentsAPI.exportExcel(projectId);
                filename = `Requirements_${project.name.replace(/\s+/g, '_')}.xlsx`;
            }

            // Create download link
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', filename);
            document.body.appendChild(link);
            link.click();
            link.remove();
            window.URL.revokeObjectURL(url);

            toast.success(`Exported as ${format.toUpperCase()}!`, { id: 'export' });

            setWorkflowSteps(prev => ({
                ...prev,
                export: { ...prev.export, completed: true }
            }));
        } catch (error) {
            console.error('Error exporting:', error);
            const errorMsg = error.response?.data?.detail || 'Failed to export';
            toast.error(errorMsg, { id: 'export' });
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <LoadingSpinner size="lg" />
            </div>
        );
    }

    if (!project) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="bg-white rounded-2xl p-6 shadow-lg">
                    <p className="text-gray-600">Project not found</p>
                    <AnimatedButton onClick={() => navigate('/dashboard')} className="mt-4">
                        Back to Dashboard
                    </AnimatedButton>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50">
            <Navbar />

            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mb-8"
                >
                    <button
                        onClick={() => navigate('/dashboard')}
                        className="flex items-center text-gray-600 hover:text-gray-900 transition-colors mb-4"
                    >
                        <ArrowLeft className="w-4 h-4 mr-2" />
                        Back to Projects
                    </button>

                    <h1 className="text-4xl font-bold text-gray-900 mb-2">{project.name}</h1>
                    <p className="text-gray-600">{project.description || 'No description'}</p>

                    {project.keywords && project.keywords.length > 0 && (
                        <div className="flex flex-wrap gap-2 mt-4">
                            {project.keywords.map((keyword, idx) => (
                                <span
                                    key={idx}
                                    className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm font-medium"
                                >
                                    {keyword}
                                </span>
                            ))}
                        </div>
                    )}
                </motion.div>

                {/* Workflow Steps */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 }}
                    className="mb-8"
                >
                    <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-200">
                        <h2 className="text-xl font-semibold mb-4 text-gray-900">Workflow Progress</h2>
                        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                            {Object.entries(workflowSteps).map(([key, step], index) => (
                                <div key={key} className="flex items-center space-x-3">
                                    <div className={`flex-shrink-0 ${step.completed ? 'text-green-600' : 'text-gray-400'}`}>
                                        {step.completed ? (
                                            <CheckCircle className="w-6 h-6" />
                                        ) : (
                                            <Circle className="w-6 h-6" />
                                        )}
                                    </div>
                                    <div className="flex-1">
                                        <p className={`text-sm font-medium ${step.completed ? 'text-gray-900' : 'text-gray-600'}`}>
                                            Step {index + 1}
                                        </p>
                                        <p className={`text-xs ${step.completed ? 'text-green-600' : 'text-gray-500'}`}>
                                            {step.label}
                                        </p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </motion.div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Actions Panel */}
                    <motion.div
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.2 }}
                        className="lg:col-span-1 space-y-6"
                    >
                        {/* Step 1: Ingest Data */}
                        <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-200">
                            <h2 className="text-lg font-semibold mb-3 text-gray-900 flex items-center">
                                <Database className="w-5 h-5 mr-2" />
                                Step 1: Ingest Data
                            </h2>
                            <AnimatedButton
                                onClick={() => setShowUploadModal(true)}
                                className="w-full justify-center"
                            >
                                <Upload className="w-4 h-4 mr-2" />
                                Upload File
                            </AnimatedButton>
                        </div>

                        {/* Step 2: Extract Requirements */}
                        <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-200">
                            <h2 className="text-lg font-semibold mb-3 text-gray-900 flex items-center">
                                <FileSearch className="w-5 h-5 mr-2" />
                                Step 2: Extract
                            </h2>
                            <div className="mb-3">
                                <p className="text-sm text-gray-600">
                                    Requirements: <span className="text-gray-900 font-semibold">{requirementsCount}</span>
                                </p>
                            </div>
                            <AnimatedButton
                                onClick={handleExtractRequirements}
                                variant="secondary"
                                className="w-full justify-center"
                                disabled={!workflowSteps.ingest.completed}
                            >
                                <FileSearch className="w-4 h-4 mr-2" />
                                Extract Requirements
                            </AnimatedButton>
                            {!workflowSteps.ingest.completed && (
                                <p className="text-xs text-yellow-600 mt-2 flex items-center">
                                    <AlertCircle className="w-3 h-3 mr-1" />
                                    Upload data first
                                </p>
                            )}
                        </div>

                        {/* Step 3: Generate BRD */}
                        <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-200">
                            <h2 className="text-lg font-semibold mb-3 text-gray-900 flex items-center">
                                <Sparkles className="w-5 h-5 mr-2" />
                                Step 3: Generate BRD
                            </h2>
                            <AnimatedButton
                                onClick={handleGenerateBRD}
                                className="w-full justify-center"
                                disabled={requirementsCount === 0}
                            >
                                <Sparkles className="w-4 h-4 mr-2" />
                                Generate BRD
                            </AnimatedButton>
                            {requirementsCount === 0 && (
                                <p className="text-xs text-yellow-600 mt-2 flex items-center">
                                    <AlertCircle className="w-3 h-3 mr-1" />
                                    Extract requirements first
                                </p>
                            )}
                        </div>

                        {/* Step 4: Export */}
                        <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-200">
                            <h2 className="text-lg font-semibold mb-3 text-gray-900 flex items-center">
                                <Download className="w-5 h-5 mr-2" />
                                Step 4: Export
                            </h2>
                            <div className="space-y-2">
                                <AnimatedButton
                                    variant="secondary"
                                    onClick={() => handleExport('pdf')}
                                    className="w-full justify-center"
                                    disabled={documents.length === 0}
                                >
                                    <Download className="w-4 h-4 mr-2" />
                                    Export PDF
                                </AnimatedButton>
                                <AnimatedButton
                                    variant="secondary"
                                    onClick={() => handleExport('word')}
                                    className="w-full justify-center"
                                    disabled={documents.length === 0}
                                >
                                    <Download className="w-4 h-4 mr-2" />
                                    Export Word
                                </AnimatedButton>
                                <AnimatedButton
                                    variant="secondary"
                                    onClick={() => handleExport('excel')}
                                    className="w-full justify-center"
                                    disabled={documents.length === 0}
                                >
                                    <Download className="w-4 h-4 mr-2" />
                                    Export Excel
                                </AnimatedButton>
                            </div>
                            {documents.length === 0 && (
                                <p className="text-xs text-yellow-600 mt-2 flex items-center">
                                    <AlertCircle className="w-3 h-3 mr-1" />
                                    Generate BRD first
                                </p>
                            )}
                        </div>
                    </motion.div>

                    {/* Main Content Panel */}
                    <motion.div
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.2 }}
                        className="lg:col-span-2 space-y-6"
                    >
                        {/* Requirements Section */}
                        <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-200">
                            <h2 className="text-xl font-semibold mb-4 text-gray-900">Requirements ({requirementsCount})</h2>

                            {requirements.length === 0 ? (
                                <div className="text-center py-12">
                                    <FileSearch className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                                    <p className="text-gray-600 mb-2">No requirements found</p>
                                    <p className="text-gray-500 text-sm">
                                        Upload data and extract requirements to get started
                                    </p>
                                </div>
                            ) : (
                                <div className="space-y-3 max-h-96 overflow-y-auto">
                                    {requirements.slice(0, 10).map((req) => (
                                        <motion.div
                                            key={req.id}
                                            whileHover={{ scale: 1.01 }}
                                            className="p-4 bg-gray-50 rounded-lg border border-gray-200"
                                        >
                                            <div className="flex items-start justify-between">
                                                <div className="flex-1">
                                                    <div className="flex items-center gap-2 mb-2">
                                                        <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs font-medium">
                                                            {req.type || 'Requirement'}
                                                        </span>
                                                        <span className={`px-2 py-1 rounded text-xs font-medium ${req.priority === 'high' ? 'bg-red-100 text-red-700' :
                                                            req.priority === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                                                                'bg-green-100 text-green-700'
                                                            }`}>
                                                            {req.priority || 'medium'}
                                                        </span>
                                                        {req.confidence && (
                                                            <span className="text-xs text-gray-500">
                                                                {Math.round(req.confidence * 100)}% confidence
                                                            </span>
                                                        )}
                                                    </div>
                                                    <p className="text-sm text-gray-700">
                                                        {req.content}
                                                    </p>
                                                </div>
                                            </div>
                                        </motion.div>
                                    ))}
                                    {requirements.length > 10 && (
                                        <p className="text-center text-sm text-gray-500">
                                            Showing 10 of {requirementsCount} requirements
                                        </p>
                                    )}
                                </div>
                            )}
                        </div>

                        {/* Documents Section */}
                        <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-200">
                            <h2 className="text-xl font-semibold mb-4 text-gray-900">Generated Documents ({documents.length})</h2>

                            {documents.length === 0 ? (
                                <div className="text-center py-12">
                                    <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                                    <p className="text-gray-600 mb-2">No documents yet</p>
                                    <p className="text-gray-500 text-sm">
                                        Generate a BRD to get started
                                    </p>
                                </div>
                            ) : (
                                <div className="space-y-3">
                                    {documents.map((doc) => (
                                        <motion.div
                                            key={doc.id}
                                            whileHover={{ scale: 1.02 }}
                                            className="p-4 bg-gray-50 rounded-lg border border-gray-200 cursor-pointer hover:border-blue-300 hover:shadow-md transition-all"
                                        >
                                            <div className="flex items-start justify-between">
                                                <div className="flex-1">
                                                    <h3 className="font-semibold text-gray-900 mb-1">
                                                        Business Requirements Document
                                                    </h3>
                                                    <p className="text-sm text-gray-600 line-clamp-2">
                                                        {doc.content?.title || 'BRD Document'}
                                                    </p>
                                                    <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
                                                        <span>Version {doc.version || '1'}</span>
                                                        <span>
                                                            {new Date(doc.created_at).toLocaleDateString()}
                                                        </span>
                                                    </div>
                                                </div>
                                                <FileText className="w-8 h-8 text-blue-600 ml-4" />
                                            </div>
                                        </motion.div>
                                    ))}
                                </div>
                            )}
                        </div>
                    </motion.div>
                </div>
            </div>

            {/* Upload File Modal */}
            {showUploadModal && (
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="fixed inset-0 bg-gray-900/50 backdrop-blur-sm flex items-center justify-center p-4 z-50"
                    onClick={() => setShowUploadModal(false)}
                >
                    <motion.div
                        initial={{ scale: 0.9, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        exit={{ scale: 0.9, opacity: 0 }}
                        onClick={(e) => e.stopPropagation()}
                        className="w-full max-w-md"
                    >
                        <div className="bg-white rounded-2xl p-6 shadow-xl">
                            <h2 className="text-2xl font-bold mb-6 text-gray-900">Upload File</h2>

                            <form onSubmit={handleFileUpload} className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                        Select File
                                    </label>
                                    <input
                                        type="file"
                                        onChange={(e) => setUploadFile(e.target.files[0])}
                                        className="w-full px-4 py-3 bg-gray-50 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
                                        accept=".txt,.pdf,.doc,.docx,.json"
                                    />
                                    <p className="text-xs text-gray-500 mt-2">
                                        Supported formats: TXT, PDF, DOC, DOCX, JSON
                                    </p>
                                </div>

                                <div className="flex space-x-3 pt-4">
                                    <AnimatedButton type="submit" className="flex-1">
                                        <Upload className="w-4 h-4 mr-2" />
                                        Upload
                                    </AnimatedButton>
                                    <AnimatedButton
                                        type="button"
                                        variant="secondary"
                                        onClick={() => {
                                            setShowUploadModal(false);
                                            setUploadFile(null);
                                        }}
                                        className="flex-1"
                                    >
                                        Cancel
                                    </AnimatedButton>
                                </div>
                            </form>
                        </div>
                    </motion.div>
                </motion.div>
            )}
        </div>
    );
}
