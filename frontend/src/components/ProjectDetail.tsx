import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { projectsApi, documentsApi, ingestionApi, editingApi, Project, Document } from '../api'

export default function ProjectDetail() {
    const { id } = useParams<{ id: string }>()
    const projectId = parseInt(id!)

    const [project, setProject] = useState<Project | null>(null)
    const [documents, setDocuments] = useState<Document[]>([])
    const [currentDoc, setCurrentDoc] = useState<Document | null>(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState('')
    const [uploadFile, setUploadFile] = useState<File | null>(null)
    const [editInstruction, setEditInstruction] = useState('')
    const [manualContent, setManualContent] = useState('')

    useEffect(() => {
        loadProject()
        loadDocuments()
    }, [projectId])

    const loadProject = async () => {
        try {
            const response = await projectsApi.get(projectId)
            setProject(response.data)
        } catch (err: any) {
            setError(err.message)
        } finally {
            setLoading(false)
        }
    }

    const loadDocuments = async () => {
        try {
            const response = await documentsApi.list(projectId)
            setDocuments(response.data)
            if (response.data.length > 0) {
                setCurrentDoc(response.data[0])
            }
        } catch (err: any) {
            console.error('Error loading documents:', err)
        }
    }

    const handleFileUpload = async () => {
        if (!uploadFile) return

        try {
            await ingestionApi.uploadFile(projectId, uploadFile)
            alert('File uploaded and processed successfully')
            setUploadFile(null)
        } catch (err: any) {
            setError(err.message)
        }
    }

    const handleManualAdd = async () => {
        if (!manualContent.trim()) return

        try {
            await ingestionApi.addManual(projectId, {
                source_type: 'file',
                source_id: 'manual-entry',
                content: manualContent,
                timestamp: new Date().toISOString(),
            })
            alert('Content added successfully')
            setManualContent('')
        } catch (err: any) {
            setError(err.message)
        }
    }

    const handleGenerateBRD = async () => {
        try {
            setLoading(true)
            await documentsApi.generate(projectId)
            await loadDocuments()
            alert('BRD generated successfully')
        } catch (err: any) {
            setError(err.message)
        } finally {
            setLoading(false)
        }
    }

    const handleDetectConflicts = async () => {
        try {
            const response = await ingestionApi.detectConflicts(projectId)
            alert(`Detected ${response.data.count} conflicts`)
        } catch (err: any) {
            setError(err.message)
        }
    }

    const handleEdit = async () => {
        if (!currentDoc || !editInstruction.trim()) return

        try {
            const response = await editingApi.edit(currentDoc.id, editInstruction)
            setCurrentDoc(response.data)
            setEditInstruction('')
            await loadDocuments()
            alert('Document edited successfully')
        } catch (err: any) {
            setError(err.message)
        }
    }

    const handleExport = async (format: string) => {
        try {
            const response = await documentsApi.export(projectId, format)
            const url = window.URL.createObjectURL(new Blob([response.data]))
            const link = document.createElement('a')
            link.href = url
            link.setAttribute('download', `brd.${format}`)
            document.body.appendChild(link)
            link.click()
            link.remove()
        } catch (err: any) {
            setError(err.message)
        }
    }

    if (loading) return <div className="loading">Loading...</div>
    if (error) return <div className="error">{error}</div>
    if (!project) return <div>Project not found</div>

    return (
        <div>
            <h2>{project.name}</h2>
            <p>{project.description}</p>

            <div className="section">
                <h3>Data Ingestion</h3>
                <div className="card">
                    <div className="form-group">
                        <label>Upload File</label>
                        <input
                            type="file"
                            accept=".pdf,.doc,.docx,.txt"
                            onChange={e => setUploadFile(e.target.files?.[0] || null)}
                        />
                        <button
                            onClick={handleFileUpload}
                            disabled={!uploadFile}
                            className="btn btn-primary"
                            style={{ marginTop: '0.5rem' }}
                        >
                            Upload & Process
                        </button>
                    </div>

                    <div className="form-group">
                        <label>Manual Content Entry</label>
                        <textarea
                            value={manualContent}
                            onChange={e => setManualContent(e.target.value)}
                            placeholder="Paste email, meeting notes, or other content..."
                        />
                        <button
                            onClick={handleManualAdd}
                            disabled={!manualContent.trim()}
                            className="btn btn-primary"
                            style={{ marginTop: '0.5rem' }}
                        >
                            Add Content
                        </button>
                    </div>
                </div>
            </div>

            <div className="section">
                <h3>Actions</h3>
                <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                    <button onClick={handleGenerateBRD} className="btn btn-primary">
                        Generate BRD
                    </button>
                    <button onClick={handleDetectConflicts} className="btn btn-secondary">
                        Detect Conflicts
                    </button>
                    {currentDoc && (
                        <>
                            <button onClick={() => handleExport('json')} className="btn btn-secondary">
                                Export JSON
                            </button>
                            <button onClick={() => handleExport('markdown')} className="btn btn-secondary">
                                Export Markdown
                            </button>
                        </>
                    )}
                </div>
            </div>

            {currentDoc && (
                <>
                    <div className="section">
                        <h3>Edit Document (v{currentDoc.version})</h3>
                        <div className="card">
                            <div className="form-group">
                                <label>Natural Language Instruction</label>
                                <input
                                    type="text"
                                    value={editInstruction}
                                    onChange={e => setEditInstruction(e.target.value)}
                                    placeholder="e.g., Add a requirement about user authentication"
                                />
                                <button
                                    onClick={handleEdit}
                                    disabled={!editInstruction.trim()}
                                    className="btn btn-primary"
                                    style={{ marginTop: '0.5rem' }}
                                >
                                    Apply Edit
                                </button>
                            </div>
                        </div>
                    </div>

                    <div className="section">
                        <h3>Current BRD (Version {currentDoc.version})</h3>
                        <div className="card">
                            <pre style={{ whiteSpace: 'pre-wrap', fontSize: '0.875rem' }}>
                                {JSON.stringify(currentDoc.content, null, 2)}
                            </pre>
                        </div>
                    </div>
                </>
            )}

            {documents.length > 1 && (
                <div className="section">
                    <h3>Version History</h3>
                    <div className="card">
                        {documents.map(doc => (
                            <div
                                key={doc.id}
                                style={{
                                    padding: '0.5rem',
                                    cursor: 'pointer',
                                    background: doc.id === currentDoc?.id ? '#e8f4f8' : 'transparent'
                                }}
                                onClick={() => setCurrentDoc(doc)}
                            >
                                Version {doc.version} - {new Date(doc.created_at).toLocaleString()}
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    )
}
