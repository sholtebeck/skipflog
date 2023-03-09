import { Routes, Route } from "react-router-dom";
import { UserAuthContextProvider } from "./context/userAuthContext";
import "./App.css";
import Home from "./components/Home";
import HomePage from "./components/HomePage";
import Login from "./components/Login";
import Signup from "./components/Signup";

function App() {
  return (
          <UserAuthContextProvider>
            <Routes>
              <Route key="0" path="/" element={<HomePage />} />
              <Route key="1" path="/home" element={<Home />} />
              <Route key="2" path="/login" element={<Login />} />
              <Route key="3" path="/signup" element={<Signup />} />
            </Routes>
          </UserAuthContextProvider>

  );
}

export default App;
