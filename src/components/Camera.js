import React, { useState, useRef, useEffect } from "react";
import { Camera } from "react-camera-pro";
import axios from "axios";
import { imageToFile, getMoodText } from "../utils";

const Photo = () => {
  const camera = useRef(null);
  const [image, setImage] = useState(null);
  const [photoTaken, setPhotoTaken] = useState(false);
  const [mood, setMood] = useState(null);

  const getMood = async () => {
    try {
      const response = await axios.get("https://moodlist.onrender.com/api/get_mood/");
      console.log(response.data);
      setMood(response.data.mood);
    }
    catch (error) {
      console.error("Error getting mood:", error);
    }
  };

  const handleTakePhoto = async () => {
    try {
      const photo = await camera.current.takePhoto(); // Wait for photo to be taken
      setImage(photo); // Update image state with the captured photo

      const file = imageToFile(photo); // Convert image to file
      const formData = new FormData();
      formData.append("file", file); // Append file to FormData

      const response = await axios.post("https://moodlist.onrender.com/api/upload/", formData);
      console.log(response.data); // Log response data from backend
      getMood(); // Get mood from backend
      setPhotoTaken(true); // Set photoTaken state to true
    } catch (error) {
      console.error("Error taking photo or uploading:", error);
    }
  };

  return (
    <div className="flex flex-col h-full bg-black">
      {!photoTaken ? (
        <>
          <div className="w-full h-2/12 items-center justify-center">
            <div className="relative w-full h-full">
              <Camera ref={camera} aspectRatio={9 / 16} className="absolute inset-0 w-full h-full" />
            </div>
          </div>
          <button
            onClick={() => handleTakePhoto()}
            className="mt-4 px-4 py-2 bg-blue-500 text-white rounded-md shadow hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50"
          >
            Take photo
          </button>
          {image === null ? null : (
            <div className="mt-4">
              <img src={image} alt="Taken photo" className="max-w-full h-auto" />
            </div>
          )}
        </>
      ) : (
        <div className="mt-4 text-white">
          <iframe 
          style={{borderRadius: '12px' }} 
          src="https://open.spotify.com/embed/playlist/3NID2u1NyZZTFKjJrDwIy4?utm_source=generator" 
          width="100%" height="352" frameBorder="0" 
          allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" 
          loading="lazy"></iframe>
          <p className="text-white-500 font-extrabold">{getMoodText(mood)}</p>
        </div>
      )}
    </div>
  );
};

export default Photo;
