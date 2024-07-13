import React, { useState, useRef, useEffect } from "react";
import { Camera } from "react-camera-pro";
import axios from "axios";
import { imageToFile, getMoodText, fetchTopTracks } from "../utils";

const Photo = () => {
  const camera = useRef(null);
  const [image, setImage] = useState(null);
  const [photoTaken, setPhotoTaken] = useState(false);
  const [mood, setMood] = useState(null);
  const [loading, setLoading] = useState(false);
  const [topTracks, setTopTracks] = useState([]);

  const getMood = async () => {
    try {
      // const response = await axios.get("https://moodlist.onrender.com/api/get_mood/");
      const response = await axios.get("http://127.0.0.1:8000/api/get_mood/");
      setMood(response.data.mood);
    }
    catch (error) {
      console.error("Error getting mood:", error);
    }
  };

  const resetMood = async () => {
    try {
      // const response = await axios.get("https://moodlist.onrender.com/api/reset_mood/");
      const response = await axios.post("http://127.0.0.1:8000/api/reset_mood/");
      setMood(null);
      setPhotoTaken(false);
      setImage(null);
    }
    catch (error) {
      console.error("Error resetting mood:", error);
    }
  }

  const handleTakePhoto = async () => {
    try {
      setLoading(true);
      const photo = await camera.current.takePhoto(); // Wait for photo to be taken
      setImage(photo); // Update image state with the captured photo

      const file = imageToFile(photo); // Convert image to file
      const formData = new FormData();
      formData.append("file", file); // Append file to FormData

      await new Promise((resolve) => setTimeout(resolve, 1000)); // Wait for 1 second

      // const response = await axios.post("https://moodlist.onrender.com/api/upload/", formData);
      const response = await axios.post("http://127.0.0.1:8000/api/upload/", formData);
      getMood(); // Get mood from backend
      setPhotoTaken(true); // Set photoTaken state to true
    } catch (error) {
      console.error("Error taking photo or uploading:", error);
    }
    finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-black">
       {mood !== 'No mood detected.' ? (
        <p className="text-center text-lg font-normal text-gray-500 lg:text-xl dark:text-gray-400">Here's a playlist for you</p>
        ) : (
        <p className="text-center text-lg font-normal text-gray-500 lg:text-xl dark:text-gray-400">Take a photo so we can analyse how you feel</p>
        )}
      {loading ? (
        <div class="relative h-screen">
        <div class="absolute top-1/4 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
          <div class="w-32 h-32 aspect-square rounded-full flex justify-center items-center animate-spin bg-gradient-to-br from-blue-500 to-purple-500">
            <span class="w-28 h-28 aspect-square rounded-full animate-spin bg-gradient-to-br from-blue-600 to-purple-600"></span>
          </div>
        </div>
      </div>
      
      ) : (
        <>
          {!photoTaken ? (
            <div className="w-full h-2/12 items-center justify-center">
              <div className="relative w-full h-full">
                <Camera ref={camera} aspectRatio={9 / 16} className="absolute inset-0 w-full h-full" />
              </div>
            </div>
          ) : null}

          {!photoTaken ? (
            <button
              onClick={() => handleTakePhoto()}
              className="mt-4 px-4 py-2 bg-blue-500 text-white rounded-md shadow hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50"
            >
              Take photo
            </button>
          ) : null}

          {photoTaken && !loading ? (
            <div className="mt-4 text-white items-center justify-center text-center">
              {getMoodText(mood) !== "No mood detected" ? (
                <>
                 
                  <p className="text-white-500 font-extrabold">{getMoodText(mood)}</p>
                  <button
                  onClick={() => resetMood()}
                  className="justify-center mt-4 px-4 py-2 bg-blue-500 text-white rounded-md shadow hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50"
                  >
                  Take another photo
                  </button>
                </>
              ) : (
                <p className="text-white-500 font-extrabold">{getMoodText(mood)}</p>
              )}
            </div>
          ) : null}
        </>
      )}
    </div>
  );
};

export default Photo;
