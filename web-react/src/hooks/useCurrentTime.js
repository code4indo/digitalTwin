import { useState, useEffect } from 'react';

// Custom hook untuk menampilkan waktu saat ini
export const useCurrentTime = (locale = 'id-ID') => {
  const [currentTime, setCurrentTime] = useState('');
  
  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      const options = { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric',
        hour: '2-digit', 
        minute: '2-digit',
        second: '2-digit'
      };
      
      setCurrentTime(now.toLocaleDateString(locale, options));
    };
    
    // Update waktu saat pertama kali komponen dimuat
    updateTime();
    
    // Set interval untuk memperbarui waktu setiap detik
    const interval = setInterval(updateTime, 1000);
    
    // Bersihkan interval saat komponen dilepas (unmounted)
    return () => clearInterval(interval);
  }, [locale]);
  
  return currentTime;
};
