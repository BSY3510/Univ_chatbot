import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = 'http://localhost:8000/api/posts';

function HomePage() {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchPosts = async () => {
      try {
        setLoading(true);
        setError(null);

        const response = await axios.get(API_URL);

        setPosts(response.data);
      } catch (err) {
        setError('데이터를 불러오는 데 실패했습니다.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchPosts();
  }, []);

  if (loading) {
    return <div>로딩 중...</div>;
  }

  if (error) {
    return <div>{error}</div>;
  }

  return (
    <div>
      <h1>강원대 공지사항</h1>
      <hr />
      <ul>
        {posts.map(post => (
          <li key={post.id} style={{ marginBottom: '10px' }}>
            <strong>[{post.department}]</strong> {/* 학과 표시 */}
            <a href={post.url} target="_blank" rel="noopener noreferrer">
              {post.title} {/* 제목 표시 */}
            </a>
            <span style={{ color: '#888', marginLeft: '10px' }}>
              ({post.created_at}) {/* 작성일 표시 */}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default HomePage;