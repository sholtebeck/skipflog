import React from "react";

export const Results = ({results, rtype}) => (
  <table className="event-table">
  <thead>
    <tr><th className="table-header">Pos</th>
        <th className="table-header">{rtype} Name</th>	
        <th className="table-header">Scores</th>
        <th className="table-header">Total</th>	
        <th className="table-header">Points</th>	
        <th className="table-header">Picked-By</th>
  </tr>
  </thead>
 <tbody>
 {results.map(result => (
          <tr key={result.name}>
             <td className="table-data">{result.pos}</td>
             <td className="table-data-left">{result.name}</td>
             <td className="table-data-left">{result.scores}</td>
             <td className="table-data">{result.total}</td>
             <td className="table-data">{result.points.toFixed(2)}</td>
             <td className="table-data">{result.picker}</td>
           </tr>
  ))}
  </tbody>
</table>
);

export default Results;