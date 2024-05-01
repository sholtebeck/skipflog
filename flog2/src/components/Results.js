const Results = ({results, event_name}) => (
    <> 
     <h5>{event_name} - Final Results</h5>
  <table className="results-table">
  <thead>
    <tr className="heading">
        <th className="table-border">Pos</th>
        <th className="table-border">Player Name</th>	
        <th className="table-border">Scores</th>
        <th className="table-border">Total</th>	
        <th className="table-border">Points</th>	
        <th className="table-border">Picked-By</th>
  </tr>
  </thead>
 <tbody>
 {results.map(result => (
          <tr key={result.name}>
             <td className="table-data">{result.pos}</td>
             <td className="table-data-left">{result.name}</td>
             <td className="table-data">{result.scores}</td>
             <td className="table-data">{result.total}</td>
             <td className="table-data">{ Math.floor(result.points) }</td>
             <td className="table-data">{result.picker}</td>
           </tr>
  ))}
  </tbody>
</table>
</>
);

export default Results;