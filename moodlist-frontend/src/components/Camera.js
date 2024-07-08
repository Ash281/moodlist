import React, { useState, useRef } from "react";
import { Camera } from "react-camera-pro";

const Photo = () => {
  const camera = useRef(null);
  const [image, setImage] = useState(null);

  return (
    <div className="flex flex-col items-center justify-center h-screen bg-gray-500">
      <div className="w-400 h-225">
        <div className="relative w-full h-full">
          <Camera ref={camera} aspectRatio={400 / 225} className="absolute inset-0 w-full h-full" />
        </div>
      </div>
      <button
        onClick={() => setImage(camera.current.takePhoto())}
        className="mt-4 px-4 py-2 bg-blue-500 text-white rounded-md shadow hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50"
      >
        Take photo
      </button>
      {image === null ? null : (
        <div className="mt-4">
          <img src={image} alt="Taken photo" className="max-w-full h-auto" />
        </div>
      )}
    </div>
  );
};

export default Photo;
