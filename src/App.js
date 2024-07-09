import React from 'react';
import Photo from './components/Camera';
import logo from './logo.svg';
import axios from 'axios';
import { useState, useEffect } from 'react';

function App() {

  const [mood, setMood] = useState(null);
  const getMood = async () => {
    try {
      const response = await axios.get("http://127.0.0.1:8000/api/get_mood/");
      console.log(response.data);
      setMood(response.data.mood);
    } catch (error) {
      console.error("Error getting mood:", error);
    }
  };

  const resetMood = async () => {
    try {
      const response = await axios.get("http://127.0.0.1:8000/api/reset_mood/");
      console.log(response.data);
      setMood(null);
    } catch (error) {
      console.error("Error resetting mood:", error);
    }
  }

  useEffect(() => {
    getMood();

    return () => {
      resetMood();
    }
  }, []);

  return (
    <div className="bg-black h-screen flex flex-col justify-start items-center">
      <div className="p-8 text-center">
        <h1 className="mb-4 text-3xl font-extrabold text-gray-900 dark:text-white md:text-5xl lg:text-6xl">
          <span className="text-transparent bg-clip-text bg-gradient-to-r to-purple-600 from-sky-400">MoodList</span> 
        </h1>
        <h2 className="text-lg font-extrabold mb-2 text-white">Make a Spotify playlist based on your mood</h2>
        {mood === 'No mood detected' ? (
        <p className="text-lg font-normal text-gray-500 lg:text-xl dark:text-gray-400">Here's a playlist for you</p>
        ) : (
        <p className="text-lg font-normal text-gray-500 lg:text-xl dark:text-gray-400">Take a photo so we can analyse how you feel</p>
        )}
      </div>
     
      <div className="flex-grow flex items-center justify-center">
        <Photo />
      </div>
    </div>
  );
}

export default App;
