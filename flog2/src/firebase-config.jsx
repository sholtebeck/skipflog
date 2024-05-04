// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAuth, GoogleAuthProvider, signInWithPopup, signOut, onAuthStateChanged } from "firebase/auth";
import { doc, getDoc,getFirestore } from "firebase/firestore";
import firebaseConfig from './assets/firebase.json';

// Firebase configuration (from .env file)
//const firebaseConfig = {
//    apiKey: import.meta.env.VITE_FIREBASE_APIKEY,
//    authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
//    projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
//    storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
//    messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGE_SENDER_ID,
//    appId: import.meta.env.VITE_FIREBASE_APP_ID,
//    measurementId: import.meta.env.VITE_FIREBASE_MEASUREMENT_ID,
//};

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
