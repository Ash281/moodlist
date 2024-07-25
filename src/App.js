import React from 'react';
import Photo from './components/Camera';
import logo from './logo.svg';
import axios from 'axios';
import { useState, useEffect } from 'react';
import SpotifyLogin from './components/SpotifyLogin';

function App() {

  const [mood, setMood] = useState(null);
  const [token, setToken] = useState(false);
  const [session, setSession] = useState(null);
  const [topTracks, setTopTracks] = useState([]);
  
  useEffect(() => {
    const isAuthenticated = async () => {
      try {
        const response = await axios.get("https://moodlist.onrender.com/api/is_authenticated/",
        // const response = await axios.get("http://127.0.0.1:8000/api/is_authenticated/",
          { withCredentials: true }
        );
        console.log(response.data.is_authenticated);
        setToken(response.data.is_authenticated);
        setSession(response.data.session_key);
      }
      catch (error) {
        console.error("Error checking authentication:", error);
      }
    }
    isAuthenticated();
  }, []);

  const getMood = async () => {
    try {
      const response = await axios.get("https://moodlist.onrender.com/api/get_mood/");
      // const response = await axios.get("http://127.0.0.1:8000/api/get_mood/");
      setMood(response.data.mood);
    } catch (error) {
      console.error("Error getting mood:", error);
    }
  };

  const resetMood = async () => {
    try {
      const response = await axios.get("https://moodlist.onrender.com/api/reset_mood/");
      // const response = await axios.post("http://127.0.0.1:8000/api/reset_mood/");
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

      </div>

      <div className="flex-grow flex items-center justify-center">
        {token ? 
         <div className="flex flex-col items-center justify-center">
            <Photo/>         
       
       </div>
       : <SpotifyLogin/>}
      </div>
    </div>
  );
}

export default App;
