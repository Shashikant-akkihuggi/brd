import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { projectsApi, Project } from '../api'

export default function ProjectList() {
    const [projects, setProjects] = useState<Project[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState('')

    useEffect(() => {
        loadProjects()
    }, [])

    const loadProjects = async () => {
        try {
            const response = await projectsApi.list()
            setProjects(response.data)
        } catch (err: any) {
            setError(err.message)
        } finally {
            setLoading(false)
        }
    }

    const handleDelete = async (id: number) => {
        if (!confirm('Delete this project?')) return

        try {
            await projectsApi.delete(id)
            loadProjects()
        } catch (err: any) {
            setError(err.message)
        }
    }

    if (loading) return <div className="loading">Loading projects...</div>
    if (error) return <div className="error">{error}</div>

    return (
        <div>
            <h2>Projects</h2>
            {projects.length === 0 ? (
                <p>No projects yet. <Link to="/create">Create one</Link></p>
            ) : (
                <div className="grid">
                    {projects.map(project => (
                        <div key={project.id} className="card">
                            <h3>{project.name}</h3>
                            <p>{project.description}</p>
                            {project.keywords && (
                                <div style={{ marginTop: '0.5rem' }}>
                                    {project.keywords.map(kw => (
                                        <span key={kw} style={{
                                            background: '#e8f4f8',
                                            padding: '0.25rem 0.5rem',
                                            borderRadius: '4px',
                                            marginRight: '0.5rem',
                                            fontSize: '0.875rem'
                                        }}>
                                            {kw}
                                        </span>
                                    ))}
                                </div>
                            )}
                            <div style={{ marginTop: '1rem', display: 'flex', gap: '0.5rem' }}>
                                <Link to={`/project/${project.id}`} className="btn btn-primary">
                                    View
                                </Link>
                                <button
                                    onClick={() => handleDelete(project.id)}
                                    className="btn btn-danger"
                                >
                                    Delete
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    )
}
