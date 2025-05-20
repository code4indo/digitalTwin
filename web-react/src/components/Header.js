import React from 'react';
import { useCurrentTime } from '../hooks/useCurrentTime';

const Header = () => {
  const currentTime = useCurrentTime();
  
  return (
    <header>
      <div className="logo">
        <img src="/img/digital-twin-logo.svg" alt="Logo Digital Twin" />
        <h1>Digital Twin Gedung Arsip</h1>
      </div>
      <div className="header-right">
        <div className="current-time" id="current-time">{currentTime}</div>
        <div className="user-profile">
          <span>Admin</span>
          <img src="/img/user-avatar.png" alt="User Avatar" />
        </div>
      </div>
    </header>
  );
};

export default Header;
