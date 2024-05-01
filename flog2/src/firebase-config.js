// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";
import { doc, getDoc,getFirestore } from "firebase/firestore";

// Firebase configuration (from .env file)
const firebaseConfig = {
  apiKey: process.env.REACT_APP_FIREBASE_API_KEY,
  authDomain: process.env.REACT_APP_FIREBASE_AUTH_DOMAIN,
  projectId: process.env.REACT_APP_FIREBASE_PROJECT_ID,
  storageBucket: process.env.REACT_APP_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: process.env.REACT_APP_FIREBASE_MESSAGING_SENDER_ID,
  appId: process.env.REACT_APP_FIREBASE_APP_ID
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export default app;

// Get Event from Firestore db 
export const getEvent = async (id) => {
  const db=getFirestore(app)
  const docRef = doc(db, "events", id);
  const docSnap = await getDoc(docRef);
  return (docSnap.exists() ? docSnap.data() : {} );
};

// Get Results from Firestore db 
export const getResults = async (id) => {
  const db=getFirestore(app)
  const docRef = doc(db, "results", id);
  const docSnap = await getDoc(docRef);
  return (docSnap.exists() ? docSnap.data() : {} );
};
