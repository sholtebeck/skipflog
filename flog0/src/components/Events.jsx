import React from "react";
import { Eventable } from './Eventable';
import events from '../data/events.json';

export const Events = () => {
	
    const columns = [
        { accessor: 'ID', label: 'ID' },
        { accessor: 'name', label: 'Event' },
        { accessor: 'event_dates', label: 'Dates' },
        { accessor: 'event_loc', label: 'Location' },
        { accessor: 'winner', label: 'Winner'},
        { accessor: 'winner_points', label: 'Winning Pts'},
        { accessor: 'loser', label: 'Loser'},
        { accessor: 'loser_points', label: 'Losing Pts'},
        { accessor: 'margin', label: 'Margin'}
            ];	
	
  return <div> <p /> <Eventable rows={events} columns={columns} pageSize="12" /> 
    </div>
};
