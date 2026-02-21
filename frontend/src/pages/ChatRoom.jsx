// src/pages/ChatRoom.jsx
import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import styled from 'styled-components';

const Container = styled.div`
  background: #111;
  color: #f0f0f0;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  font-family: 'Inter', 'Segoe UI', sans-serif;
  direction: rtl;
`;

const Header = styled.div`
  text-align: center;
  padding: 20px 15px 10px;
`;

const Title = styled.h1`
  font-size: 2rem;
  font-weight: 800;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 8px;
`;

const StatusBox = styled.div`
  background: #1e1e1e;
  border: 1px solid #333;
  border-radius: 8px;
  padding: 15px;
  margin: 10px auto;
  max-width: 500px;
  text-align: center;
`;

const MemberList = styled.ul`
  margin-top: 10px;
  padding: 8px;
  background: #282828;
  border-radius: 6px;
  max-height: 120px;
  overflow-y: auto;
  text-align: right;
  list-style: none;

  & li {
    padding: 4px 0;
    border-bottom: 1px dotted #444;
    font-size: 0.9rem;
  }

  & li:last-child {
    border-bottom: none;
  }
`;

const ChatWrapper = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 0 15px 15px;
  overflow: hidden;
`;

const ChatHistory = styled.div`
  flex: 1;
  overflow-y: auto;
  background: #1a1a1a;
  border: 1px solid #333;
  border-radius: 12px;
  padding: 15px;
  margin-bottom: 15px;
  display: flex;
  flex-direction: column;
`;

const MessageContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 12px;
`;

const MessageItem = styled.div`
  display: flex;
  width: 100%;
  justify-content: ${props => (props.isSelf ? 'flex-start' : 'flex-end')};
`;

const BubbleWrapper = styled.div`
  max-width: 85%;
  display: flex;
  flex-direction: column;
`;

const Bubble = styled.div`
  padding: 10px 15px;
  border-radius: 18px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.2);
  word-break: break-word;
  background: ${props => (props.isSelf ? '#3c598e' : '#252525')};
  color: ${props => (props.isSelf ? 'white' : '#f0f0f0')};
  border-bottom-${props => (props.isSelf ? 'left' : 'right')}-radius: 4px;
`;

const Sender = styled.span`
  font-weight: bold;
  color: #a2d4ba;
  margin-bottom: 3px;
  font-size: 0.9rem;
  display: block;
`;

const Meta = styled.div`
  display: flex;
  justify-content: space-between;
  margin-top: 5px;
  font-size: 0.75rem;
  color: #999;
`;

const InputArea = styled.div`
  padding: 10px 0;
  background: #111;
  border-top: 1px solid #222;
  flex-shrink: 0;
`;

const Form = styled.form`
  display: flex;
  gap: 10px;
  align-items: center;
`;

const Textarea = styled.textarea`
  flex: 1;
  padding: 12px 16px;
  border-radius: 20px;
  border: 1px solid #333;
  background: #1a1a1a;
  color: white;
  font-size: 1rem;
  resize: none;
  min-height: 48px;
  max-height: 120px;
  outline: none;

  &:focus {
    border-color: #667eea;
  }
`;

const SendButton = styled.button`
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 12px 24px;
  font-size: 1rem;
  font-weight: 600;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s;

  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
  }
`;

const ExitButton = styled.button`
  background: #764ba2;
  color: white;
  border: none;
  padding: 10px 20px;
  font-size: 0.95rem;
  border-radius: 8px;
  cursor: pointer;
  margin: 15px auto;
  display: block;
  width: 50%;
  max-width: 300px;
  box-shadow: 0 4px 10px rgba(118, 75, 162, 0.3);

  &:hover {
    background: #5a3d8a;
  }
`;

function ChatRoom() {
  const { roomId } = useParams();
  const navigate = useNavigate();

  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [membersCount, setMembersCount] = useState(1);
  const [activeGuests, setActiveGuests] = useState([]);
  const [currentUser, setCurrentUser] = useState('شما'); // بعداً از context بگیر

  const chatRef = useRef(null);
  const wsRef = useRef(null);

  // اسکرول به پایین هنگام اضافه شدن پیام
  useEffect(() => {
    if (chatRef.current) {
      chatRef.current.scrollTop = chatRef.current.scrollHeight;
    }
  }, [messages]);

  // اتصال به WebSocket
  useEffect(() => {
    if (!roomId) return;

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/chat/${roomId}/`;

    wsRef.current = new WebSocket(wsUrl);

    wsRef.current.onopen = () => {
      console.log('وب‌سوکت متصل شد');
    };

    wsRef.current.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        const msg = {
          content: data.message || '',
          sender: data.sender || 'ناشناس',
          created_at: data.created_at || new Date().toISOString(),
        };

        setMessages((prev) => [
          ...prev,
          { ...msg, isSelf: msg.sender === currentUser },
        ]);
      } catch (err) {
        console.error('خطا در پردازش پیام:', err);
      }
    };

    wsRef.current.onclose = () => {
      console.log('وب‌سوکت قطع شد');
    };

    return () => {
      wsRef.current?.close();
    };
  }, [roomId, currentUser]);

  const sendMessage = (e) => {
    e.preventDefault();
    if (!input.trim() || !wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      return;
    }

    wsRef.current.send(JSON.stringify({ message: input.trim() }));
    setInput('');
  };

  const handleExit = () => {
    if (wsRef.current) wsRef.current.close();
    navigate('/rooms');
  };

  return (
    <Container>
      <Header>
        <Title>چت روم: {roomId?.slice(0, 8)}...</Title>
        <p style={{ fontSize: '0.9rem', opacity: 0.9 }}>
          شما با نام: <strong>{currentUser}</strong> وارد شدید
        </p>
      </Header>

      <StatusBox>
        <strong>اعضای فعال: {membersCount} نفر</strong>
        <MemberList>
          <p style={{ color: '#999', marginBottom: 5 }}>لیست مهمانان:</p>
          {activeGuests.length > 0 ? (
            activeGuests.map((guest, i) => <li key={i}>{guest}</li>)
          ) : (
            <li>مهمان فعال دیگری نیست</li>
          )}
        </MemberList>
      </StatusBox>

      <ChatWrapper>
        <ChatHistory ref={chatRef}>
          <MessageContainer>
            {messages.length === 0 ? (
              <p style={{ color: '#777', textAlign: 'center', marginTop: 'auto' }}>
                هنوز پیامی ارسال نشده است...
              </p>
            ) : (
              messages.map((msg, idx) => (
                <MessageItem key={idx} isSelf={msg.isSelf}>
                  <BubbleWrapper>
                    {!msg.isSelf && <Sender>{msg.sender}:</Sender>}
                    <Bubble isSelf={msg.isSelf}>
                      {msg.content}
                    </Bubble>
                    <Meta>
                      <span>
                        {new Date(msg.created_at).toLocaleTimeString('fa-IR', {
                          hour: '2-digit',
                          minute: '2-digit',
                        })}
                      </span>
                    </Meta>
                  </BubbleWrapper>
                </MessageItem>
              ))
            )}
          </MessageContainer>
        </ChatHistory>

        <InputArea>
          <Form onSubmit={sendMessage}>
            <Textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="پیام خود را بنویسید..."
              rows={1}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  sendMessage(e);
                }
              }}
            />
            <SendButton type="submit">ارسال</SendButton>
          </Form>
        </InputArea>
      </ChatWrapper>

      <ExitButton onClick={handleExit}>خروج از روم</ExitButton>
    </Container>
  );
}

export default ChatRoom;