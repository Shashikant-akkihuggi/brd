import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { projectsApi } from '../api'

export default function CreateProject() {
    const navigate = useNavigate()
    const [formData, setFormData] = useState({
        name: '',
        description: '',
        keywords: '',
    })
    const [error, setError] = useState('')

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()

        try {
            const keywords = formData.keywords
                .split(',')
                .map(k => k.trim())
                .filter(k => k)

            await projectsApi.create({
                name: formData.name,
                description: formData.description,
                keywords: keywords.length > 0 ? keywords : null,
            })

            navigate('/')
        } catch (err: any) {
            setError(err.message)
        }
    }

    return (
        <div>
            <h2>Create New Project</h2>
            {error && <div className="error">{error}</div>}

            <form onSubmit={handleSubmit} className="card">
                <div className="form-group">
                    <label>Project Name *</label>
                    <input
                        type="text"
                        required
                        value={formData.name}
                        onChange={e => setFormData({ ...formData, name: e.target.value })}
                    />
                </div>

                <div className="form-group">
                    <label>Description</label>
                    <textarea
                        value={formData.description}
                        onChange={e => setFormData({ ...formData, description: e.target.value })}
                    />
                </div>

                <div className="form-group">
                    <label>Keywords (comma-separated)</label>
                    <input
                        type="text"
                        placeholder="e.g., authentication, payment, dashboard"
                        value={formData.keywords}
                        onChange={e => setFormData({ ...formData, keywords: e.target.value })}
                    />
                </div>

                <button type="submit" className="btn btn-primary">
                    Create Project
                </button>
            </form>
        </div>
    )
}
