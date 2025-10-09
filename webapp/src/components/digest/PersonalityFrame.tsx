import React, { useState, useEffect } from 'react';
import { cn } from '../../lib/utils';

interface PersonalityFrameProps {
  aiStyle: 'analytical' | 'business' | 'meme';
  isActive: boolean; // To control opacity based on modal activity
}

const colorMap = {
  analytical: "from-blue-400 via-indigo-400 to-cyan-400",
  business: "from-amber-400 via-orange-400 to-yellow-400",
  meme: "from-pink-400 via-fuchsia-400 to-rose-400",
};

const PersonalityFrame: React.FC<PersonalityFrameProps> = ({ aiStyle, isActive }) => {
  const [speed, setSpeed] = useState('3s');

  useEffect(() => {
    document.documentElement.style.setProperty("--speed", speed);
  }, [speed]);

  const handleMouseEnter = () => setSpeed('1.5s');
  const handleMouseLeave = () => setSpeed('3s');
  const handleBlur = () => setSpeed('4.5s');

  return (
    <div
      className={cn(
        "absolute top-0 left-0 right-0 h-[3px] rounded-t-3xl bg-[length:200%_100%] ",
        "bg-gradient-to-r animate-shimmer transition-all duration-300 ease-linear",
        colorMap[aiStyle],
        isActive ? "opacity-100" : "opacity-60"
      )}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      onFocus={handleMouseEnter} // Treat focus like mouse enter for keyboard users
      onBlur={handleBlur}
      tabIndex={0} // Make div focusable
    />
  );
};

export default PersonalityFrame;