import { useState, useEffect } from 'react';
import axios from 'axios';
import { useUserAuth } from "../context/userAuthContext";
import NavBar from './NavBar';
import PicksTable from './PicksTable';
import { Datatable } from './Datatable';
import Button from "react-bootstrap/Button";
import { getEvent } from '../firebase-config';
import PointsTable from './PointsTable';
import Results from './Results';

const currentEventID = () => {
    let today=new Date();
    const months=["04","04","04","04","05","06","07","07","07","07"];
    return (today.getYear()-100).toString()+months[today.getMonth()];
}


const HomePage = () => {
    const [isLoading,setLoading] = useState(false);
    const [eventInfo, setEventInfo] = useState({});
    const [availablePlayers, setAvailablePlayers] = useState([]);
    const [selectedPlayers, setSelectedPlayers] = useState([]);
    const [player, setPlayer] = useState("");
    const eventId=currentEventID();
    const { logOut, user } = useUserAuth();

    const userName = () => {         
        return user && user.displayName ? user.displayName.split(" ")[0] : ""; 
    }

    const canPick = () => {
        return eventInfo.players && userName() === eventInfo.next; 
    }

    const complete = () => {
        return eventInfo.status === "Final";
    }
    const nextPick = () => {
        if (eventInfo.pick_no>22) {
            return ""
        } else if (eventInfo.next !== userName()) {
            return "Waiting For "+ eventInfo.nextpick
        } else {
            return eventInfo.nextpick
        }
    }

    const columns = [
        { accessor: 'rank', label: 'Rank' },
        { accessor: 'name', label: 'Name' },
        { accessor: 'country', label: 'Country' },
        { accessor: 'odds', label: 'Odds' },
        { accessor: 'points', label: 'Points' }
       ];

    useEffect(() => {
        const loadEventInfo = async () => {
            setLoading(true);
            const newEvent=await getEvent(eventId);
//        const response = await axios.get(`/api/event/${eventId}`);
//        const newEvent = response.data;
            setEventInfo(newEvent);
            setAvailablePlayers(newEvent.players.filter(function (player) { return player.picked === 0; }));
            setSelectedPlayers(newEvent.players.filter(function (player) { return player.picker && player.points > 0; }));
            setPlayer(availablePlayers[0]);
        }

        if (!isLoading) {
            loadEventInfo();
        }
    }, [isLoading, eventId,  availablePlayers]);

//   if (!eventInfo) {        return <NotFoundPage />    }

    const handlePick = async () => {

            const response = await axios.put(`/api/pick/${eventInfo.ID}`, {
                picker: userName(),
                player: player
            });
            const newEvent = response.data.event;
            setEventInfo(newEvent);
            setAvailablePlayers(availablePlayers.filter(function (p) { return p.name !== player; }));
            setLoading(false);
      }

    return (
        <>
        {eventInfo && <NavBar eventInfo={eventInfo} userName={userName()} logOut={() => logOut()} /> }
        <div className="container mt-3">
        <div className="row align-items-start">
        <div className="col">     
        {eventInfo.lastpick && <h5><b>Last Pick:</b> {eventInfo.lastpick} </h5>}
        {eventInfo.pickers && <PicksTable pickers={eventInfo.pickers} />  }

        {canPick() ? <h5 className="pick-table">{eventInfo.nextpick}: 
         <select className="select-option" name="player"  value={player}  onChange={(event) => {setPlayer(event.target.value)}}>
            <option>Select a Player</option>
    {availablePlayers.map(player => (
       <option >{player.name}</option>  ))}
     </select><Button variant="dark" onClick={() => handlePick()}>Pick</Button></h5>  
     : <h5>{nextPick()}</h5>}
     
     </div>
      <div className="col">
      {canPick() && <Datatable rows={availablePlayers} columns={columns} pageSize="10" canPick={canPick()} handlePick={(player) => handlePick(player)} setPlayer={setPlayer} /> }
      {complete() && <Results results={selectedPlayers} event_name={eventInfo.name} /> } <p/>
      {complete() && <PointsTable pickers={eventInfo.pickers} /> }
      </div>
    </div>
    </div>
     </>
    );
}

export default HomePage;