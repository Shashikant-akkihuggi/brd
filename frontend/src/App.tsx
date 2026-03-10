import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import ProjectList from './components/ProjectList'
import ProjectDetail from './components/ProjectDetail'
import CreateProject from './components/CreateProject'

function App() {
    return (
        <BrowserRouter>
            <div className="app">
                <nav className="navbar">
                    <h1>BRD Generation Platform</h1>
                    <Link to="/">Projects</Link>
                    <Link to="/create">New Project</Link>
                </nav>
                <main className="container">
                    <Routes>
                        <Route path="/" element={<ProjectList />} />
                        <Route path="/create" element={<CreateProject />} />
                        <Route path="/project/:id" element={<ProjectDetail />} />
                    </Routes>
                </main>
            </div>
        </BrowserRouter>
    )
}

export default App
