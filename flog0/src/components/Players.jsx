import React from "react";
import { useState, useEffect } from 'react';
import { Datatable } from './Datatable';
import PointsTable from './PointsTable';
import Results from './Results';
import { getNames, playerResults } from './helpers';
import events from '../data/events.json';
import players from '../data/players.json';

export const Players = () => {
  const [player, setPlayer] = useState({});
  const [playEvents, setPlayEvents] = useState([]);
  const playerNames = getNames(players)

  const handlePlayer = (p) => {
    if (p.target.value) {
      let newPlayer=players.filter(q => q.name == p.target.value)[0]
      setPlayer(newPlayer)
      setPlayEvents(playerResults(events,newPlayer.name));
    } else {
      setPlayer({})
      setPlayEvents([])
    }
  };

  const columns = [
    { accessor: 'pos', label: 'Pos' },
    { accessor: 'name', label: 'Name' },
    { accessor: 'mark', label: 'Mark' },
    { accessor: 'steve', label: 'Steve' },
    { accessor: 'total', label: 'Total'},
    { accessor: 'first', label: 'First'},
    { accessor: 'last', label: 'Last'},
    { accessor: 'points', label: 'Points'}
        ];	

  return <div className="container">
 <div className="row">
        <div className="col-6"> 
       <p />
       <Datatable rows={players} columns={columns} pageSize="12" headerName="Players:" />
       <p/>
       {player.pickers && <PointsTable pickers={player.pickers} /> }
    </div>
    <div className="col-6">
    <div className="strong">Player:  <select className="select-option" onChange={(p) => {handlePlayer(p)}}>
      <option value=""></option>
      {playerNames.map(name => ( <option value={name}>{name}</option> ))}
       </select>
       <p/>
       </div>
       {player.name && <Results results={playEvents} rtype="Event" /> } 
       </div>
    </div>
  </div>
};
