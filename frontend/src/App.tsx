import React from 'react';
import { BrowserRouter, Routes, Route, Navigate, Link } from 'react-router-dom';
import { Shield, BookOpen, MessageSquare, Search, FileText, BarChart3, Settings } from 'lucide-react';

// Simplified Navigation Bar Component
const Sidebar = () => (
    <div className="w-64 bg-slate-900 text-slate-100 flex flex-col h-screen border-r border-slate-800">
        <div className="p-6 flex items-center gap-3 border-b border-slate-800">
            <Shield className="w-8 h-8 text-indigo-400" />
            <span className="font-bold text-xl tracking-tight">RAGForge</span>
        </div>
        <nav className="flex-1 p-4 space-y-1">
            <Link to="/chat" className="flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-slate-800 text-slate-300 hover:text-white transition">
                <MessageSquare className="w-5 h-5 text-indigo-400" /> AI Research Chat
            </Link>
            <Link to="/documents" className="flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-slate-800 text-slate-300 hover:text-white transition">
                <FileText className="w-5 h-5 text-emerald-400" /> Knowledge Sources
            </Link>
            <Link to="/research" className="flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-slate-800 text-slate-300 hover:text-white transition">
                <BookOpen className="w-5 h-5 text-amber-400" /> Research Mode
            </Link>
            <Link to="/search" className="flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-slate-800 text-slate-300 hover:text-white transition">
                <Search className="w-5 h-5 text-sky-400" /> Semantic Search
            </Link>
            <Link to="/evaluation" className="flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-slate-800 text-slate-300 hover:text-white transition">
                <BarChart3 className="w-5 h-5 text-purple-400" /> RAG Evaluation
            </Link>
        </nav>
    </div>
);

export function App() {
    return (
        <BrowserRouter>
            <div className="flex h-screen bg-slate-950 font-sans antialiased text-slate-100">
                <Sidebar />
                <main className="flex-1 overflow-y-auto p-8">
                    <Routes>
                        <Route path="/" element={<Navigate to="/chat" replace />} />
                        <Route path="/chat" element={
                            <div className="max-w-4xl mx-auto bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl">
                                <h1 className="text-2xl font-bold mb-4">Grounded Research Chat</h1>
                                <p className="text-slate-400">Select a collection and ask questions grounded directly in your uploaded literature.</p>
                            </div>
                        } />
                        <Route path="/documents" element={
                            <div className="max-w-4xl mx-auto bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl">
                                <h1 className="text-2xl font-bold mb-4">Document Management</h1>
                                <p className="text-slate-400">Upload PDF, DOCX, TXT, or MD files into collections for ingestion and vector indexing.</p>
                            </div>
                        } />
                    </Routes>
                </main>
            </div>
        </BrowserRouter>
    );
}

export default App;