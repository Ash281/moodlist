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
  const [playlist, setPlaylist] = useState([]);
  const [token, setToken] = useState(false);
  const [session, setSession] = useState(null);

  useEffect(() => {
    const isAuthenticated = async () => {
      try {
        // const response = await axios.get("https://moodlist.onrender.com/api/is_authenticated/");
        // const response = await axios.get("http://127.0.0.1:8000/api/is_authenticated/",
        //  { withCredentials: true }
        // );
        const response = await axios.get("https://moodlist.onrender.com/api/is_authenticated/", {
          withCredentials: true
        });
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

  useEffect(() => {
    const fetchTopTracks = async () => {
      try {
        // const response = await axios.get(`http://127.0.0.1:8000/api/top_tracks/?mood=${mood}`, {
        //  withCredentials: true
        // });
        const response = await axios.get(`https://moodlist.onrender.com/api/top_tracks/?mood=${mood}`, {
          withCredentials: true
        });
        console.log("playlist", response.data.playlist_id);
        setPlaylist(response.data.playlist_id);
      } catch (error) {
        console.error("Error fetching top tracks:", error);
      }
    };
  
    if (mood) {
      fetchTopTracks();
    }
  }, [mood]);
    
  const getMood = async () => {
    try {
      const response = await axios.get("https://moodlist.onrender.com/api/get_mood/");
      // const response = await axios.get("http://127.0.0.1:8000/api/get_mood/");
      setMood(response.data.mood);
    }
    catch (error) {
      console.error("Error getting mood:", error);
    }
  };

  const resetMood = async () => {
    try {
      const response = await axios.get("https://moodlist.onrender.com/api/reset_mood/");
      // const response = await axios.post("http://127.0.0.1:8000/api/reset_mood/");
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

      const response = await axios.post("https://moodlist.onrender.com/api/upload/", formData);
      // const response = await axios.post("http://127.0.0.1:8000/api/upload/", formData);
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
    <div className="flex flex-col bg-black">
  {mood === null ? (
    <p className="text-center text-lg font-normal text-gray-500 lg:text-xl dark:text-gray-400">Take a photo of yourself</p>
  ) : (
    <p className="text-center text-lg font-normal text-gray-500 lg:text-xl dark:text-gray-400">Here's a playlist for you</p>
  )}

  {loading ? (
    <div className="relative">
      <div className="absolute inset-0 flex items-center justify-center">
        <div className="w-32 h-32 aspect-square rounded-full flex justify-center items-center animate-spin bg-gradient-to-br from-blue-500 to-purple-500">
          <span className="w-28 h-28 aspect-square rounded-full animate-spin bg-gradient-to-br from-blue-600 to-purple-600"></span>
        </div>
      </div>
    </div>
  ) : (
    <>
      {!photoTaken ? (
        <div className="flex-grow flex items-center justify-center">
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
        <div className="mt-4 flex flex-col items-center justify-center text-white">
          {getMoodText(mood) !== "No mood detected" ? (
            <>
              <div className="flex flex-col items-center justify-center">
                <iframe
                  title="Spotify Playlist"
                  src={`https://open.spotify.com/embed/playlist/${playlist}`}
                  width="300"
                  height="380"
                  frameBorder="0"
                  allowtransparency="true"
                  allow="encrypted-media"
                ></iframe>
              </div>
              <p className="text-white font-extrabold">{getMoodText(mood)}</p>
              <button
                onClick={() => resetMood()}
                className="mt-4 px-4 py-2 bg-blue-500 text-white rounded-md shadow hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50"
              >
                Take another photo
              </button>
            </>
          ) : (
            <p className="text-white font-extrabold">{getMoodText(mood)}</p>
          )}
        </div>
      ) : null}
    </>
  )}
</div>

  );
};

export default Photo;
