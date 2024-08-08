import React from 'react';

const SpotifyLogin = () => {
    // const loginURL = 'http://127.0.0.1:8000/api/login/';
    const loginURL = 'https://moodlist-production.up.railway.app/api/login/';
  return (
    <div>
      <a href={loginURL}>
        <button className='bg-green-500 text-white font-extrabold'>Connect to Spotify</button>
      </a>
    </div>
  );
};

export default SpotifyLogin;