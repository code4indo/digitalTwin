import React from 'react';

const Footer = () => {
  const currentYear = new Date().getFullYear();
  
  return (
    <footer>
      <div className="copyright">
        &copy; {currentYear} Digital Twin - Sistem Cerdas Manajemen Iklim Mikro Gedung Arsip
      </div>
      <div className="version">
        Versi 1.2.0
      </div>
    </footer>
  );
};

export default Footer;
