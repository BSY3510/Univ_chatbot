import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = 'http://localhost:8000/api/posts';

const DEPARTMENTS = [
  '전체',
  '컴퓨터공학과',
  '전기전자공학과',
  '전자공학과',
  'AI융합학과',
  '디지털밀리터리학과'
];

function HomePage() {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [selectedDept, setSelectedDept] = useState(
    () => localStorage.getItem('selectedDept') || '전체'
  );

  useEffect(() => {
    const fetchPosts = async () => {
      try {
        setLoading(true);
        setError(null);

        const params = {
          limit: 20
        };
        
        if (selectedDept !== '전체') {
          params.department = selectedDept;
        }

        const response = await axios.get(API_URL, { params });
        setPosts(response.data);
        
        localStorage.setItem('selectedDept', selectedDept);

      } catch (err) {
        setError('데이터를 불러오는 데 실패했습니다.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchPosts();
  }, [selectedDept]);

  const handleDeptClick = (dept) => {
    setSelectedDept(dept);
  };

  return (
    <div>
      <h1>강원대 공지사항</h1>
      
      <div>
        {DEPARTMENTS.map(dept => (
          <button
            key={dept}
            onClick={() => handleDeptClick(dept)}
            style={{
              margin: '5px',
              fontWeight: selectedDept === dept ? 'bold' : 'normal',
              backgroundColor: selectedDept === dept ? '#e0e0e0' : 'white'
            }}
          >
            {dept}
          </button>
        ))}
      </div>
      <hr />

      {loading && <div>로딩 중...</div>}
      {error && <div>{error}</div>}
      {!loading && !error && (
        <ul>
          {posts.map(post => (
            <li key={post.id} style={{ marginBottom: '10px' }}>
              <strong>[{post.department}]</strong>
              <a href={post.url} target="_blank" rel="noopener noreferrer">
                {post.title}
              </a>
              <span style={{ color: '#888', marginLeft: '10px' }}>
                ({post.created_at})
              </span>
            </li>
          ))}
          {posts.length === 0 && <li>표시할 게시물이 없습니다.</li>}
        </ul>
      )}
    </div>
  );
}

export default HomePage;