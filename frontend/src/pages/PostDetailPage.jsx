import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/posts';

function PostDetailPage() {
  const { postId } = useParams();
  
  const [post, setPost] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [recommendations, setRecommendations] = useState([]);
  const [loadingRecs, setLoadingRecs] = useState(true);

  useEffect(() => {
    const fetchPostDetail = async () => {
      try {
        setLoading(true);
        const response = await axios.get(`${API_BASE_URL}/${postId}`);
        setPost(response.data);
      } catch (err) {
        setError('게시물을 불러오는 데 실패했습니다.');
      } finally {
        setLoading(false);
      }
    };
    
    fetchPostDetail();
  }, [postId]);

  useEffect(() => {
    const fetchRecommendations = async () => {
      try {
        setLoadingRecs(true);
        const response = await axios.get(`${API_BASE_URL}/${postId}/similar`);
        setRecommendations(response.data);
      } catch (err) {
        console.error("추천 게시물 로딩 실패:", err);
        setRecommendations([]);
      } finally {
        setLoadingRecs(false);
      }
    };
    
    fetchRecommendations();
  }, [postId]);

  if (loading) return <div>로딩 중...</div>;
  if (error) return <div>{error}</div>;
  if (!post) return <div>게시물이 없습니다.</div>;

  return (
    <div style={{ padding: '20px' }}>
      <Link to="/">&larr; 목록으로 돌아가기</Link>

      <h1>{post.title}</h1>
      <div style={{ color: '#555', marginBottom: '20px' }}>
        <span>[{post.department}]</span> | 
        <span>{post.author}</span> | 
        <span>{post.created_at}</span>
      </div>
      <a href={post.url} target="_blank" rel="noopener noreferrer">
        [원문 보러가기]
      </a>
      
      <div style={{ marginTop: '20px', padding: '10px', border: '1px solid #eee', background: '#f9f9f9' }}>
        <pre style={{ whiteSpace: 'pre-wrap', wordWrap: 'break-word' }}>
          {post.content}
        </pre>
      </div>

      <div style={{ marginTop: '40px' }}>
        <h3>함께 보면 좋은 글 (AI 추천)</h3>
        {loadingRecs ? (
          <div>추천 게시물 로딩 중...</div>
        ) : (
          <ul>
            {recommendations.length > 0 ? (
              recommendations.map(recPost => (
                <li key={recPost.id}>
                  <Link to={`/posts/${recPost.id}`}>
                    [{recPost.department}] {recPost.title}
                  </Link>
                </li>
              ))
            ) : (
              <li>추천 게시물이 없습니다.</li>
            )}
          </ul>
        )}
      </div>
    </div>
  );
}

export default PostDetailPage;