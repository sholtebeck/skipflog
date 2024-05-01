import { Route, Routes } from "react-router-dom";
import "./App.css";
import { Navbar } from "./components/Navbar";
import { Home } from "./components/Home";
import { Events } from "./components/Events";
import { Players } from "./components/Players";

function App() {
  return (
    <div className="App">
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/events" element={<Events />} />
        <Route path="/players" element={<Players />} />
        <Route path="/results" element={<Home />} />
      </Routes>
    </div>
  );
}

export default App;
