import React from 'react';
import { Routes, Route } from 'react-router-dom';
import HomePage from './pages/HomePage';
import PostDetailPage from './pages/PostDetailPage';

function App() {
  return (
    <div className="App">
      <Routes>
        <Route path="/" element={<HomePage />} />
        
        <Route path="/posts/:postId" element={<PostDetailPage />} />
      </Routes>
    </div>
  );
}

export default App;