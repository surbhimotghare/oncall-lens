'use client';

import { useState, useEffect } from 'react';
import { Moon, Sun } from 'lucide-react';

export default function ThemeToggle() {
  const [isDark, setIsDark] = useState(false);

  useEffect(() => {
    // Check for saved theme preference or default to light
    const savedTheme = localStorage.getItem('oncall-lens-theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
      setIsDark(true);
      document.documentElement.classList.add('dark');
    } else {
      setIsDark(false);
      document.documentElement.classList.remove('dark');
    }
  }, []);

  const toggleTheme = () => {
    console.log('🌙 Theme toggle clicked, current isDark:', isDark);
    
    if (isDark) {
      console.log('🌞 Switching to light mode');
      setIsDark(false);
      document.documentElement.classList.remove('dark');
      localStorage.setItem('oncall-lens-theme', 'light');
    } else {
      console.log('🌙 Switching to dark mode');
      setIsDark(true);
      document.documentElement.classList.add('dark');
      localStorage.setItem('oncall-lens-theme', 'dark');
    }
    
    console.log('📄 Document classes after toggle:', document.documentElement.classList.toString());
  };

  return (
    <div className="flex items-center space-x-2">
      <button
        onClick={toggleTheme}
        className={`
          p-2 rounded-xl transition-all duration-200 
          ${isDark 
            ? 'bg-gray-800 text-yellow-400 hover:bg-gray-700' 
            : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
          }
        `}
        title={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
      >
        {isDark ? (
          <Sun className="w-5 h-5" />
        ) : (
          <Moon className="w-5 h-5" />
        )}
      </button>
      {/* Debug indicator */}
      <div className="text-xs text-gray-500 dark:text-gray-400">
        {isDark ? 'Dark' : 'Light'}
      </div>
    </div>
  );
}
