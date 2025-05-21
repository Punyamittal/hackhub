// pages/index.js
import { useState, useEffect, useRef } from 'react';
import Head from 'next/head';
import styles from '../styles/Home.module.css';

export default function Home() {
  const [timeLeft, setTimeLeft] = useState({
    hours: 51,
    minutes: 0,
    seconds: 0
  });
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');
  const messagesEndRef = useRef(null);

  useEffect(() => {
    const timer = setInterval(() => {
      setTimeLeft(prev => {
        const totalSeconds = prev.hours * 3600 + prev.minutes * 60 + prev.seconds - 1;
        if (totalSeconds <= 0) {
          clearInterval(timer);
          return { hours: 0, minutes: 0, seconds: 0 };
        }
        return {
          hours: Math.floor(totalSeconds / 3600),
          minutes: Math.floor((totalSeconds % 3600) / 60),
          seconds: totalSeconds % 60
        };
      });
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (input.trim() === '') return;

    const userMessage = input;
    setInput('');
    const newMessages = [...messages, { role: 'user', content: userMessage }];
    setMessages(newMessages);
    setIsLoading(true);

    try {
      setTimeout(() => {
        setMessages([...newMessages, { 
          role: 'assistant', 
          content: 'Thanks for your message! Our team will get back to you soon.' 
        }]);
        setIsLoading(false);
      }, 1000);
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages([...newMessages, { 
        role: 'assistant', 
        content: 'Sorry, there was an error processing your request.' 
      }]);
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.container}>
      <Head>
        <title>HackHub 2025- 51-Hour Hackathon</title>
        <meta name="description" content="From Caffeine to Code—Let's Build Something Bold! Join HackHub 2025for a 51-hour marathon of innovation." />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className={styles.main}>
        <h1 className={styles.title}>HackHub 2025</h1>
        <p className={styles.subtitle}>From Caffeine to Code—Let's Build Something Bold!</p>
        
        <div className={styles.countdown}>
          <h2>Time Remaining</h2>
          <div className={styles.timer}>
            <span>{String(timeLeft.hours).padStart(2, '0')}</span>:
            <span>{String(timeLeft.minutes).padStart(2, '0')}</span>:
            <span>{String(timeLeft.seconds).padStart(2, '0')}</span>
          </div>
        </div>

        <div className={styles.tabs}>
          <button 
            className={`${styles.tab} ${activeTab === 'overview' ? styles.activeTab : ''}`}
            onClick={() => setActiveTab('overview')}
          >
            Overview
          </button>
          <button 
            className={`${styles.tab} ${activeTab === 'domains' ? styles.activeTab : ''}`}
            onClick={() => setActiveTab('domains')}
          >
            Domains
          </button>
          <button 
            className={`${styles.tab} ${activeTab === 'prizes' ? styles.activeTab : ''}`}
            onClick={() => setActiveTab('prizes')}
          >
            Prizes
          </button>
          <button 
            className={`${styles.tab} ${activeTab === 'judges' ? styles.activeTab : ''}`}
            onClick={() => setActiveTab('judges')}
          >
            Judges
          </button>
          <button 
            className={`${styles.tab} ${activeTab === 'chat' ? styles.activeTab : ''}`}
            onClick={() => setActiveTab('chat')}
          >
            Chat
          </button>
        </div>

        <div className={styles.content}>
          {activeTab === 'overview' && (
            <div className={styles.overview}>
              <div className={styles.eventInfo}>
                <div className={styles.infoCard}>
                  <h3>📅 Event Details</h3>
                  <p>June 21, 2025</p>
                  <p>51 Hours Duration</p>
                  <p>100% Online</p>
                </div>
                <div className={styles.infoCard}>
                  <h3>👥 Participation</h3>
                  <p>Ages 16+ only</p>
                  <p>Teams of 2-6 members</p>
                  <p>Global participation</p>
                </div>
              </div>
              
              <div className={styles.description}>
                <h2>Welcome to HackHub 2025</h2>
                <p>HackHub is a fully online, high-energy, 51-hour hackathon kicking off on June 21. This is our debut edition, and we're here to make it unforgettable. Whether you're a beginner exploring tech or a seasoned coder, HackHub invites you to build something meaningful and compete for exciting rewards.</p>
              </div>

              <div className={styles.benefits}>
                <h2>🎁 Why Join HackHub?</h2>
                <ul>
                  <li>🏆 Real Cash Prizes</li>
                  <li>📦 Swags for Top Teams</li>
                  <li>📜 Participation Certificates for All</li>
                  <li>💼 Internship Opportunities for Outstanding Talent</li>
                  <li>🌐 100% Online & Global – Join from Anywhere</li>
                </ul>
              </div>
            </div>
          )}

          {activeTab === 'domains' && (
            <div className={styles.domains}>
              <h2>🧩 Domains You Can Build In</h2>
              <div className={styles.domainGrid}>
                <div className={styles.domainCard}>
                  <h3>🏥 Healthcare & Wellness</h3>
                  <p>Innovative solutions for better health outcomes</p>
                </div>
                <div className={styles.domainCard}>
                  <h3>📚 Education & Skill Development</h3>
                  <p>Revolutionizing learning experiences</p>
                </div>
                <div className={styles.domainCard}>
                  <h3>🎨 Art, Culture & Entertainment</h3>
                  <p>Creative tech solutions for the arts</p>
                </div>
                <div className={styles.domainCard}>
                  <h3>🔒 Cybersecurity & Privacy</h3>
                  <p>Protecting digital assets and privacy</p>
                </div>
                <div className={styles.domainCard}>
                  <h3>🌱 Sustainable Development & Climate Tech</h3>
                  <p>Solutions for a better planet</p>
                </div>
                <div className={styles.domainCard}>
                  <h3>💰 FinTech & Digital Economy</h3>
                  <p>Innovative financial solutions</p>
                </div>
                <div className={styles.domainCard}>
                  <h3>🎯 Open Innovation (Wildcard)</h3>
                  <p>Think outside the box!</p>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'prizes' && (
            <div className={styles.prizes}>
              <h2>💰 Prize Pool</h2>
              <p className={styles.prizeInfo}>70% of the total participation fee goes directly into the prize pool—the more participants, the bigger the prizes!</p>
              
              <div className={styles.judgingCriteria}>
                <h3>Judging Criteria</h3>
                <div className={styles.criteriaGrid}>
                  <div className={styles.criteriaCard}>
                    <h4>Innovation</h4>
                    <p>Originality and creativity of the idea</p>
                  </div>
                  <div className={styles.criteriaCard}>
                    <h4>Technical Skill</h4>
                    <p>Complexity and execution of the project</p>
                  </div>
                  <div className={styles.criteriaCard}>
                    <h4>Impact</h4>
                    <p>Usefulness, relevance, and potential real-world impact</p>
                  </div>
                  <div className={styles.criteriaCard}>
                    <h4>Design & UX</h4>
                    <p>User interface, ease of use, and aesthetics</p>
                  </div>
                  <div className={styles.criteriaCard}>
                    <h4>Presentation</h4>
                    <p>Clarity of the demo video and documentation</p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'judges' && (
            <div className={styles.judges}>
              <h2>👨‍⚖️ Judges</h2>
              <div className={styles.judgesGrid}>
                <div className={styles.judgeCard}>
                  <h3>Punya Mittal</h3>
                  <p>Vellore Institute of Technology</p>
                </div>
                <div className={styles.judgeCard}>
                  <h3>Shreyas Kumar</h3>
                  <p>Vellore Institute of Technology</p>
                </div>
                <div className={styles.judgeCard}>
                  <h3>Ayush Upadhyay</h3>
                  <p>Vellore Institute of Technology</p>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'chat' && (
        <div className={styles.chatContainer}>
          <div className={styles.messages}>
            {messages.map((msg, index) => (
              <div key={index} className={`${styles.message} ${msg.role === 'user' ? styles.userMessage : styles.botMessage}`}>
                    <span className={styles.messageRole}>{msg.role === 'user' ? 'You' : 'HackHub Bot'}</span>
                <div className={styles.messageContent}>{msg.content}</div>
              </div>
            ))}
            {isLoading && (
              <div className={`${styles.message} ${styles.botMessage}`}>
                    <span className={styles.messageRole}>HackHub Bot</span>
                <div className={styles.messageContent}>
                  <div className={styles.loadingDots}>
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <form onSubmit={handleSubmit} className={styles.inputForm}>
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
                  placeholder="Ask questions about the hackathon..."
              className={styles.messageInput}
              disabled={isLoading}
            />
            <button 
              type="submit" 
              className={styles.sendButton}
                  disabled={isLoading || input.trim() === ''}
            >
              Send
            </button>
          </form>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}