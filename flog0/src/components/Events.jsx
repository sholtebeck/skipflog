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
        { accessor: 'winner_points', label: 'Winning Pts',fixed:2},
        { accessor: 'loser', label: 'Loser'},
        { accessor: 'loser_points', label: 'Losing Pts',fixed:2},
        { accessor: 'margin', label: 'Margin', fixed:2}
            ];	
	
  return <div> <p /> <Eventable rows={events} columns={columns} pageSize="12" /> 
    </div>
};
