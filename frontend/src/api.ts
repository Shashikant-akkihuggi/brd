import axios from 'axios'

const api = axios.create({
    baseURL: '/api',
    headers: {
        'Content-Type': 'application/json',
    },
})

export interface Project {
    id: number
    name: string
    description?: string
    keywords?: string[]
    created_at: string
}

export interface Document {
    id: number
    project_id: number
    version: number
    content: any
    created_at: string
}

export const projectsApi = {
    list: () => api.get<Project[]>('/projects'),
    get: (id: number) => api.get<Project>(`/projects/${id}`),
    create: (data: any) => api.post<Project>('/projects', data),
    delete: (id: number) => api.delete(`/projects/${id}`),
}

export const documentsApi = {
    generate: (projectId: number) => api.post<Document>(`/documents/${projectId}/generate`),
    list: (projectId: number) => api.get<Document[]>(`/documents/${projectId}/documents`),
    get: (documentId: number) => api.get<Document>(`/documents/document/${documentId}`),
    export: (projectId: number, format: string) =>
        api.get(`/documents/${projectId}/export/${format}`, { responseType: 'blob' }),
    traceability: (projectId: number) => api.get(`/documents/${projectId}/traceability`),
}

export const ingestionApi = {
    uploadFile: (projectId: number, file: File) => {
        const formData = new FormData()
        formData.append('file', file)
        return api.post(`/ingestion/${projectId}/upload`, formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
        })
    },
    addManual: (projectId: number, data: any) =>
        api.post(`/ingestion/${projectId}/manual`, data),
    detectConflicts: (projectId: number) =>
        api.post(`/ingestion/${projectId}/detect-conflicts`),
}

export const editingApi = {
    edit: (documentId: number, instruction: string, section?: string) =>
        api.post<Document>(`/editing/${documentId}/edit`, { instruction, section }),
}

export default api
