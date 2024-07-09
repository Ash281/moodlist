export const dataURItoBlob = (dataURI) => {
    console.log(dataURI);
    const byteString = atob(dataURI.split(",")[1]);
    const mimeString = dataURI.split(",")[0].split(":")[1].split(";")[0];
    const ab = new ArrayBuffer(byteString.length);
    const ia = new Uint8Array(ab);
  
    for (let i = 0; i < byteString.length; i++) {
      ia[i] = byteString.charCodeAt(i);
    }
  
    return new Blob([ab], { type: mimeString });
  }

export const imageToFile = (image) => {
    const blob = dataURItoBlob(image);
    const file = new File([blob], "uploaded_image.jpg", { type: "image/jpeg" });
    return file;
    };

export const getMoodText = (mood) => {
    switch (mood) {
        case "happy":
            return "Happy today? 😊 Here's a feel good playlist for you ❤️";
        case "sad":
            return "Sorry to hear you're feeling down 😢 Here's a sad songs playlist for you 💧";
        case "angry":
            return "Angry? 😡 Here's a playlist to help you calm down 🧘‍♂️";
        case "surprise":
            return "Surprised? 😲 Here's a high energy playlist for you 🎉";
        case "fear":
            return "Scared? 😱 Here's a playlist to help you feel safe 🏠";
        case "disgust":
            return "Disgusted? 🤢 Here's a playlist to help you feel better 🌸";
        default:
            return "No mood detected";
    }
}