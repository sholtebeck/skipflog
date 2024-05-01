import React from "react";
import { useState, useEffect } from 'react';
import PicksTable from './PicksTable';
import PointsTable from './PointsTable';
import Results from './Results';
import events from '../data/events.json';
import {getNames} from './helpers';

export const Home = () => {
    const [isLoading,setLoading] = useState(false);
//    const [events, setEvents] = useState(events);
    const [eventInfo, setEventInfo] = useState(events[0]);
    const eventNames=getNames(events)

    const handleEventChange = (e) => {
        setEventInfo(events[e.target.value]);
      };
    

  return <div className="container">
   
    <div className="row">
        <div className="col-6"> 
        <div className="strong">Event:
    <select className="select-option" onChange={(e) => {handleEventChange(e)}}>
    {eventNames.map(name => ( <option value={eventNames.indexOf(name)}>{name}</option> ))}
       </select>
       </div>
        <div className="strong">{eventInfo.name} - Picks</div>    
   <PicksTable pickers={eventInfo.pickers} /><p />
   <PointsTable pickers={eventInfo.pickers} /> 
       </div>
      <div className="col-6">
        <div className="strong">  {eventInfo.name} - Final Results <br/> {eventInfo.event_dates} at {eventInfo.event_loc} </div>
      <Results results={eventInfo.players} rtype="Player" /> 
      </div>
 </div>
 </div>
};
