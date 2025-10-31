import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import './Chatbot.css'; 

const API_CHATBOT_URL = 'http://localhost:8000/api/chatbot';

function Chatbot() {
  const [isOpen, setIsOpen] = useState(false);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  const [messages, setMessages] = useState([
    {
      sender: 'bot',
      type: 'text',
      content: '안녕하세요! 강원대학교 정보 챗봇입니다. 무엇이 궁금하신가요?'
    }
  ]);
  
  const messageListRef = useRef(null);
  useEffect(() => {
    if (messageListRef.current) {
      messageListRef.current.scrollTop = messageListRef.current.scrollHeight;
    }
  }, [messages]);

  const toggleChat = () => {
    setIsOpen(prev => !prev);
  };

  const handleSend = async (e) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    const userQuery = inputValue;

    setMessages(prev => [
      ...prev,
      { sender: 'user', type: 'text', content: userQuery }
    ]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await axios.post(API_CHATBOT_URL, {
        query: userQuery
      });

      if (response.data && response.data.answer) {
        setMessages(prev => [
          ...prev,
          {
            sender: 'bot',
            type: 'text',
            content: response.data.answer 
          }
        ]);
        
        if (response.data.sources && response.data.sources.length > 0) {
           setMessages(prev => [
            ...prev,
            {
              sender: 'bot',
              type: 'response',
              content: response.data.sources 
            }
          ]);
        }
      } else {
         setMessages(prev => [
          ...prev,
          {
            sender: 'bot',
            type: 'text',
            content: '죄송합니다. 관련 정보를 찾지 못했습니다.'
          }
        ]);
      }
    } catch (error) {
      console.error("챗봇 API 오류:", error);
      setMessages(prev => [
        ...prev,
        {
          sender: 'bot',
          type: 'text',
          content: '오류가 발생했습니다. 잠시 후 다시 시도해주세요.'
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      <div className="chatbot-icon" onClick={toggleChat}>
        {isOpen ? '✕' : '💬'}
      </div>

      <div className={`chatbot-window ${isOpen ? 'open' : ''}`}>
        <div className="chatbot-header">
          강원대 AI 챗봇
        </div>
        
        <div className="message-list" ref={messageListRef}>
          {messages.map((msg, index) => (
            <div key={index} className={`message ${msg.sender}`}>
              
              {/* 봇 응답 렌더링 로직 */}
              {msg.type === 'response' ? (
                <div>
                  <p style={{fontSize: '0.9em', color: '#666', marginTop: '-5px', marginBottom: '8px'}}>
                    ↓ 답변의 근거가 된 자료입니다.
                  </p>
                  {msg.content.map(item => (
                    <div key={item.post_id} className="bot-response-card">
                      <Link to={`/posts/${item.post_id}`}>
                        [{item.post_title}]
                      </Link>
                      
                      <p>
                        {item.text.length > 150 
                          ? `${item.text.substring(0, 150)}...` 
                          : item.text}
                      </p>
                    </div>
                  ))}
                </div>
              ) : (
                <div style={{ whiteSpace: 'pre-wrap' }}>
                  <ReactMarkdown>{msg.content}</ReactMarkdown>
                </div>
              )}
            </div>
          ))}

          {isLoading && (
            <div className="message bot loading">
              <div className="spinner dot1"></div>
              <div className="spinner dot2"></div>
              <div className="spinner dot3"></div>
            </div>
          )}
        </div>
        
        <form className="chatbot-input-form" onSubmit={handleSend}>
          <input
            type="text"
            placeholder="질문을 입력하세요..."
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            disabled={isLoading}
          />
          <button type="submit" disabled={isLoading}>
            &rarr;
          </button>
        </form>
        
      </div>
    </div>
  );
}

export default Chatbot;