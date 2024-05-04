//import { Link, useNavigate } from 'react-router-dom';
import { useState } from 'react';
import { useUserAuth } from "../context/userAuthContext";
import Button from "react-bootstrap/Button";
import GoogleButton from "react-google-button";


const NavBar = ({eventInfo, userName}) => {
    const { user,  googleSignIn, logOut } = useUserAuth();
    const [error, setError] = useState('');

    const handleGoogleSignIn = async (e) => {
        e.preventDefault();
        try {
          await googleSignIn();
        } catch (err) {
          setError(err);
        }
      };

      const handleLogout = async () => {
        try {
          await logOut();
        } catch (err) {
          setError(err);
        }
      };

const LogButton = () => {
        return user ? <label><Button variant="primary" onClick={handleLogout}>Sign Out</Button> Logged in as <b>{userName}</b></label>
            : <GoogleButton className="g-btn" type="dark" onClick={handleGoogleSignIn} />
    }

    return (
        <nav className="navbar navbar-light bg-light">
        <div className="container-fluid">
        <LogButton />
        {error && <label>{error}</label>}
        {eventInfo && <>
          <label><b>Event:</b>{eventInfo.Name} </label>
          <label><b>Dates:</b> {eventInfo.event_dates} </label>
          <label><b>Location:</b>{eventInfo.event_loc} </label>
          </>
         }
        </div>
      </nav>
    );
}

export default NavBar;