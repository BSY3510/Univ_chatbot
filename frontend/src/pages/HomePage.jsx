import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Link, useSearchParams } from 'react-router-dom';

const API_URL = 'http://localhost:8000/api/posts';
const POSTS_PER_PAGE = 20;
const PAGES_PER_GROUP = 10;

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

  const [searchParams, setSearchParams] = useSearchParams();

  const currentPage = parseInt(searchParams.get('page') || '1', 10);
  const selectedDept = searchParams.get('department') || 
                       localStorage.getItem('selectedDept') || 
                       '전체';

  const startPage = Math.floor((currentPage - 1) / PAGES_PER_GROUP) * PAGES_PER_GROUP + 1;

  useEffect(() => {
    const fetchPosts = async () => {
      try {
        setLoading(true);
        setError(null);

        const params = {
          limit: POSTS_PER_PAGE,
          skip: (currentPage - 1) * POSTS_PER_PAGE
        };
        
        if (selectedDept !== '전체') {
          params.department = selectedDept;
        }

        const response = await axios.get(API_URL, { params });
        setPosts(response.data);

      } catch (err) {
        setError('데이터를 불러오는 데 실패했습니다.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchPosts();
  }, [selectedDept, currentPage]);

  const updateSearchParams = (newPage, newDept) => {
    const params = {};

    if (newPage > 1) {
        params.page = newPage;
    }

    if (newDept && newDept !== '전체') {
        params.department = newDept;
    }

    setSearchParams(params);
  }

  const handleDeptClick = (dept) => {
    updateSearchParams(1, dept);
    localStorage.setItem('selectedDept', dept);
  };

  const handlePageClick = (pageNumber) => {
    updateSearchParams(pageNumber, selectedDept);
  };

  const handlePrevGroup = () => {
    const prevGroupStartPage = Math.max(startPage - PAGES_PER_GROUP, 1);
    updateSearchParams(prevGroupStartPage, selectedDept);
  };

  const handleNextGroup = () => {
    if (posts.length === POSTS_PER_PAGE) {
      const nextGroupStartPage = startPage + PAGES_PER_GROUP;
      updateSearchParams(nextGroupStartPage, selectedDept);
    }
  };

  const renderPageNumbers = () => {
    return Array.from({ length: PAGES_PER_GROUP }, (_, i) => {
      const pageNumber = startPage + i;

      return (
        <button
          key={pageNumber}
          onClick={() => handlePageClick(pageNumber)}
          disabled={loading}
          style={{
            margin: '0 5px',
            fontWeight: currentPage === pageNumber ? 'bold' : 'normal',
            color: 'black',
            backgroundColor: currentPage === pageNumber ? '#e0e0e0' : 'white'
          }}
        >
          {pageNumber}
        </button>
      );
    });
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
              
              <Link to={`/posts/${post.id}`}>
                {post.title}
              </Link>
              
              <span style={{ color: '#888', marginLeft: '10px' }}>
                ({post.created_at})
              </span>
            </li>
          ))}
          {posts.length === 0 && <li>표시할 게시물이 없습니다.</li>}
        </ul>
      )}

      <hr />
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', margin: '20px' }}>
        <button 
          onClick={handlePrevGroup}
          disabled={startPage === 1 || loading}
        >
          &lt;&lt; 이전
        </button>
 
        <div style={{ margin: '0 10px' }}>
          {renderPageNumbers()}
        </div>
        
        <button 
          onClick={handleNextGroup}
          disabled={posts.length < POSTS_PER_PAGE || loading}
        >
          다음 &gt;&gt;
        </button>
      </div>
    </div>
  );
}

export default HomePage;