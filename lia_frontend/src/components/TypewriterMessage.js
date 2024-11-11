import React, { useState, useEffect, useRef, memo } from 'react';

const TypewriterMessage = memo(({ role, message, isInterim }) => {
  console.log('🎭 TypewriterMessage: Rendering message', {
    role,
    messageLength: message?.length,
    isInterim
  });

  const [displayedMessage, setDisplayedMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const hasTyped = useRef(false);
  const timeoutIdRef = useRef(null);

  useEffect(() => {
    console.log('📝 TypewriterMessage: Message changed, resetting display', {
      newMessage: message,
      isInterim
    });
    if (!hasTyped.current) {
      let index = 0;
      setDisplayedMessage('');
      setIsTyping(true);

      const typingSpeed = Math.max(20, 1000 / message.length);

      const typeWriter = () => {
        if (index < message.length) {
          const nextChar = message.charAt(index);
          setDisplayedMessage((prev) => prev + nextChar);
          index++;
          timeoutIdRef.current = setTimeout(typeWriter, typingSpeed);
        } else {
          setIsTyping(false);
          hasTyped.current = true;
        }
      };

      typeWriter();

      return () => {
        if (timeoutIdRef.current) {
          clearTimeout(timeoutIdRef.current);
        }
      };
    }
  }, [message]);

  return (
    <div className={`chat-message ${role} ${isInterim ? 'interim' : ''}`}>
      <div className="message-header">
        {role === 'lia' ? '💃 LIA:' : '👤 User:'}
      </div>
      <div className={`message-content ${isTyping ? 'typewriter' : ''}`}>
        {displayedMessage}
        {isInterim && <span className="cursor">|</span>}
      </div>
    </div>
  );
});

export default TypewriterMessage;
