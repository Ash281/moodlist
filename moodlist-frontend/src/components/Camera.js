import React, { useState, useRef, useEffect } from "react";
import { Camera } from "react-camera-pro";
import axios from "axios";
import { imageToFile } from "../utils";

const Photo = () => {
  const camera = useRef(null);
  const [image, setImage] = useState(null);
  const [photoTaken, setPhotoTaken] = useState(false);
  const [mood, setMood] = useState(null);

  const getMood = async () => {
    try {
      const response = await axios.get("http://127.0.0.1:8000/api/get_mood/");
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

      const response = await axios.post("http://127.0.0.1:8000/api/upload/", formData);
      console.log(response.data); // Log response data from backend
      getMood(); // Get mood from backend
      setPhotoTaken(true); // Set photoTaken state to true
    } catch (error) {
      console.error("Error taking photo or uploading:", error);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center h-full bg-black">
      {!photoTaken ? (
        <>
          <div className="w-full h-2/12">
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
          <p className="text-white-500 font-extrabold">You look {mood}, so here's a {mood} playlist for you!</p>
        </div>
      )}
    </div>
  );
};

export default Photo;
