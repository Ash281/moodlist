import React from 'react';
import Photo from './components/Camera';
import logo from './logo.svg';

function App() {
  return (
    <div className="bg-gray-500 h-screen flex flex-col justify-start items-center">
      <div className="p-8 text-center">
        <h1 className="mb-4 text-3xl font-extrabold text-gray-900 dark:text-white md:text-5xl lg:text-6xl">
          <span className="text-transparent bg-clip-text bg-gradient-to-r to-purple-600 from-sky-400">MoodList</span> 
        </h1>
        <h2 className="text-lg mb-2">Make a Spotify playlist based on your mood</h2>
        <p className="text-lg font-normal text-gray-500 lg:text-xl dark:text-gray-400">Placeholder text</p>
      </div>

      <div className="flex-grow flex items-center justify-center">
        <Photo />
      </div>
    </div>
  );
}

export default App;
